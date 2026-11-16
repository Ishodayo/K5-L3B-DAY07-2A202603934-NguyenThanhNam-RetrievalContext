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


class NeighborIndex:
    """Adjacent chunks in reading order (page, id) that belong to the same section.

    Day 6 chunk B never crosses a page, so a section is often split; the retriever finds the
    section start while the evidence sits in the following chunk (dev d09, d15).
    """

    def __init__(self, chunks: list[dict[str, Any]]) -> None:
        order = sorted(chunks, key=lambda c: (c["source_id"], c["page"], c["id"]))
        self.next: dict[str, dict[str, Any]] = {}
        self.prev: dict[str, dict[str, Any]] = {}
        for a, b in zip(order, order[1:]):
            same = (a["source_id"] == b["source_id"] and a["metadata"].get("section")
                    and a["metadata"].get("section") == b["metadata"].get("section"))
            if same:
                self.next[a["id"]] = b
                self.prev[b["id"]] = a

    def expand(self, results: list[dict[str, Any]], mode: str = "next") -> list[dict[str, Any]]:
        """Insert each result's neighbour(s) right after it; neighbours keep the parent's rank."""
        if mode not in ("next", "both"):
            raise ValueError("mode must be 'next' or 'both'")
        out: list[dict[str, Any]] = []
        seen: set[str] = set()

        def add(c: dict[str, Any], parent: dict[str, Any] | None) -> None:
            if c["id"] in seen:
                return
            seen.add(c["id"])
            if parent is None:
                out.append(c)
            else:
                out.append({**c, "score": parent.get("score", 0.0), "rank": parent.get("rank"),
                            "method": "neighbor", "neighbor_of": parent["id"]})

        for r in results:
            if mode == "both" and r["id"] in self.prev:
                add(self.prev[r["id"]], r)
            add(r, None)
            if r["id"] in self.next:
                add(self.next[r["id"]], r)
        return out


def estimate_tokens(text: str) -> int:
    return (len(text) + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN
