# Copied unchanged from Day 6 repo (K5-L3B-DAY06-NguyenThanhNam-2A202603934-DataIngestion, commit 9cbecf5, starter/src/embeddings.py).
# Do not change embedding/query logic: queries must stay compatible with the Day 6 pgvector index.
"""Real local embedding model (sentence-transformers). No mock/random fallback."""
from __future__ import annotations

import logging
from typing import Protocol

DEFAULT_MODEL = "BAAI/bge-base-en-v1.5"
# Per the BGE v1.5 model card: add this instruction to short retrieval queries; passages get no prefix.
BGE_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class MyEmbedder:
    """Local SentenceTransformer adapter. Vectors are L2-normalized (cosine = dot product).

    Any load/encode error is raised: we never silently substitute fake vectors.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL, batch_size: int = 32, device: str = "cpu") -> None:
        logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
        from sentence_transformers import SentenceTransformer  # heavy import kept local

        self.model_name = model_name
        self.batch_size = batch_size
        self.model = SentenceTransformer(model_name, device=device)
        self.dimensions = int(self.model.get_sentence_embedding_dimension())
        self.max_seq_length = int(self.model.max_seq_length)
        self.query_prefix = BGE_QUERY_INSTRUCTION if "bge-" in model_name.lower() else ""
        self.revision = self._revision()

    def _revision(self) -> str:
        """Commit hash of the downloaded model snapshot (for the report), if available."""
        try:
            from huggingface_hub import scan_cache_dir

            for repo in scan_cache_dir().repos:
                if repo.repo_id == self.model_name:
                    return sorted(r.commit_hash for r in repo.revisions)[0]
        except Exception:  # noqa: BLE001 - informational only
            pass
        return "unknown"

    def count_tokens(self, text: str) -> int:
        return len(self.model.tokenizer(text)["input_ids"])

    def _encode(self, texts: list[str]) -> list[list[float]]:
        vecs = self.model.encode(texts, batch_size=self.batch_size, normalize_embeddings=True,
                                 convert_to_numpy=True, show_progress_bar=False)
        if vecs.shape != (len(texts), self.dimensions):
            raise RuntimeError(f"Unexpected embedding shape {vecs.shape}")
        return vecs.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._encode(texts)

    def embed_query(self, question: str) -> list[float]:
        return self._encode([self.query_prefix + question])[0]

    def info(self) -> dict:
        return {"provider": "local sentence-transformers", "model": self.model_name,
                "revision": self.revision, "dimensions": self.dimensions,
                "max_seq_length": self.max_seq_length, "normalize": True,
                "query_prefix": self.query_prefix, "document_prefix": "", "cost_usd": 0.0}
