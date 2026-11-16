"""Adapter: Day 6 pgvector index -> Day 7 chunk schema (id, text, source_id, source, page, metadata).

Dense retrieval embeds the query with the same model/prefix as Day 6, so it is compatible with
the stored vectors. Any DB or model error is raised; there is no fake fallback.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import psycopg

from . import config
from .day6.store import TABLE, PgVectorStore


def to_day7(row: dict[str, Any], strategy: str,
            sources: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Map one Day 6 row to the Day 7 contract (data/README.md).

    `sources` (source_id -> document info) adds version/sha256/accessed_at to metadata,
    so the cited chunk can be traced to the exact document version.
    """
    meta = dict(row.get("metadata") or {})
    meta.update({"strategy": strategy, "chapter_id": row["chapter_id"],
                 "chapter_title": row["chapter_title"], "section": row.get("section")})
    if sources is not None:
        if row["document_id"] not in sources:
            raise KeyError(f"document {row['document_id']} missing from {config.SOURCES_FILE.name}")
        doc = sources[row["document_id"]]
        meta.update({k: doc[k] for k in config.VERSION_FIELDS})
    return {"id": row["chunk_id"], "text": row["text"], "source_id": row["document_id"],
            "source": row["source"], "page": row["page"], "metadata": meta}


def index_info(database_url: str, strategy: str) -> dict[str, Any]:
    """Row count and vector dimension of the stored index (to check compatibility)."""
    with psycopg.connect(database_url, connect_timeout=5) as conn:
        dim = conn.execute("SELECT atttypmod FROM pg_attribute WHERE attrelid = %s::regclass "
                           "AND attname = 'embedding'", (TABLE,)).fetchone()[0]
        rows = conn.execute(f"SELECT count(*), count(DISTINCT chunk_id) FROM {TABLE} WHERE strategy=%s",
                            (strategy,)).fetchone()
        versions = conn.execute("SELECT current_setting('server_version'), extversion "
                                "FROM pg_extension WHERE extname='vector'").fetchone()
    return {"table": TABLE, "strategy": strategy, "rows": rows[0], "distinct_ids": rows[1],
            "vector_dimensions": dim, "postgresql": versions[0], "pgvector": versions[1]}


def export_chunks(database_url: str, strategy: str, out: Path) -> int:
    """Write all chunks of one strategy (no vectors) as a JSON array, ordered by page and id."""
    with psycopg.connect(database_url, connect_timeout=5) as conn:
        cur = conn.execute(f"SELECT chunk_id, text, document_id, source, page, chapter_id, chapter_title, "
                           f"section, metadata FROM {TABLE} WHERE strategy=%s ORDER BY page, chunk_id",
                           (strategy,))
        keys = [d.name for d in cur.description]
        sources = config.load_sources()
        chunks = [to_day7(dict(zip(keys, r)), strategy, sources) for r in cur.fetchall()]
    if not chunks:
        raise RuntimeError(f"no chunks for strategy {strategy}: run Day 6 ingest first")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(chunks, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return len(chunks)


class DenseRetriever:
    """Method M1: dense cosine search on the Day 6 pgvector index (exact search, optional filters)."""

    method = "dense"

    def __init__(self, strategy: str = config.DAY6_STRATEGY, database_url: str | None = None,
                 model_name: str = config.EMBEDDING_MODEL) -> None:
        from .day6.embeddings import MyEmbedder  # heavy import (torch) kept local

        self.strategy = strategy
        self.database_url = database_url or config.database_url()
        started = time.perf_counter()
        self.embedder = MyEmbedder(model_name)
        self.load_seconds = time.perf_counter() - started
        info = index_info(self.database_url, strategy)
        if info["vector_dimensions"] != self.embedder.dimensions:
            raise RuntimeError(f"index has vector({info['vector_dimensions']}) but query model "
                               f"{model_name} has {self.embedder.dimensions} dims")
        if info["rows"] == 0:
            raise RuntimeError(f"index strategy {strategy} is empty: run Day 6 ingest first")
        self.index = info
        self.sources = config.load_sources()
        self.store = PgVectorStore(self.database_url, self.embedder.dimensions)

    def search(self, query: str, *, top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if not query.strip() or top_k < 1:
            raise ValueError("query must be non-empty and top_k >= 1")
        vector = self.embedder.embed_query(query)
        rows = self.store.search(self.strategy, vector, top_k=top_k, filters=filters)
        results = []
        for rank, row in enumerate(rows, 1):
            chunk = to_day7(row, self.strategy, self.sources)
            chunk.update({"score": row["score"], "rank": rank, "method": self.method})
            results.append(chunk)
        return results

    def info(self) -> dict[str, Any]:
        return {"method": self.method, "embedding": self.embedder.info(), "index": self.index,
                "model_load_seconds": round(self.load_seconds, 2)}
