"""Run the agent on every case of a split and save traces in the starter/agent_metrics.py format.

Inputs: data/day7/agent_cases.json (no gold). Outputs in results/agent/:
  {config}_{split}_traces.json   — one trace per case (query_id, status, events, citations, ...)
  {config}_{split}_auto.json     — automatic numbers only (status counts, tool use, searches, tokens, time)
  {config}_{split}_reviews.json  — manual label template (created once, never overwritten)
Quality (grounded answer, citation support, abstention) needs the manual labels; see BENCHMARK.md §3.
"""
from __future__ import annotations

import json
import os
import statistics
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from . import config
from .agent import AgentConfig, GeminiSession, run_agent
from .benchmark import CASES_OUT

OUT_DIR = config.RESULTS_DIR / "agent"

AGENT_CONFIGS: dict[str, AgentConfig] = {
    "baseline": AgentConfig(
        name="baseline", method="dense", top_k=3, budget_chars=4000, max_searches=3,
        desc="Gemini GEMINI_MODEL + search_book on M1 dense (pgvector Day 6), top-3 per search, "
             "context budget 4000 chars, max 3 searches"),
    "m2_bm25": AgentConfig(
        name="m2_bm25", method="bm25", top_k=3, budget_chars=4000, max_searches=3,
        desc="Same agent, search_book on M2 BM25 (word tokens)"),
    "m3_hybrid": AgentConfig(
        name="m3_hybrid", method="hybrid", top_k=3, budget_chars=4000, max_searches=3,
        desc="Same agent, search_book on M3 hybrid RRF(dense20, bm25 20)"),
    "c1_neighbors": AgentConfig(
        name="c1_neighbors", method="dense", top_k=3, budget_chars=10000, max_searches=3, neighbors="both",
        desc="H1: baseline + previous/next chunk of the same section for every hit, budget 10000"),
    "c2_budget": AgentConfig(
        name="c2_budget", method="dense", top_k=3, budget_chars=10000, max_searches=3,
        desc="H3 / control for C1: baseline with budget 10000 only (no neighbours)"),
    "c_lite": AgentConfig(
        name="c_lite", method="dense", top_k=3, budget_chars=10000, max_searches=3, neighbors="both",
        model_env="GEMINI_MODEL_LITE",
        desc="Trade-off: C1 settings with GEMINI_MODEL_LITE (gemini-3.5-flash-lite, $0.30/$2.50 per 1M)"),
}


def _expander(cfg: AgentConfig):
    if not cfg.neighbors:
        return None
    from .eval_retrieval import neighbor_index
    return neighbor_index()


def context_evidence(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Scoring only (after the run): does the final context contain gold evidence? Answerable cases."""
    from .benchmark import QUESTIONS_OUT, evidence_hit
    from .retrievers import load_chunks

    gold = {q["id"]: q["gold"] for q in json.loads(QUESTIONS_OUT.read_text(encoding="utf-8"))}
    chunks = {c["id"]: c for c in load_chunks()}
    rows = [t for t in traces if t["query_id"] in gold]
    hits = {t["query_id"]: any(evidence_hit(chunks[i], gold[t["query_id"]]) for i in t["context_ids"])
            for t in rows}
    return {"context_evidence": f"{sum(hits.values())}/{len(rows)}",
            "context_evidence_rate": round(sum(hits.values()) / len(rows), 3) if rows else None,
            "context_evidence_miss": sorted(k for k, v in hits.items() if not v)}


# Paid tier, standard, text, USD per 1M tokens (input, output incl. thinking).
# Source: https://aistudio.google.com/docs/pricing (read 2026-11-16). gemini-3.5-flash is NOT listed
# there, so its price must come from .env (GEMINI_PRICE_IN_PER_M / GEMINI_PRICE_OUT_PER_M, e.g. from the
# billing console); otherwise cost is reported as unknown (None), never as 0.
PRICES: dict[str, tuple[float, float]] = {
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "gemini-3.1-flash-lite": (0.25, 1.50),
    "gemini-3.6-flash": (0.75, 3.75),   # through 2026-12-31; 1.50 / 7.50 from 2027-01-01
    "gemini-3.8-flash": (0.75, 3.75),   # through 2026-12-31; 1.50 / 7.50 from 2027-01-01
}


def price_per_million(model: str) -> tuple[float, float] | None:
    """(input, output) USD per 1M tokens: .env override for the model in use, else the table, else None."""
    pin, pout = os.environ.get("GEMINI_PRICE_IN_PER_M"), os.environ.get("GEMINI_PRICE_OUT_PER_M")
    if pin and pout and model == os.environ.get("GEMINI_MODEL"):
        return float(pin), float(pout)
    return PRICES.get(model)


def cost_usd(tokens: dict[str, int], model: str) -> float | None:
    """Thinking tokens are billed at the output rate. None = price unknown (not free)."""
    price = price_per_million(model)
    if price is None:
        return None
    pin, pout = price
    return round((tokens.get("input", 0) * pin + (tokens.get("output", 0) + tokens.get("thoughts", 0)) * pout)
                 / 1_000_000, 6)


def build_retriever(cfg: AgentConfig):
    from .eval_retrieval import RetrieverFactory

    return RetrieverFactory().get({"method": cfg.method, "tokenizer": cfg.tokenizer,
                                   "candidates": cfg.candidates, "rrf_k": cfg.rrf_k})


def ask(question: str, cfg: AgentConfig, filters: dict[str, Any] | None = None, retriever=None) -> dict[str, Any]:
    retriever = retriever or build_retriever(cfg)
    trace = run_agent(question, GeminiSession(cfg.model), retriever, cfg, filters=filters,
                      expander=_expander(cfg))
    trace["model"] = cfg.model
    trace["cost_usd"] = cost_usd(trace["tokens"], cfg.model)
    return trace


def load_cases(split: str, ids: list[str] | None = None) -> list[dict[str, Any]]:
    cases = [c for c in json.loads(CASES_OUT.read_text(encoding="utf-8")) if c["split"] == split]
    if ids:
        missing = set(ids) - {c["id"] for c in cases}
        if missing:
            raise SystemExit(f"unknown ids for split {split}: {sorted(missing)}")
        cases = [c for c in cases if c["id"] in ids]
    return cases


def summarize(traces: list[dict[str, Any]], cases: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [t for t in traces if t["status"] != "error"]
    searches = Counter(t["n_searches"] for t in ok)
    tok = {k: sum(t["tokens"].get(k, 0) for t in traces) for k in ("input", "output", "thoughts")}
    answerable = {c["id"]: c["answerable"] for c in cases}
    return {
        "cases": len(traces), "errors": len(traces) - len(ok),
        "status": dict(Counter(t["status"] for t in traces)),
        "tool_use": f"{sum(t['n_searches'] > 0 for t in ok)}/{len(ok)}",
        "searches_distribution": {str(k): v for k, v in sorted(searches.items())},
        "mean_searches": round(statistics.mean(t["n_searches"] for t in ok), 2) if ok else None,
        "answered_with_citation": f"{sum(t['status'] == 'answered' for t in ok)}/{len(ok)}",
        "abstain_on_unanswerable": f"{sum(t['status'] == 'abstain' for t in ok if not answerable[t['query_id']])}"
                                   f"/{sum(not answerable[t['query_id']] for t in ok)}",
        "abstain_on_answerable": f"{sum(t['status'] == 'abstain' for t in ok if answerable[t['query_id']])}"
                                 f"/{sum(answerable[t['query_id']] for t in ok)}",
        "invalid_citations_dropped": sum(len(t.get("invalid_citations", [])) for t in traces),
        **context_evidence(traces),
        "mean_context_chars": round(statistics.mean(t["context_chars"] for t in ok)) if ok else 0,
        "budget_drops": sum(len(e.get("dropped_by_budget", [])) for t in ok for e in t["events"]),
        "tokens_total": tok,
        "mean_tokens_per_case": {k: round(v / len(traces)) for k, v in tok.items()} if traces else {},
        "mean_elapsed_s": round(statistics.mean(t["elapsed_s"] for t in traces), 2) if traces else None,
        **_cost_summary(traces),
        "note": "automatic counts only; grounded answer / citation support / abstention need manual reviews",
    }


def _cost_summary(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Recompute cost from stored tokens + model so a price change applies to old traces too."""
    models = sorted({t.get("model", "") for t in traces})
    costs = [cost_usd(t["tokens"], t.get("model", "")) for t in traces]
    known = all(c is not None for c in costs)
    total = round(sum(costs), 6) if known and costs else None
    return {"cost_usd_total": total,
            "cost_usd_per_case": round(total / len(traces), 6) if total is not None and traces else None,
            "price_per_m_in_out": {m: price_per_million(m) for m in models},
            "cost_note": "paid tier; thinking billed as output" if known else
                         "price unknown for model -> set GEMINI_PRICE_IN_PER_M / GEMINI_PRICE_OUT_PER_M in .env"}


def run(split: str, name: str, *, ids: list[str] | None = None, confirm_test: bool = False) -> dict[str, Any]:
    if split == "test" and not confirm_test:
        raise SystemExit("test split is held out: choose the config on dev first, then pass --confirm-test")
    if name not in AGENT_CONFIGS:
        raise SystemExit(f"unknown agent config {name}; known: {sorted(AGENT_CONFIGS)}")
    cfg = AGENT_CONFIGS[name]
    cases = load_cases(split, ids)
    retriever = build_retriever(cfg)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{name}_{split}_traces.json"
    existing = {t["query_id"]: t for t in json.loads(path.read_text(encoding="utf-8"))} if path.exists() else {}
    for case in cases:
        trace = ask(case["question"], cfg, case.get("filter"), retriever)
        trace = {"query_id": case["id"], "split": split, "answerable": case["answerable"], **trace,
                 "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        existing[case["id"]] = trace
        print(f"{case['id']:4} {trace['status']:8} searches={trace['n_searches']} "
              f"cites={len(trace['citations'])} {trace['elapsed_s']:5.1f}s  {trace['answer'][:90]!r}")
        path.write_text(json.dumps(list(existing.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    all_cases = load_cases(split)
    traces = [existing[c["id"]] for c in all_cases if c["id"] in existing]
    for t in traces:  # refresh per-trace cost with the current price table
        t["cost_usd"] = cost_usd(t["tokens"], t.get("model", ""))
    path.write_text(json.dumps(list(existing.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"config": name, "desc": cfg.desc, "split": split, "model": cfg.model,
               "covered": f"{len(traces)}/{len(all_cases)}", **summarize(traces, all_cases),
               "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (OUT_DIR / f"{name}_{split}_auto.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                                       encoding="utf-8")
    # Manual labels: `python -m src.run review-sheet ...` then `import-reviews` (src/reviews.py).
    if split == "test":
        log = OUT_DIR / "test_runs.json"
        runs = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
        runs.append({"config": name, "ids": ids, "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        log.write_text(json.dumps(runs, indent=2) + "\n", encoding="utf-8")
    return summary
