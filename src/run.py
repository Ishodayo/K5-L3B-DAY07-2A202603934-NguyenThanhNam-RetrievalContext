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

    p = sub.add_parser("build-benchmark", help="Day 6 questions + unanswerable -> data/day7 JSON")
    p.set_defaults(func=cmd_build_benchmark)

    p = sub.add_parser("verify-benchmark", help="check counts, evidence, filters, split, absence")
    p.set_defaults(func=cmd_verify_benchmark)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
