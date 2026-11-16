"""Build the dev/test comparison table: retrieval metrics (original query) + agent metrics + labels.

Reads results/retrieval/summary_{split}.json, results/agent/{cfg}_{split}_auto.json and, when present,
results/agent/{cfg}_{split}_metrics.json (starter/agent_metrics.py output from manual labels).
Writes results/compare_{split}.csv/.json.
"""
from __future__ import annotations

import csv
import json
from typing import Any

from . import config

# agent config -> retrieval config with the same retrieval/context settings (original question, 1 search)
RETRIEVAL_OF = {"baseline": "dense", "m2_bm25": "bm25", "m3_hybrid": "hybrid",
                "c1_neighbors": "dense_nb2", "c2_budget": "dense_8k", "c_lite": "dense_nb2"}


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _frac(s: str) -> tuple[int, int]:
    n, d = s.split("/")
    return int(n), int(d)


def select(names: list[str]) -> dict[str, Any]:
    """Apply the selection rule fixed before test (benchmark/README.md) to the dev comparison."""
    from datetime import datetime, timezone

    rows = {r["config"]: r for r in build("dev", names)}
    missing = [n for n in names if n not in rows or rows[n]["grounded_mean"] is None]
    if missing:
        raise SystemExit(f"need agent runs + imported labels for: {missing}")
    steps, cand = [], list(rows)
    ctx = {n: _frac(rows[n]["agent_ctx"])[0] for n in cand}
    best = max(ctx.values())
    cand = [n for n in cand if best - ctx[n] <= 1]
    steps.append(f"1) Context Evidence Rate (agent) dev: {ctx}; best={best}, tie if <= 1 question -> {cand}")
    g = {n: rows[n]["grounded_mean"] for n in cand}
    best = max(g.values())
    cand = [n for n in cand if best - g[n] <= 0.1 + 1e-9]
    steps.append(f"2) Grounded mean /2: {g}; best={best}, tie if <= 0.1 -> {cand}")
    ab = {n: (_frac(rows[n]["abstention"]), _frac(rows[n]["false_abstention"])[0]) for n in cand}
    min_false = min(v[1] for v in ab.values())
    cand = [n for n in cand if ab[n][0][0] == ab[n][0][1] and ab[n][1] == min_false]
    steps.append(f"3) Abstention all correct and fewest false abstentions: "
                 f"{ {n: f'{v[0][0]}/{v[0][1]}, false {v[1]}' for n, v in ab.items()} } -> {cand}")
    cost = {n: rows[n]["cost_usd_per_case"] for n in cand}
    chosen = min(cand, key=lambda n: (cost[n], rows[n]["mean_searches"]))
    steps.append(f"4) Cost per case (USD): {cost} -> {chosen}")
    return {"selected_config": chosen, "baseline_config": "baseline",
            "decided_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "based_on": "dev only; rule fixed in benchmark/README.md (commit 88e0d72) before any Day 7 run",
            "steps": steps, "dev_rows": [rows[n] for n in names], "test_runs": []}


def build(split: str, names: list[str]) -> list[dict[str, Any]]:
    retr = {s["config"]: s for s in (_load(config.RESULTS_DIR / "retrieval" / f"summary_{split}.json") or [])}
    rows = []
    for name in names:
        auto = _load(config.RESULTS_DIR / "agent" / f"{name}_{split}_auto.json")
        if auto is None:
            continue
        met = _load(config.RESULTS_DIR / "agent" / f"{name}_{split}_metrics.json")
        rname = RETRIEVAL_OF.get(name) or auto.get("retrieval_config")
        r = retr.get(rname, {})
        g = (met or {}).get("grounded_answer", {})
        row = {
            "config": name, "model": auto["model"], "desc": auto["desc"],
            "retrieval_cfg": rname, "hit1": r.get("hit1"), "hit3": r.get("hit3"),
            "retrieval_ctx": r.get("context_evidence"),
            "agent_ctx": auto.get("context_evidence"), "agent_ctx_miss": ",".join(auto.get("context_evidence_miss", [])),
            "grounded_0/1/2": f"{g.get('0')}/{g.get('1')}/{g.get('2')}" if met else "chưa chấm",
            "grounded_mean": g.get("mean") if met else None,
            "citation_valid": f"{met['citation_validity']['n']}/{met['citation_validity']['N']}" if met else None,
            "answer_with_citation": (f"{met['answer_citation_coverage']['n']}/{met['answer_citation_coverage']['N']}"
                                     if met else auto.get("answered_with_citation")),
            "abstention": f"{met['abstention']['n']}/{met['abstention']['N']}" if met else auto.get("abstain_on_unanswerable"),
            "false_abstention": (f"{met['false_abstention']['n']}/{met['false_abstention']['N']}"
                                 if met else auto.get("abstain_on_answerable")),
            "tool_use": auto["tool_use"], "mean_searches": auto["mean_searches"],
            "errors": auto["errors"], "mean_context_chars": auto.get("mean_context_chars"),
            "mean_tokens_in": auto["mean_tokens_per_case"].get("input"),
            "mean_tokens_out+think": (auto["mean_tokens_per_case"].get("output", 0)
                                      + auto["mean_tokens_per_case"].get("thoughts", 0)),
            "mean_elapsed_s": auto["mean_elapsed_s"],
            "cost_usd_total": auto.get("cost_usd_total"), "cost_usd_per_case": auto.get("cost_usd_per_case"),
        }
        rows.append(row)
    out = config.RESULTS_DIR / f"compare_{split}"
    out.with_suffix(".json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if rows:
        with out.with_suffix(".csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    return rows
