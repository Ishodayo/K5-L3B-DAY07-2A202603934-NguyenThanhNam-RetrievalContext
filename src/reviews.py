"""Manual labelling helpers (BENCHMARK.md §3). The labels are written by the student, not by code.

review-sheet  : writes, per config and split,
                results/agent/{cfg}_{split}_review.md   — what to read: question, expected answer, gold page,
                                                          agent answer, full text of every cited chunk
                results/agent/{cfg}_{split}_review.csv  — blank label table to fill (Excel / any editor)
import-reviews: reads the filled CSV -> {cfg}_{split}_reviews.json (starter format) -> runs
                starter/agent_metrics.py aggregate -> {cfg}_{split}_metrics.json

CSV columns to fill:
  answer_grade        answerable cases: 0 = wrong/missing evidence, 1 = partly right, 2 = right and complete
                      (an abstention on an answerable case is 0)
  citation_support    one 1/0 per citation, in the order of the `citations` column, separated by ";"
                      (1 = the chunk really supports the sentence it is attached to)
  abstention_correct  unanswerable cases: 1 = refused without unsupported claims, 0 = otherwise
  reason              short reason (required)
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

from . import config
from .benchmark import CASES_OUT, QUESTIONS_OUT

AGENT_DIR = config.RESULTS_DIR / "agent"
FIELDS = ["query_id", "answerable", "status", "citations", "answer_grade", "citation_support",
          "abstention_correct", "reason"]


def _traces(cfg: str, split: str) -> list[dict[str, Any]]:
    path = AGENT_DIR / f"{cfg}_{split}_traces.json"
    if not path.exists():
        raise SystemExit(f"{path.name} not found: run agent-eval first")
    return json.loads(path.read_text(encoding="utf-8"))


def export_sheet(cfg: str, split: str) -> tuple[Path, Path]:
    questions = {q["id"]: q for q in json.loads(QUESTIONS_OUT.read_text(encoding="utf-8"))}
    cases = {c["id"]: c for c in json.loads(CASES_OUT.read_text(encoding="utf-8"))}
    chunks = {c["id"]: c for c in json.loads((config.DATA_DIR / "chunks.json").read_text(encoding="utf-8"))}
    traces = _traces(cfg, split)
    md = [f"# Bảng chấm tay — `{cfg}` / {split}", "",
          "Đọc từng câu, đối chiếu câu trả lời với đáp án chuẩn và với **text của từng chunk được trích**, "
          "rồi điền file CSV cùng tên. Thang điểm: BENCHMARK.md §3. Chunk ID có dạng `B:thinkpython2:pTTT:NNN` "
          "(TTT = trang PDF; trang in = trang PDF − 22).", ""]
    rows = []
    for t in traces:
        qid = t["query_id"]
        md += [f"## {qid} — {'có đáp án' if t['answerable'] else 'THIẾU evidence'} — status `{t['status']}`", "",
               f"**Câu hỏi:** {t['question']}", ""]
        if qid in questions:
            q = questions[qid]
            md += [f"**Đáp án chuẩn:** {q['expected_answer']}  ",
                   f"**Trang gold:** {', '.join(str(g['page']) for g in q['gold'])}", ""]
        else:
            md += [f"**Vì sao thiếu evidence:** {cases[qid].get('absence_reason', '')}", ""]
        md += [f"**Query agent đã tìm:** " + "; ".join(f"`{e['query']}`" for e in t["events"] if e["event"] == "search"),
               "", "**Câu trả lời của agent:**", "", "> " + (t["answer"] or "(trống)").replace("\n", "\n> "), ""]
        for i, cid in enumerate(t["citations"], 1):
            text = " ".join(chunks[cid]["text"].split())
            md += [f"<details><summary>Citation {i}: <code>{cid}</code> (trang {chunks[cid]['page']})</summary>",
                   "", text, "", "</details>", ""]
        md += ["---", ""]
        rows.append({"query_id": qid, "answerable": int(t["answerable"]), "status": t["status"],
                     "citations": ";".join(t["citations"]), "answer_grade": "", "citation_support": "",
                     "abstention_correct": "", "reason": ""})
    md_path = AGENT_DIR / f"{cfg}_{split}_review.md"
    csv_path = AGENT_DIR / f"{cfg}_{split}_review.csv"
    md_path.write_text("\n".join(md), encoding="utf-8")
    if csv_path.exists():
        print(f"{csv_path.name} already exists — not overwritten (delete it to start again)")
    else:
        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:  # BOM so Excel shows Vietnamese
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
    return md_path, csv_path


CTX_FIELDS = ["query_id", "context_ids", "context_grade", "reason"]


def export_context_sheet(cfg: str, split: str) -> tuple[Path, Path]:
    """BENCHMARK §2: grade the FINAL agent context 0/1/2 for answerable cases (0 = no evidence,
    1 = evidence but missing a condition or source, 2 = enough evidence and source)."""
    questions = {q["id"]: q for q in json.loads(QUESTIONS_OUT.read_text(encoding="utf-8"))}
    chunks = {c["id"]: c for c in json.loads((config.DATA_DIR / "chunks.json").read_text(encoding="utf-8"))}
    md = [f"# Chấm context 0/1/2 — `{cfg}` / {split}", "",
          "Đọc context cuối agent nhận được (các chunk dưới), so với đáp án chuẩn và evidence gold. "
          "**0** = không có evidence · **1** = có nhưng thiếu điều kiện hoặc nguồn · **2** = đủ evidence và nguồn.", ""]
    rows = []
    for t in _traces(cfg, split):
        q = questions.get(t["query_id"])
        if q is None:
            continue  # unanswerable cases are not graded for context
        md += [f"## {q['id']} — {q['question']}", "", f"**Đáp án chuẩn:** {q['expected_answer']}  ",
               "**Evidence gold:** " + " · ".join(f"p{g['page']}: “{' '.join(g['evidence'].split())}”"
                                                  for g in q["gold"]), "",
               f"**Context cuối:** {len(t['context_ids'])} chunk, {t['context_chars']} ký tự", ""]
        for cid in t["context_ids"]:
            md += [f"<details><summary><code>{cid}</code> (trang {chunks[cid]['page']})</summary>", "",
                   " ".join(chunks[cid]["text"].split()), "", "</details>", ""]
        md += ["---", ""]
        rows.append({"query_id": q["id"], "context_ids": ";".join(t["context_ids"]), "context_grade": "",
                     "reason": ""})
    md_path = AGENT_DIR / f"{cfg}_{split}_context_review.md"
    csv_path = AGENT_DIR / f"{cfg}_{split}_context_review.csv"
    md_path.write_text("\n".join(md), encoding="utf-8")
    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=CTX_FIELDS)
            w.writeheader()
            w.writerows(rows)
    return md_path, csv_path


def import_context(cfg: str, split: str) -> dict[str, Any]:
    path = AGENT_DIR / f"{cfg}_{split}_context_review.csv"
    text = path.read_text(encoding="utf-8-sig")
    header = text.splitlines()[0] if text else ""
    rows = list(csv.DictReader(text.splitlines(), delimiter=";" if header.count(";") > header.count(",") else ","))
    counts, labels, problems = {"0": 0, "1": 0, "2": 0}, [], []
    for r in rows:
        g = r["context_grade"].strip()
        if g == "":
            continue  # BENCHMARK §2 asks for at least 5 graded answerable cases, not all
        if g not in counts or not r["reason"].strip():
            problems.append(f"{r['query_id']}: context_grade must be 0/1/2 with a reason")
            continue
        counts[g] += 1
        labels.append({"query_id": r["query_id"], "context_grade": int(g), "reason": r["reason"].strip()})
    if problems:
        raise SystemExit("Fix the CSV first:\n  " + "\n  ".join(problems))
    if len(labels) < 5:
        print(f"warning: {len(labels)} graded cases; BENCHMARK §2 asks for at least 5")
    n = len(labels)
    report = {"config": cfg, "split": split, "graded": n, "counts": counts,
              "mean": round((counts["1"] + 2 * counts["2"]) / n, 3) if n else None, "labels": labels}
    (AGENT_DIR / f"{cfg}_{split}_context_metrics.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def _flag(value: str, name: str, qid: str) -> bool:
    v = value.strip().lower()
    if v in ("1", "true", "yes", "y", "đúng", "x"):
        return True
    if v in ("0", "false", "no", "n", "sai"):
        return False
    raise ValueError(f"{qid}: {name} must be 1 or 0, got {value!r}")


def import_reviews(cfg: str, split: str) -> dict[str, Any]:
    csv_path = AGENT_DIR / f"{cfg}_{split}_review.csv"
    traces = {t["query_id"]: t for t in _traces(cfg, split)}
    text = csv_path.read_text(encoding="utf-8-sig")
    header = text.splitlines()[0] if text else ""
    delim = ";" if header.count(";") > header.count(",") else ","  # Excel (VN locale) may save with ";"
    rows = list(csv.DictReader(text.splitlines(), delimiter=delim))
    reviews, problems = [], []
    for r in rows:
        qid = r["query_id"].strip()
        t = traces.get(qid)
        if t is None:
            problems.append(f"{qid}: not in traces")
            continue
        try:
            sup_raw = [s for s in r["citation_support"].replace(",", ";").split(";") if s.strip()]
            support = [_flag(s, "citation_support", qid) for s in sup_raw]
            if len(support) != len(t["citations"]):
                raise ValueError(f"{qid}: {len(t['citations'])} citation(s) need {len(t['citations'])} value(s) "
                                 f"in citation_support, got {len(support)}")
            if not r["reason"].strip():
                raise ValueError(f"{qid}: reason is empty")
            rev = {"query_id": qid, "citation_support": support, "reason": r["reason"].strip()}
            if t["answerable"]:
                grade = int(r["answer_grade"])
                if grade not in (0, 1, 2):
                    raise ValueError(f"{qid}: answer_grade must be 0, 1 or 2")
                rev["answer_grade"] = grade
            else:
                rev["abstention_correct"] = _flag(r["abstention_correct"], "abstention_correct", qid)
            reviews.append(rev)
        except (ValueError, KeyError) as exc:
            problems.append(str(exc))
    if problems:
        raise SystemExit("Fix the CSV first:\n  " + "\n  ".join(problems))
    (AGENT_DIR / f"{cfg}_{split}_reviews.json").write_text(
        json.dumps(reviews, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sys.path.insert(0, str(config.ROOT / "starter"))
    from agent_metrics import aggregate

    cases = [c for c in json.loads(CASES_OUT.read_text(encoding="utf-8")) if c["split"] == split]
    report = {"split": split, "config": cfg, **aggregate(cases, list(traces.values()), reviews)}
    (AGENT_DIR / f"{cfg}_{split}_metrics.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
