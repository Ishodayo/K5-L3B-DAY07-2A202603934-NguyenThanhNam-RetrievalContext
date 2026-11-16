"""Context selection: deduplicate, keep rank order, fit a character budget, keep source headers."""
from __future__ import annotations

from typing import Any

CHARS_PER_TOKEN = 4  # rough estimate for English text; real token counts come from the model API


def block(chunk: dict[str, Any]) -> str:
    meta = chunk.get("metadata", {})
    return (f"[{chunk['id']} | {chunk['source_id']} {meta.get('version', '')} | page {chunk['page']} | "
            f"{meta.get('chapter_id', '')}]\n{chunk['text']}")


def pack_context(results: list[dict[str, Any]], budget_chars: int = 4000) -> tuple[str, list[str]]:
    """Add chunks in rank order while the whole context (headers included) stays within budget.

    A chunk that does not fit is skipped (not truncated) so every cited block is complete.
    Returns (context text, ids of included chunks).
    """
    if budget_chars < 1:
        raise ValueError("budget_chars must be positive")
    blocks: list[str] = []
    ids: list[str] = []
    seen: set[str] = set()
    for c in results:
        if c["id"] in seen:
            continue
        seen.add(c["id"])
        candidate = block(c)
        if len("\n\n".join(blocks + [candidate])) <= budget_chars:
            blocks.append(candidate)
            ids.append(c["id"])
    return "\n\n".join(blocks), ids


def estimate_tokens(text: str) -> int:
    return (len(text) + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN
