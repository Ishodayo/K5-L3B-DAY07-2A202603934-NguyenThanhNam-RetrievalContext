"""Build and verify the Day 7 benchmark.

Inputs (committed, hand-checked):
  benchmark/day6_questions.jsonl  — 22 answerable questions, copied unchanged from Day 6
  benchmark/unanswerable.json     — questions without evidence in the corpus (written for Day 7)
Outputs:
  data/day7/questions.json   — answerable only, Day 7 schema (id, split, question, expected_answer, gold, filter?)
  data/day7/agent_cases.json — every case with `answerable`; NO gold/answer (safe to feed the agent runner)

Gold never enters retrieval or the agent: runners read agent_cases.json, scorers read questions.json.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from . import config

BENCH_DIR = config.ROOT / "benchmark"
DAY6_QUESTIONS = BENCH_DIR / "day6_questions.jsonl"
UNANSWERABLE = BENCH_DIR / "unanswerable.json"
QUESTIONS_OUT = config.DATA_DIR / "questions.json"
CASES_OUT = config.DATA_DIR / "agent_cases.json"
CHUNKS = config.DATA_DIR / "chunks.json"

MIN_COUNTS = {("dev", True): 15, ("dev", False): 2, ("test", True): 5, ("test", False): 2}


def match_key(text: str) -> str:
    """Day 6 matching rule: NFC, join end-of-line hyphens, drop all whitespace, lowercase."""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"-\n", "", text)
    return re.sub(r"\s+", "", text).lower()


def evidence_hit(chunk: dict[str, Any], gold: list[dict[str, Any]]) -> bool:
    """A chunk is a hit if it is from a gold source+page and contains that evidence (normalized)."""
    key = match_key(chunk["text"])
    return any(chunk["source_id"] == g["source_id"] and chunk["page"] == g["page"]
               and match_key(g["evidence"]) in key for g in gold)


def exact_span(text: str, evidence: str) -> str | None:
    """Return the exact substring of `text` that matches `evidence` under match_key, or None.

    Used once at build time so `evidence in chunk['text']` also holds (starter baseline contract).
    """
    if evidence in text:
        return evidence
    keychars, positions = [], []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "-" and text[i + 1:i + 2] == "\n":
            i += 2
            continue
        if not ch.isspace():
            low = ch.lower()
            keychars.append(low if len(low) == 1 else ch)
            positions.append(i)
        i += 1
    target = match_key(evidence)
    start = "".join(keychars).find(target)
    if start < 0 or not target:
        return None
    return text[positions[start]:positions[start + len(target) - 1] + 1]


def _day6_gold(q: dict[str, Any]) -> list[dict[str, Any]]:
    gold = [{"source_id": q["gold_source_id"], "page": q["gold_page"], "evidence": q["evidence_quote"]}]
    for alt in q.get("alternatives", []):
        gold.append({"source_id": alt.get("gold_source_id", q["gold_source_id"]), "page": alt["gold_page"],
                     "evidence": alt["evidence_quote"]})
    return gold


def build(chunks: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_page: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for c in chunks:
        by_page.setdefault((c["source_id"], c["page"]), []).append(c)

    questions = []
    for line in DAY6_QUESTIONS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        q = json.loads(line)
        gold = []
        for g in _day6_gold(q):
            span = next((s for c in by_page.get((g["source_id"], g["page"]), [])
                         if (s := exact_span(c["text"], g["evidence"]))), None)
            if span is None:
                raise ValueError(f"{q['id']}: evidence not inside one chunk of page {g['page']}")
            entry = {**g, "evidence": span}
            if span != g["evidence"]:
                entry["evidence_day6"] = g["evidence"]  # original quote kept for traceability
            gold.append(entry)
        item = {"id": q["id"], "split": q["split"], "type": q["type"], "question": q["question"],
                "expected_answer": q["expected_answer"], "gold": gold, "answerable": True}
        if q.get("filter"):
            item["filter"] = q["filter"]  # user-provided scope, allowed as retrieval input
        questions.append(item)

    unanswerable = json.loads(UNANSWERABLE.read_text(encoding="utf-8"))
    cases = [{"id": q["id"], "split": q["split"], "type": q["type"], "question": q["question"],
              "answerable": True, "expected_behavior": "search_and_answer",
              **({"filter": q["filter"]} if "filter" in q else {})} for q in questions]
    cases += [{"id": u["id"], "split": u["split"], "type": "unanswerable", "question": u["question"],
               "answerable": False, "expected_behavior": "search_and_abstain",
               "absence_reason": u["absence_reason"]} for u in unanswerable]
    return questions, cases


def verify(chunks: list[dict[str, Any]], questions: list[dict[str, Any]],
           cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Check counts, evidence, filters, split hygiene and absence; return a report (problems listed)."""
    problems: list[str] = []
    chapter_of = {(c["source_id"], c["page"]): c["metadata"]["chapter_id"] for c in chunks}
    chapters = set(chapter_of.values())

    ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)):
        problems.append("duplicate case id")
    if {q["id"] for q in questions} != {c["id"] for c in cases if c["answerable"]}:
        problems.append("questions.json and agent_cases.json answerable ids differ")
    leaked = [c["id"] for c in cases if {"gold", "expected_answer", "evidence"} & set(c)]
    if leaked:
        problems.append(f"gold/answer fields in agent_cases: {leaked}")

    counts = Counter((c["split"], c["answerable"]) for c in cases)
    for key, need in MIN_COUNTS.items():
        if counts[key] < need:
            problems.append(f"{key[0]} answerable={key[1]}: {counts[key]} < {need}")

    evidence_rows = []
    for q in questions:
        for g in q["gold"]:
            hits = [c["id"] for c in chunks if evidence_hit(c, [g])]
            exact = [c["id"] for c in chunks if c["source_id"] == g["source_id"] and c["page"] == g["page"]
                     and g["evidence"] in c["text"]]
            evidence_rows.append({"id": q["id"], "page": g["page"], "chunks": hits, "exact": bool(exact)})
            if not hits or not exact:
                problems.append(f"{q['id']} p{g['page']}: evidence not found in a chunk")
        if "filter" in q:
            want = q["filter"].get("chapter_id")
            main = q["gold"][0]
            if want not in chapters:
                problems.append(f"{q['id']}: unknown filter chapter {want}")
            elif chapter_of.get((main["source_id"], main["page"])) != want:
                problems.append(f"{q['id']}: filter {want} does not contain the gold page")

    dev_ch = {chapter_of[(q["gold"][0]["source_id"], q["gold"][0]["page"])] for q in questions if q["split"] == "dev"}
    test_ch = {chapter_of[(q["gold"][0]["source_id"], q["gold"][0]["page"])] for q in questions if q["split"] == "test"}
    if dev_ch & test_ch:
        problems.append(f"chapters in both dev and test: {sorted(dev_ch & test_ch)}")

    absence_rows = []
    for u in json.loads(UNANSWERABLE.read_text(encoding="utf-8")):
        found = [(c["id"], m.group(0)) for pat in u["absence_check"] for c in chunks
                 for m in re.finditer(pat, c["text"], re.I)]
        absence_rows.append({"id": u["id"], "patterns": u["absence_check"], "matches": found})
        if found:
            problems.append(f"{u['id']}: absence check matched {found[:3]}")

    sys.path.insert(0, str(config.ROOT / "starter"))
    try:
        from baseline import validate  # starter contract: exact evidence inside a chunk of the gold page
        validate(chunks, questions)
        starter_contract = "ok"
    except ValueError as exc:
        starter_contract = f"failed: {exc}"
        problems.append(f"starter validate: {exc}")

    return {
        "counts": {f"{s}_{'answerable' if a else 'unanswerable'}": n for (s, a), n in sorted(counts.items())},
        "total_cases": len(cases), "gold_evidence": len(evidence_rows),
        "evidence_rewritten_from_day6": sum("evidence_day6" in g for q in questions for g in q["gold"]),
        "with_filter": sum("filter" in q for q in questions),
        "dev_chapters": sorted(dev_ch), "test_chapters": sorted(test_ch),
        "starter_validate": starter_contract,
        "evidence": evidence_rows, "absence": absence_rows, "problems": problems,
    }


def load_chunks() -> list[dict[str, Any]]:
    if not CHUNKS.exists():
        raise FileNotFoundError(f"{CHUNKS} missing: run `python -m src.run export-chunks` first")
    return json.loads(CHUNKS.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
