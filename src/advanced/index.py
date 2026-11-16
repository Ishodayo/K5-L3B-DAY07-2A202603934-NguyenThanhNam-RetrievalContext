"""Separate pgvector table `adv_chunks` (same Postgres as Day 6; the Day 6 `chunks` table is not touched)
plus dense / BM25 / hybrid retrievers for the advanced corpus."""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any

import psycopg

from .. import config
from .ingest import CHUNKS_OUT

TABLE = "adv_chunks"


def _vec(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.7f}" for x in v) + "]"


def load_chunks() -> list[dict[str, Any]]:
    if not CHUNKS_OUT.exists():
        raise FileNotFoundError("data/advanced/chunks.json missing: run `python -m src.run adv-ingest`")
    return json.loads(CHUNKS_OUT.read_text(encoding="utf-8"))


def build_index(batch: int = 32) -> dict[str, Any]:
    """Embed every chunk (bge-base, no passage prefix) and replace the rows of this document."""
    from ..day6.embeddings import MyEmbedder

    chunks = load_chunks()
    t0 = time.perf_counter()
    emb = MyEmbedder(config.EMBEDDING_MODEL)
    load_s = time.perf_counter() - t0
    t1 = time.perf_counter()
    vectors = emb.embed_documents([c["text"] for c in chunks])
    embed_s = time.perf_counter() - t1
    too_long = sum(emb.count_tokens(c["text"]) > emb.max_seq_length for c in chunks)
    with psycopg.connect(config.database_url(), connect_timeout=5) as conn, conn.transaction():
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE} (
            chunk_id text PRIMARY KEY, document_id text NOT NULL, page integer NOT NULL, kind text NOT NULL,
            text text NOT NULL, content_hash text NOT NULL, metadata jsonb NOT NULL,
            embedding vector({emb.dimensions}) NOT NULL)""")
        doc_ids = sorted({c["source_id"] for c in chunks})
        conn.execute(f"DELETE FROM {TABLE} WHERE document_id = ANY(%s)", (doc_ids,))
        with conn.cursor() as cur:
            for c, v in zip(chunks, vectors):
                cur.execute(f"INSERT INTO {TABLE} VALUES (%s,%s,%s,%s,%s,%s,%s,%s::vector)",
                            (c["id"], c["source_id"], c["page"], c["metadata"]["kind"], c["text"],
                             hashlib.sha256(c["text"].encode()).hexdigest()[:16],
                             json.dumps({**c["metadata"], "source": c["source"]}, ensure_ascii=False), _vec(v)))
        n = conn.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    return {"table": TABLE, "rows": n, "model": emb.model_name, "dimensions": emb.dimensions,
            "chunks_over_512_tokens": too_long, "model_load_s": round(load_s, 1), "embed_s": round(embed_s, 1),
            "cost_usd": 0.0}


class AdvDenseRetriever:
    method = "dense"

    def __init__(self) -> None:
        from ..day6.embeddings import MyEmbedder

        self.embedder = MyEmbedder(config.EMBEDDING_MODEL)
        self.url = config.database_url()
        with psycopg.connect(self.url, connect_timeout=5) as conn:
            n = conn.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
        if n == 0:
            raise RuntimeError(f"{TABLE} is empty: run `python -m src.run adv-index`")

    def search(self, query: str, *, top_k: int = 5, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if filters:
            raise ValueError("advanced corpus has no filters")
        q = _vec(self.embedder.embed_query(query))
        with psycopg.connect(self.url, connect_timeout=5) as conn:
            rows = conn.execute(f"SELECT chunk_id, text, document_id, page, metadata, "
                                f"1 - (embedding <=> %s::vector) FROM {TABLE} "
                                f"ORDER BY embedding <=> %s::vector, chunk_id LIMIT %s", (q, q, top_k)).fetchall()
        out = []
        for rank, (cid, text, doc, page, meta, score) in enumerate(rows, 1):
            meta = dict(meta)
            source = meta.pop("source", "")
            out.append({"id": cid, "text": text, "source_id": doc, "source": source, "page": page,
                        "metadata": meta, "score": float(score), "rank": rank, "method": self.method})
        return out


def make_retriever(method: str):
    from ..retrievers import BM25Retriever, HybridRetriever

    if method == "dense":
        return AdvDenseRetriever()
    if method == "bm25":
        return BM25Retriever(load_chunks())
    if method == "hybrid":
        return HybridRetriever([AdvDenseRetriever(), BM25Retriever(load_chunks())], candidates=30)
    raise ValueError(method)
