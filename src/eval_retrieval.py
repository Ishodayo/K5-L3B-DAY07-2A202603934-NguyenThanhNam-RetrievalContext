"""Retrieval + context evaluation on one split (no LLM).

Per answerable question: run the method on the ORIGINAL question (+ user-provided filter only),
keep the top-10 ranking, pack the top_k into the context budget, and label hits with the gold
evidence (labels are computed after retrieval; gold never reaches the retriever).

Metrics (benchmark/README.md): Hit@1, Evidence Hit@3, Hit@k, MRR@10, Context Evidence Rate,
median latency, context size. Unanswerable questions are excluded from these denominators.
"""
from __future__ import annotations

import csv
import json
import statistics
import time
from datetime import datetime, timezone
from typing import Any

from . import config
from .benchmark import QUESTIONS_OUT, evidence_hit
from .context import estimate_tokens, pack_context

RANK_DEPTH = 10  # ranking kept for MRR@10 / analysis; metrics at 1 and 3 always reported

# Configs compared in GĐ3 (dev). GĐ5 adds improvement configs here.
CONFIGS: dict[str, dict[str, Any]] = {
    "dense": {"method": "dense", "top_k": 3, "budget_chars": 4000,
              "desc": "M1 dense pgvector (bge-base-en-v1.5, cosine, exact), top-3"},
    "bm25": {"method": "bm25", "top_k": 3, "budget_chars": 4000,
             "desc": "M2 BM25Okapi k1=1.5 b=0.75, word tokens, top-3"},
    "hybrid": {"method": "hybrid", "top_k": 3, "budget_chars": 4000, "candidates": 20, "rrf_k": 60,
               "desc": "M3 RRF(dense top-20, bm25 top-20), k=60, top-3"},
}

OUT_DIR = config.RESULTS_DIR / "retrieval"


class RetrieverFactory:
    """Builds retrievers once and records their setup cost (model load / index build)."""

    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}
        self.setup_seconds: dict[str, float] = {}

    def _timed(self, key: str, build) -> Any:
        if key not in self._cache:
            t = time.perf_counter()
            self._cache[key] = build()
            self.setup_seconds[key] = round(time.perf_counter() - t, 2)
        return self._cache[key]

    def dense(self):
        from .day6_store import DenseRetriever
        return self._timed("dense", DenseRetriever)

    def bm25(self, tokenizer: str = "word"):
        from .retrievers import BM25Retriever, load_chunks
        return self._timed(f"bm25_{tokenizer}", lambda: BM25Retriever(load_chunks(), tokenizer=tokenizer))

    def get(self, cfg: dict[str, Any]):
        from .retrievers import HybridRetriever
        m = cfg["method"]
        if m == "dense":
            return self.dense()
        if m == "bm25":
            return self.bm25(cfg.get("tokenizer", "word"))
        if m == "hybrid":
            return HybridRetriever([self.dense(), self.bm25(cfg.get("tokenizer", "word"))],
                                   candidates=cfg.get("candidates", 20), k=cfg.get("rrf_k", 60))
        raise ValueError(f"unknown method {m}")


def load_questions(split: str) -> list[dict[str, Any]]:
    qs = json.loads(QUESTIONS_OUT.read_text(encoding="utf-8"))
    return [q for q in qs if q["split"] == split and q.get("answerable", True)]


def evaluate_question(q: dict[str, Any], retriever, cfg: dict[str, Any]) -> dict[str, Any]:
    top_k = cfg["top_k"]
    filters = q.get("filter")  # user-provided scope only
    trace: dict[str, Any] = {"query_id": q["id"], "split": q["split"], "type": q.get("type"),
                             "question": q["question"], "filter": filters, "method": cfg["method"],
                             "top_k": top_k, "budget_chars": cfg["budget_chars"]}
    started = time.perf_counter()
    try:
        results = retriever.search(q["question"], top_k=max(RANK_DEPTH, top_k), filters=filters)
    except Exception as exc:  # recorded, not hidden: counts as a miss in every metric
        trace.update({"status": "error", "error": f"{type(exc).__name__}: {exc}",
                      "elapsed_ms": (time.perf_counter() - started) * 1000, "results": [],
                      "context": "", "context_ids": [], "hit1": False, "hit3": False, "hitk": False,
                      "rr": 0.0, "context_hit": False, "context_chars": 0, "context_tokens_est": 0})
        return trace
    elapsed_ms = (time.perf_counter() - started) * 1000
    context, ids = pack_context(results[:top_k], cfg["budget_chars"])
    labelled = []
    for c in results:
        labelled.append({"rank": c["rank"], "id": c["id"], "page": c["page"],
                         "chapter_id": c["metadata"].get("chapter_id"), "score": round(c["score"], 5),
                         "hit": evidence_hit(c, q["gold"]),
                         **({"component_ranks": c["component_ranks"]} if "component_ranks" in c else {})})
    first_hit = next((r["rank"] for r in labelled if r["hit"]), None)
    trace.update({
        "status": "ok", "elapsed_ms": round(elapsed_ms, 1), "results": labelled,
        "context": context, "context_ids": ids, "context_chars": len(context),
        "context_tokens_est": estimate_tokens(context),
        "hit1": first_hit == 1, "hit3": first_hit is not None and first_hit <= 3,
        "hitk": first_hit is not None and first_hit <= top_k,
        "rr": 1.0 / first_hit if first_hit else 0.0,
        "context_hit": any(r["hit"] and r["id"] in ids for r in labelled),
        "gold_pages": sorted({g["page"] for g in q["gold"]}),  # for error analysis only (after retrieval)
    })
    return trace


def summarize(name: str, cfg: dict[str, Any], traces: list[dict[str, Any]], setup: float) -> dict[str, Any]:
    n = len(traces)
    ok = [t for t in traces if t["status"] == "ok"]

    def frac(key: str) -> str:
        k = sum(t[key] for t in traces)
        return f"{k}/{n}"

    return {
        "config": name, "split": traces[0]["split"] if traces else None, "method": cfg["method"],
        "desc": cfg.get("desc", ""), "top_k": cfg["top_k"], "budget_chars": cfg["budget_chars"],
        "N": n, "errors": n - len(ok),
        "hit1": frac("hit1"), "hit1_rate": round(sum(t["hit1"] for t in traces) / n, 3),
        "hit3": frac("hit3"), "hit3_rate": round(sum(t["hit3"] for t in traces) / n, 3),
        "hitk": frac("hitk"),
        "context_evidence": frac("context_hit"),
        "context_evidence_rate": round(sum(t["context_hit"] for t in traces) / n, 3),
        "mrr10": round(sum(t["rr"] for t in traces) / n, 3),
        "filter_questions": sum(1 for t in traces if t["filter"]),
        "median_ms": round(statistics.median(t["elapsed_ms"] for t in ok), 1) if ok else None,
        "mean_context_chars": round(statistics.mean(t["context_chars"] for t in ok)) if ok else 0,
        "mean_context_tokens_est": round(statistics.mean(t["context_tokens_est"] for t in ok)) if ok else 0,
        "mean_context_chunks": round(statistics.mean(len(t["context_ids"]) for t in ok), 2) if ok else 0,
        "setup_seconds": setup, "cost_usd": 0.0,
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def run(split: str, names: list[str], *, confirm_test: bool = False) -> list[dict[str, Any]]:
    if split == "test" and not confirm_test:
        raise SystemExit("test split is held out: choose the config on dev first, then pass --confirm-test")
    unknown = [n for n in names if n not in CONFIGS]
    if unknown:
        raise SystemExit(f"unknown config(s) {unknown}; known: {sorted(CONFIGS)}")
    questions = load_questions(split)
    factory = RetrieverFactory()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = []
    for name in names:
        cfg = CONFIGS[name]
        retriever = factory.get(cfg)
        tok = f"bm25_{cfg.get('tokenizer', 'word')}"
        parts = {"dense": ["dense"], "bm25": [tok], "hybrid": ["dense", tok]}[cfg["method"]]
        setup = sum(factory.setup_seconds.get(p, 0.0) for p in parts)  # model load / index build
        traces = [evaluate_question(q, retriever, cfg) | {"config": name} for q in questions]
        with (OUT_DIR / f"{name}_{split}.jsonl").open("w", encoding="utf-8") as f:
            for t in traces:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
        summaries.append(summarize(name, cfg, traces, round(setup, 2)))
    _save_summary(split, summaries)
    if split == "test":
        log = OUT_DIR / "test_runs.json"
        runs = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
        runs.append({"configs": names, "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        log.write_text(json.dumps(runs, indent=2) + "\n", encoding="utf-8")
    return summaries


def _save_summary(split: str, summaries: list[dict[str, Any]]) -> None:
    path = OUT_DIR / f"summary_{split}.json"
    existing = {s["config"]: s for s in json.loads(path.read_text(encoding="utf-8"))} if path.exists() else {}
    existing.update({s["config"]: s for s in summaries})
    rows = [existing[k] for k in sorted(existing, key=lambda k: list(CONFIGS).index(k) if k in CONFIGS else 99)]
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (OUT_DIR / f"summary_{split}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
