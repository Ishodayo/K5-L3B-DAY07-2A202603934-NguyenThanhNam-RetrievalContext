# Copied unchanged from Day 6 repo (K5-L3B-DAY06-NguyenThanhNam-2A202603934-DataIngestion, commit 9cbecf5, starter/src/store.py).
# Do not change embedding/query logic: queries must stay compatible with the Day 6 pgvector index.
"""Store and search vectors using PostgreSQL + pgvector (exact cosine search)."""
from __future__ import annotations

import json
from typing import Any

import psycopg

from .models import Chunk

TABLE = "chunks"
# Only these metadata columns may be used as filters (values are always SQL parameters).
FILTERABLE = {"chapter_id", "document_id", "page"}


def _vec(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.7f}" for x in v) + "]"


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int) -> None:
        if not database_url:
            raise ValueError("DATABASE_URL is empty (copy starter/.env.example to starter/.env)")
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.database_url = database_url
        self.dimensions = dimensions

    def _connect(self) -> psycopg.Connection:
        # Fails loudly if Docker/pgvector is not running; no silent fallback.
        return psycopg.connect(self.database_url, connect_timeout=5)

    def versions(self) -> dict:
        with self._connect() as conn:
            row = conn.execute("SELECT current_setting('server_version'), extversion "
                               "FROM pg_extension WHERE extname='vector'").fetchone()
        if not row:
            raise RuntimeError("pgvector extension is missing")
        return {"postgresql": row[0], "pgvector": row[1]}

    def create_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE} (
                    chunk_id      text PRIMARY KEY,
                    strategy      text NOT NULL,
                    document_id   text NOT NULL,
                    source        text NOT NULL,
                    page          integer NOT NULL,
                    chapter_id    text NOT NULL,
                    chapter_title text NOT NULL,
                    section       text,
                    text          text NOT NULL,
                    content_hash  text NOT NULL,
                    metadata      jsonb NOT NULL,
                    embedding     vector({self.dimensions}) NOT NULL
                )""")
            dim = conn.execute(
                "SELECT atttypmod FROM pg_attribute WHERE attrelid = %s::regclass AND attname = 'embedding'",
                (TABLE,)).fetchone()[0]
            if dim != self.dimensions:
                raise RuntimeError(f"Table {TABLE} has vector({dim}) but model has {self.dimensions} dims; "
                                   f"drop the table before switching model.")
            conn.execute(f"CREATE INDEX IF NOT EXISTS {TABLE}_strategy_chapter ON {TABLE} (strategy, chapter_id)")
            # No HNSW/IVFFlat index on purpose: exact nearest-neighbour search, so filters never drop results.

    def existing_hashes(self, strategy: str, document_id: str) -> dict[str, str]:
        with self._connect() as conn:
            rows = conn.execute(f"SELECT chunk_id, content_hash FROM {TABLE} WHERE strategy=%s AND document_id=%s",
                                (strategy, document_id)).fetchall()
        return dict(rows)

    def get_vectors(self, chunk_ids: list[str]) -> dict[str, list[float]]:
        """Read stored vectors back (used to reuse unchanged embeddings)."""
        if not chunk_ids:
            return {}
        with self._connect() as conn:
            rows = conn.execute(f"SELECT chunk_id, embedding::text FROM {TABLE} WHERE chunk_id = ANY(%s)",
                                (chunk_ids,)).fetchall()
        return {cid: json.loads(v) for cid, v in rows}

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> dict[str, int]:
        """Insert/update by stable chunk_id; delete this strategy's obsolete chunks of the same documents.

        Returns counts {inserted, updated, unchanged, deleted}. Re-running with identical input
        changes nothing, so the row count stays the same (no duplicates).
        """
        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
        if any(len(v) != self.dimensions for v in vectors):
            raise ValueError(f"vector dimension != {self.dimensions}")
        if len({c.chunk_id for c in chunks}) != len(chunks):
            raise ValueError("duplicate chunk_id in input")
        counts = {"inserted": 0, "updated": 0, "unchanged": 0, "deleted": 0}
        doc_ids = sorted({c.document_id for c in chunks})
        with self._connect() as conn, conn.transaction():
            old = dict(conn.execute(
                f"SELECT chunk_id, content_hash FROM {TABLE} WHERE strategy=%s AND document_id = ANY(%s)",
                (strategy, doc_ids)).fetchall())
            with conn.cursor() as cur:
                for c, v in zip(chunks, vectors):
                    h = c.metadata["content_hash"]
                    if old.get(c.chunk_id) == h:
                        counts["unchanged"] += 1
                        continue
                    counts["updated" if c.chunk_id in old else "inserted"] += 1
                    cur.execute(
                        f"""INSERT INTO {TABLE} (chunk_id, strategy, document_id, source, page, chapter_id,
                                chapter_title, section, text, content_hash, metadata, embedding)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::vector)
                            ON CONFLICT (chunk_id) DO UPDATE SET
                                text=EXCLUDED.text, content_hash=EXCLUDED.content_hash, page=EXCLUDED.page,
                                chapter_id=EXCLUDED.chapter_id, chapter_title=EXCLUDED.chapter_title,
                                section=EXCLUDED.section, metadata=EXCLUDED.metadata,
                                embedding=EXCLUDED.embedding""",
                        (c.chunk_id, strategy, c.document_id, c.source, c.page, c.metadata["chapter_id"],
                         c.metadata["chapter_title"], c.metadata.get("section"), c.text, h,
                         json.dumps(c.metadata, ensure_ascii=False), _vec(v)))
                obsolete = sorted(set(old) - {c.chunk_id for c in chunks})
                if obsolete:
                    cur.execute(f"DELETE FROM {TABLE} WHERE chunk_id = ANY(%s)", (obsolete,))
                counts["deleted"] = len(obsolete)
        return counts

    def count(self) -> dict[str, dict[str, int]]:
        with self._connect() as conn:
            rows = conn.execute(f"SELECT strategy, count(*), count(DISTINCT chunk_id) FROM {TABLE} "
                                f"GROUP BY strategy ORDER BY strategy").fetchall()
        return {s: {"rows": n, "distinct_ids": d} for s, n, d in rows}

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Exact cosine search inside one strategy; optional equality filters on whitelisted columns."""
        if len(query_vector) != self.dimensions:
            raise ValueError("query vector has wrong dimension")
        where, params = ["strategy = %s"], [strategy]
        for col, val in (filters or {}).items():
            if col not in FILTERABLE:
                raise ValueError(f"filter on '{col}' is not allowed")
            where.append(f"{col} = %s")
            params.append(val)
        q = _vec(query_vector)
        sql = (f"SELECT chunk_id, text, 1 - (embedding <=> %s::vector) AS score, document_id, source, page, "
               f"chapter_id, chapter_title, section, metadata FROM {TABLE} WHERE {' AND '.join(where)} "
               f"ORDER BY embedding <=> %s::vector, chunk_id LIMIT %s")
        with self._connect() as conn:
            rows = conn.execute(sql, [q, *params, q, top_k]).fetchall()
        keys = ["chunk_id", "text", "score", "document_id", "source", "page", "chapter_id",
                "chapter_title", "section", "metadata"]
        return [dict(zip(keys, r)) | {"score": float(r[2])} for r in rows]
