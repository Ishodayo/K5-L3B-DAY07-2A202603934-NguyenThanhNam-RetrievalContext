"""Paths and settings for Day 7. Secrets come only from REPO/.env (never committed)."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "day7"
RESULTS_DIR = ROOT / "results"

load_dotenv(ROOT / ".env")

# Day 6 index reused as-is (phương án 1). Strategy B = section/paragraph chunks (528 rows).
# Day 6 strategy C was a copy of B plus a chapter filter, so filters are applied on B directly.
DAY6_STRATEGY = "B"
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL") or "BAAI/bge-base-en-v1.5"
EXPECTED_DIMENSIONS = 768


SOURCES_FILE = DATA_DIR / "sources.json"
# Document-level fields copied into every chunk's metadata (data/README: keep version or date).
VERSION_FIELDS = ("version", "pdf_sha256", "accessed_at")


def load_sources() -> dict[str, dict]:
    """source_id -> document info (title, license, version, ...)."""
    import json

    docs = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    return {d["source_id"]: d for d in docs}


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL is empty: copy .env.example to .env")
    return url
