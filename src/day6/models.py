# Copied unchanged from Day 6 repo (K5-L3B-DAY06-NguyenThanhNam-2A202603934-DataIngestion, commit 9cbecf5, starter/src/models.py).
# Do not change embedding/query logic: queries must stay compatible with the Day 6 pgvector index.
"""Shared data contracts; keep traceability from chunk back to source."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentPage:
    document_id: str
    source: str
    page: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    source: str
    page: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
