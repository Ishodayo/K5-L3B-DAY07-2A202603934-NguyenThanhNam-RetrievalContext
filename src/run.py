"""Day 7 command line. Run from the repo root: .\\.venv\\Scripts\\python -m src.run <command>."""
from __future__ import annotations

import argparse
import json
import sys
import time

from . import config


def cmd_info(args: argparse.Namespace) -> int:
    from .day6_store import DenseRetriever

    info = DenseRetriever(strategy=args.strategy).info()
    print(json.dumps(info, ensure_ascii=False, indent=2))
    if args.save:
        out = config.RESULTS_DIR / "day6_connection.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"saved {out.relative_to(config.ROOT)}")
    return 0


def cmd_export_chunks(args: argparse.Namespace) -> int:
    from .day6_store import export_chunks

    out = config.ROOT / args.out
    n = export_chunks(config.database_url(), args.strategy, out)
    print(f"exported {n} chunks (strategy {args.strategy}) -> {out.relative_to(config.ROOT)}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    from .eval_retrieval import RetrieverFactory

    retriever = RetrieverFactory().get({"method": args.method, "tokenizer": args.tokenizer})
    filters = {"chapter_id": args.chapter} if args.chapter else None
    started = time.perf_counter()
    results = retriever.search(args.query, top_k=args.top_k, filters=filters)
    elapsed = (time.perf_counter() - started) * 1000
    print(f"method={args.method} top_k={args.top_k} filter={filters} query_ms={elapsed:.0f}")
    for r in results:
        text = " ".join(r["text"].split())
        print(f"#{r['rank']} {r['score']:.4f} {r['id']} page={r['page']} "
              f"{r['metadata']['chapter_id']} | {text[:110]}")
    return 0


def cmd_retrieval_eval(args: argparse.Namespace) -> int:
    from .eval_retrieval import OUT_DIR, run

    summaries = run(args.split, [n.strip() for n in args.configs.split(",") if n.strip()],
                    confirm_test=args.confirm_test)
    cols = ["config", "N", "errors", "hit1", "hit3", "context_evidence", "mrr10", "median_ms",
            "mean_context_tokens_est", "mean_context_chunks", "setup_seconds"]
    print(" | ".join(cols))
    for s in summaries:
        print(" | ".join(str(s[c]) for c in cols))
    print(f"traces + summary -> {OUT_DIR.relative_to(config.ROOT)}")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    from .eval_agent import AGENT_CONFIGS, ask

    cfg = AGENT_CONFIGS[args.config]
    filters = {"chapter_id": args.chapter} if args.chapter else None
    t = ask(args.question, cfg, filters)
    for e in t["events"]:
        if e["event"] == "search":
            print(f"search[{e['method']}] {e['query']!r} -> "
                  + ", ".join(f"p{r['page']}" for r in e["results"]) + f" | +ctx {len(e['added_to_context'])}")
        else:
            print(e["event"], e.get("error", ""))
    print(f"\nstatus={t['status']} reason={t['reason']} model={t['model']} searches={t['n_searches']} "
          f"model_calls={t['n_model_calls']} tokens={t['tokens']} time={t['elapsed_s']}s cost=${t['cost_usd']}")
    print(f"citations={t['citations']} invalid={t['invalid_citations']}")
    print("\n" + (t["answer"] or t.get("error", "")))
    if args.save:
        out = config.RESULTS_DIR / "agent" / "ask_examples.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        rows = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
        rows.append(t)
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nsaved -> {out.relative_to(config.ROOT)}")
    return 0 if t["status"] != "error" else 1


def cmd_agent_eval(args: argparse.Namespace) -> int:
    from .eval_agent import run

    ids = [i.strip() for i in args.ids.split(",")] if args.ids else None
    summary = run(args.split, args.config, ids=ids, confirm_test=args.confirm_test)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def cmd_review_sheet(args: argparse.Namespace) -> int:
    from .reviews import export_sheet

    from .reviews import export_context_sheet

    for name in args.configs.split(","):
        md, csv_path = export_sheet(name.strip(), args.split)
        print(f"read  {md.relative_to(config.ROOT)}\nfill  {csv_path.relative_to(config.ROOT)}")
        if args.context:
            md, csv_path = export_context_sheet(name.strip(), args.split)
            print(f"read  {md.relative_to(config.ROOT)}\nfill  {csv_path.relative_to(config.ROOT)}")
    return 0


def cmd_import_reviews(args: argparse.Namespace) -> int:
    from .reviews import AGENT_DIR, import_context, import_reviews

    for name in args.configs.split(","):
        if (AGENT_DIR / f"{name.strip()}_{args.split}_context_review.csv").exists():
            c = import_context(name.strip(), args.split)
            print(f"{name}: context 0/1/2 = {c['counts']['0']}/{c['counts']['1']}/{c['counts']['2']} "
                  f"(graded {c['graded']}) mean={c['mean']}")
        r = import_reviews(name.strip(), args.split)
        g = r["grounded_answer"]
        print(f"{name}: grounded 0/1/2 = {g['0']}/{g['1']}/{g['2']} mean={g['mean']} | citation "
              f"{r['citation_validity']['n']}/{r['citation_validity']['N']} | abstention "
              f"{r['abstention']['n']}/{r['abstention']['N']} | false abstention "
              f"{r['false_abstention']['n']}/{r['false_abstention']['N']}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    from .compare import build

    rows = build(args.split, [n.strip() for n in args.configs.split(",")])
    cols = ["config", "hit1", "hit3", "retrieval_ctx", "agent_ctx", "context_0/1/2", "grounded_0/1/2",
            "grounded_mean", "citation_valid", "abstention", "false_abstention", "mean_searches",
            "mean_elapsed_s", "cost_usd_total"]
    print(" | ".join(cols))
    for r in rows:
        print(" | ".join(str(r[c]) for c in cols))
    print(f"-> results/compare_{args.split}.csv")
    return 0


def cmd_select(args: argparse.Namespace) -> int:
    from .compare import select

    out = config.RESULTS_DIR / "selection.json"
    if out.exists() and not args.overwrite:
        raise SystemExit("results/selection.json already exists (use --overwrite only before running test)")
    sel = select([n.strip() for n in args.configs.split(",")])
    out.write_text(json.dumps(sel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n".join(sel["steps"]))
    print(f"SELECTED: {sel['selected_config']} -> {out.relative_to(config.ROOT)}")
    return 0


def cmd_build_benchmark(args: argparse.Namespace) -> int:
    from . import benchmark as bm

    questions, cases = bm.build(bm.load_chunks())
    bm.write_json(bm.QUESTIONS_OUT, questions)
    bm.write_json(bm.CASES_OUT, cases)
    print(f"{len(questions)} answerable -> {bm.QUESTIONS_OUT.relative_to(config.ROOT)}; "
          f"{len(cases)} cases -> {bm.CASES_OUT.relative_to(config.ROOT)}")
    return 0


def cmd_verify_benchmark(args: argparse.Namespace) -> int:
    from . import benchmark as bm

    chunks = bm.load_chunks()
    questions = json.loads(bm.QUESTIONS_OUT.read_text(encoding="utf-8"))
    cases = json.loads(bm.CASES_OUT.read_text(encoding="utf-8"))
    report = bm.verify(chunks, questions, cases)
    for row in report["evidence"]:
        print(f"{'OK ' if row['chunks'] and row['exact'] else 'ERR'} {row['id']:4} p{row['page']:03d} "
              f"{', '.join(row['chunks'])}")
    for row in report["absence"]:
        print(f"{'OK ' if not row['matches'] else 'ERR'} {row['id']:4} absent: {len(row['matches'])} matches "
              f"for {len(row['patterns'])} patterns")
    summary = {k: v for k, v in report.items() if k not in ("evidence", "absence")}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    out = config.RESULTS_DIR / "benchmark_verify.json"
    bm.write_json(out, report)
    print(f"saved {out.relative_to(config.ROOT)}")
    print("RESULT:", "all checks passed" if not report["problems"] else f"{len(report['problems'])} problem(s)")
    return 0 if not report["problems"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m src.run", description="Day 7 Agentic RAG")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("info", help="check Day 6 index + embedding compatibility")
    p.add_argument("--strategy", default=config.DAY6_STRATEGY)
    p.add_argument("--save", action="store_true", help="write results/day6_connection.json")
    p.set_defaults(func=cmd_info)

    p = sub.add_parser("export-chunks", help="export Day 6 chunks to the Day 7 JSON schema")
    p.add_argument("--strategy", default=config.DAY6_STRATEGY)
    p.add_argument("--out", default="data/day7/chunks.json")
    p.set_defaults(func=cmd_export_chunks)

    p = sub.add_parser("search", help="run one retrieval query")
    p.add_argument("query")
    p.add_argument("--method", default="dense", choices=["dense", "bm25", "hybrid"])
    p.add_argument("--top-k", type=int, default=3)
    p.add_argument("--chapter", help="chapter_id filter, e.g. ch14 (only when given by the user)")
    p.add_argument("--tokenizer", default="word", choices=["word", "code"], help="BM25 tokenizer")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("retrieval-eval", help="Hit@1/Hit@3/Context Evidence Rate per config on a split")
    p.add_argument("--split", choices=["dev", "test"], required=True)
    p.add_argument("--configs", default="dense,bm25,hybrid", help="comma-separated names from CONFIGS")
    p.add_argument("--confirm-test", action="store_true", help="required for test (after choosing on dev)")
    p.set_defaults(func=cmd_retrieval_eval)

    p = sub.add_parser("ask", help="ask the agent one question (real Gemini + retriever)")
    p.add_argument("question")
    p.add_argument("--config", default="baseline")
    p.add_argument("--chapter", help="user-provided chapter_id scope, e.g. ch14")
    p.add_argument("--save", action="store_true", help="append the trace to results/agent/ask_examples.json")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("agent-eval", help="run the agent on a split, save traces + review template")
    p.add_argument("--split", choices=["dev", "test"], required=True)
    p.add_argument("--config", default="baseline")
    p.add_argument("--ids", help="comma-separated subset of case ids")
    p.add_argument("--confirm-test", action="store_true")
    p.set_defaults(func=cmd_agent_eval)

    p = sub.add_parser("review-sheet", help="write .md to read + blank .csv to fill for manual labels")
    p.add_argument("--split", choices=["dev", "test"], required=True)
    p.add_argument("--configs", default="baseline")
    p.add_argument("--context", action="store_true", help="also write the context 0/1/2 sheet (BENCHMARK §2)")
    p.set_defaults(func=cmd_review_sheet)

    p = sub.add_parser("import-reviews", help="filled .csv -> reviews.json -> agent metrics")
    p.add_argument("--split", choices=["dev", "test"], required=True)
    p.add_argument("--configs", default="baseline")
    p.set_defaults(func=cmd_import_reviews)

    p = sub.add_parser("compare", help="comparison table of agent configs (retrieval + agent + labels)")
    p.add_argument("--split", choices=["dev", "test"], required=True)
    p.add_argument("--configs", default="baseline,m2_bm25,m3_hybrid,c1_neighbors,c2_budget,c_lite")
    p.set_defaults(func=cmd_compare)

    p = sub.add_parser("select", help="apply the pre-registered selection rule on dev -> results/selection.json")
    p.add_argument("--configs", default="baseline,m2_bm25,m3_hybrid,c1_neighbors,c2_budget,c_lite")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_select)

    p = sub.add_parser("build-benchmark", help="Day 6 questions + unanswerable -> data/day7 JSON")
    p.set_defaults(func=cmd_build_benchmark)

    p = sub.add_parser("verify-benchmark", help="check counts, evidence, filters, split, absence")
    p.set_defaults(func=cmd_verify_benchmark)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
