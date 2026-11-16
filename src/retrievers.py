"""Retrieval methods for Day 7. Every method returns Day 7 chunks with score, rank and method.

M1 dense  : Day 6 pgvector index (src/day6_store.py)
M2 bm25   : lexical BM25 over data/day7/chunks.json (the same chunks as the dense index)
M3 hybrid : Reciprocal Rank Fusion of dense + bm25 (rank-based, no raw-score mixing)

Filters (e.g. {"chapter_id": "ch14"}) are equality checks on chunk metadata and must come from
the user/question input, never from gold labels.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Protocol

from . import config

# Word tokens only (like the starter TF-IDF). Symbols such as "//" or "%" are dropped.
WORD_RE = re.compile(r"\w+")
# Code-aware: also keep runs of operator symbols ("//", "%", "==", "**", "+=") as tokens.
CODE_RE = re.compile(r"\w+|[^\w\s]{1,3}")
PUNCT_ONLY = set(".,;:!?\"'()[]{}“”‘’—–-•…")


class Retriever(Protocol):
    method: str

    def search(self, query: str, *, top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]: ...


def tokenize(text: str, mode: str = "word") -> list[str]:
    text = unicodedata.normalize("NFC", text).casefold()
    if mode == "word":
        return WORD_RE.findall(text)
    if mode == "code":
        return [t for t in CODE_RE.findall(text) if t not in PUNCT_ONLY]
    raise ValueError(f"unknown tokenizer mode {mode}")


def matches(chunk: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    return all(chunk["metadata"].get(k) == v for k, v in (filters or {}).items())


def load_chunks(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or config.DATA_DIR / "chunks.json"
    return json.loads(path.read_text(encoding="utf-8"))


class BM25Retriever:
    """BM25Okapi (rank-bm25) on chunk text; k1/b are the library defaults unless given."""

    def __init__(self, chunks: list[dict[str, Any]], *, tokenizer: str = "word",
                 k1: float = 1.5, b: float = 0.75) -> None:
        from rank_bm25 import BM25Okapi

        if not chunks:
            raise ValueError("BM25 needs at least one chunk")
        self.method = "bm25" if tokenizer == "word" else f"bm25_{tokenizer}"
        self.chunks, self.tokenizer, self.k1, self.b = chunks, tokenizer, k1, b
        self.bm25 = BM25Okapi([tokenize(c["text"], tokenizer) for c in chunks], k1=k1, b=b)

    def search(self, query: str, *, top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if not query.strip() or top_k < 1:
            raise ValueError("query must be non-empty and top_k >= 1")
        tokens = tokenize(query, self.tokenizer)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        ranked = sorted((i for i, c in enumerate(self.chunks) if matches(c, filters) and scores[i] > 0),
                        key=lambda i: (-scores[i], self.chunks[i]["id"]))[:top_k]
        return [{**self.chunks[i], "score": float(scores[i]), "rank": r, "method": self.method}
                for r, i in enumerate(ranked, 1)]

    def info(self) -> dict[str, Any]:
        return {"method": self.method, "tokenizer": self.tokenizer, "k1": self.k1, "b": self.b,
                "chunks": len(self.chunks)}


def rrf_fuse(rankings: list[list[dict[str, Any]]], *, k: int = 60, top_k: int = 3,
             method: str = "hybrid") -> list[dict[str, Any]]:
    """Reciprocal Rank Fusion: score = sum 1/(k + rank). Ties broken by chunk id."""
    fused: dict[str, float] = {}
    first: dict[str, dict[str, Any]] = {}
    sources: dict[str, dict[str, int]] = {}
    for ranking in rankings:
        for r, chunk in enumerate(ranking, 1):
            cid = chunk["id"]
            fused[cid] = fused.get(cid, 0.0) + 1.0 / (k + r)
            first.setdefault(cid, chunk)
            sources.setdefault(cid, {})[chunk.get("method", "?")] = r
    order = sorted(fused, key=lambda cid: (-fused[cid], cid))[:top_k]
    out = []
    for r, cid in enumerate(order, 1):
        base = {key: v for key, v in first[cid].items() if key not in ("score", "rank", "method")}
        out.append({**base, "score": fused[cid], "rank": r, "method": method,
                    "component_ranks": sources[cid]})
    return out


class HybridRetriever:
    """M3: take `candidates` from each retriever, fuse with RRF (k=60), return top_k."""

    def __init__(self, retrievers: list[Retriever], *, candidates: int = 20, k: int = 60,
                 method: str = "hybrid") -> None:
        if len(retrievers) < 2:
            raise ValueError("hybrid needs at least two retrievers")
        self.retrievers, self.candidates, self.k, self.method = retrievers, candidates, k, method

    def search(self, query: str, *, top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        n = max(self.candidates, top_k)
        rankings = [r.search(query, top_k=n, filters=filters) for r in self.retrievers]
        return rrf_fuse(rankings, k=self.k, top_k=top_k, method=self.method)

    def info(self) -> dict[str, Any]:
        return {"method": self.method, "fusion": "RRF", "k": self.k, "candidates_per_retriever": self.candidates,
                "components": [r.method for r in self.retrievers]}
