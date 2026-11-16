"""Advanced benchmark: build cases.json (no gold) from questions.json and verify it (ADVANCED.md §2)."""
from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

from .evaluate import ADV_DATA
from .index import load_chunks

MIN_TEST = {"table": 6, "image": 5, "chart": 5, "multihop": 4, "text": 4, "unanswerable": 6}
MIN_DEV_ANSWERABLE, MIN_DEV_UNANSWERABLE, MIN_TEST_TOTAL = 15, 3, 30
ABSENCE_REGEX = {
    "ad_u1": r"hospital bed|\bbeds?\b", "ad_u2": r"cholera", "ad_u3": r"maternal mortality.{0,60}2022",
    "at_u1": r"vaccine doses|doses administered", "at_u2": r"mpox|monkeypox",
    "at_u3": r"life expectancy.{0,40}2021", "at_u4": r"cancer incidence|new cancer cases",
    "at_u5": r"health expenditure per capita|current health expenditure", "at_u6": r"HIV prevalence",
}


def build_and_verify() -> dict[str, Any]:
    qs = json.loads((ADV_DATA / "questions.json").read_text(encoding="utf-8"))
    chunks = load_chunks()
    problems = []
    ids = [q["id"] for q in qs]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids")
    counts = Counter((q["split"], q["group"]) for q in qs)
    for g, n in MIN_TEST.items():
        if counts[("test", g)] < n:
            problems.append(f"test {g}: {counts[('test', g)]} < {n}")
    if sum(v for (s, _), v in counts.items() if s == "test") < MIN_TEST_TOTAL:
        problems.append("test < 30 questions")
    dev_ans = sum(v for (s, g), v in counts.items() if s == "dev" and g != "unanswerable")
    if dev_ans < MIN_DEV_ANSWERABLE or counts[("dev", "unanswerable")] < MIN_DEV_UNANSWERABLE:
        problems.append("dev needs >= 15 answerable + 3 unanswerable")
    pages = {c["page"] for c in chunks}
    for q in qs:
        if q["answerable"]:
            for e in q["evidence"]:
                if e["page"] not in pages:
                    problems.append(f"{q['id']}: evidence page {e['page']} has no chunk")
            if q["group"] == "multihop" and len({e["page"] for e in q["evidence"]}) < 2:
                problems.append(f"{q['id']}: multihop needs evidence from >= 2 pages")
    absence = {}
    for qid, pat in ABSENCE_REGEX.items():
        hits = [(c["id"], m.group(0)) for c in chunks for m in re.finditer(pat, c["text"], re.I)]
        absence[qid] = {"regex": pat, "hits": hits[:5], "n": len(hits)}
        if hits:
            problems.append(f"{qid}: absence regex matched {hits[:2]}")
    cases = [{"id": q["id"], "split": q["split"], "group": q["group"], "question": q["question"],
              "answerable": q["answerable"]} for q in qs]
    (ADV_DATA / "cases.json").write_text(json.dumps(cases, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    report = {"questions": len(qs), "counts": {f"{s}/{g}": n for (s, g), n in sorted(counts.items())},
              "chunks": len(chunks), "absence": absence, "problems": problems}
    out = ADV_DATA.parent.parent / "results" / "advanced" / "benchmark_verify.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
