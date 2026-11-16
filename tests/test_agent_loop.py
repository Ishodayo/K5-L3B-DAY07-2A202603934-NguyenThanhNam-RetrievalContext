"""Offline tests of the agent loop with a scripted fake model and fake retriever.

These only check control flow (tool calls, budget, stop conditions, citation parsing, errors).
They are never used as benchmark results.
"""
import json
import unittest
from pathlib import Path

from src.agent import AgentConfig, Call, Step, parse_answer, run_agent

ROOT = Path(__file__).resolve().parents[1]
CID_A = "B:doc:p061:001"
CID_B = "B:doc:p062:000"


def chunk(cid, page, text, rank):
    return {"id": cid, "text": text, "source_id": "doc", "source": "s", "page": page,
            "metadata": {"chapter_id": "ch05", "version": "v1"}, "score": 1.0 / rank, "rank": rank}


class FakeRetriever:
    method = "fake"

    def __init__(self, fail=False):
        self.calls, self.fail = [], fail

    def search(self, query, *, top_k=3, filters=None):
        self.calls.append((query, filters))
        if self.fail:
            raise ConnectionError("db down")
        return [chunk(CID_A, 61, "Floor division // rounds down.", 1),
                chunk(CID_B, 62, "Modulus % returns the remainder.", 2)][:top_k]


class ScriptedSession:
    """Plays back a list of Steps; records what the agent sent as tool results."""

    def __init__(self, steps):
        self.steps, self.sent = list(steps), []

    def first(self, user_text):
        return self.steps.pop(0)

    def tool_results(self, results):
        self.sent.append(results)
        return self.steps.pop(0)


def search(q):
    return Step("", [Call("search_book", {"query": q}, "id1")], {"input": 10, "output": 2})


CFG = AgentConfig(name="t", top_k=2, budget_chars=10_000, max_searches=2)


class ParseAnswerTest(unittest.TestCase):
    def test_valid_invalid_and_abstain(self):
        p = parse_answer(f"It rounds down [{CID_A}] and [B:doc:p999:000].", [CID_A])
        self.assertEqual((p["status"], p["citations"], p["invalid_citations"]),
                         ("answered", [CID_A], ["B:doc:p999:000"]))
        self.assertEqual(parse_answer("No citation here.", [CID_A])["reason"], "invalid_or_missing_citations")
        self.assertEqual(parse_answer("INSUFFICIENT_EVIDENCE: not in book", [CID_A])["status"], "abstain")


class RunAgentTest(unittest.TestCase):
    def test_search_then_answer_with_citation(self):
        session = ScriptedSession([search("floor division"), Step(f"It rounds down [{CID_A}].", [])])
        r = FakeRetriever()
        t = run_agent("What does // do?", session, r, CFG, filters={"chapter_id": "ch05"})
        self.assertEqual(t["status"], "answered")
        self.assertEqual(t["citations"], [CID_A])
        self.assertEqual(r.calls, [("floor division", {"chapter_id": "ch05"})])  # filter from caller
        self.assertEqual(t["n_searches"], 1)
        self.assertEqual(t["context_ids"], [CID_A, CID_B])
        self.assertEqual(t["tokens"]["input"], 10)
        self.assertIn(CID_A, session.sent[0][0][1]["passages"])

    def test_search_limit_then_abstain(self):
        session = ScriptedSession([search("a"), search("b"), search("c"),
                                   Step("INSUFFICIENT_EVIDENCE: nothing", [])])
        t = run_agent("q", session, FakeRetriever(), CFG, max_turns=10)
        self.assertEqual(t["n_searches"], 2)
        self.assertIn("search_limit", [e["event"] for e in t["events"]])
        self.assertEqual(t["status"], "abstain")

    def test_duplicate_chunks_not_resent_and_budget(self):
        small = AgentConfig(name="t", top_k=2, budget_chars=90, max_searches=3)
        session = ScriptedSession([search("a"), search("a again"), Step(f"x [{CID_A}]", [])])
        t = run_agent("q", session, FakeRetriever(), small)
        first, second = [e for e in t["events"] if e["event"] == "search"]
        self.assertEqual(first["added_to_context"], [CID_A])
        self.assertEqual(first["dropped_by_budget"], [CID_B])
        self.assertEqual(second["added_to_context"], [])
        self.assertLessEqual(t["context_chars"], 90)

    def test_answer_without_search_citations_is_abstain(self):
        t = run_agent("q", ScriptedSession([Step(f"Guess [{CID_A}].", [])]), FakeRetriever(), CFG)
        self.assertEqual((t["status"], t["invalid_citations"]), ("abstain", [CID_A]))

    def test_retriever_error_is_reported(self):
        t = run_agent("q", ScriptedSession([search("a")]), FakeRetriever(fail=True), CFG)
        self.assertEqual(t["status"], "error")
        self.assertIn("db down", t["error"])

    def test_trace_fits_starter_agent_metrics(self):
        import sys
        sys.path.insert(0, str(ROOT / "starter"))
        from agent_metrics import aggregate
        t = run_agent("q", ScriptedSession([search("a"), Step(f"x [{CID_A}]", [])]), FakeRetriever(), CFG)
        t["query_id"] = "c1"
        out = aggregate([{"id": "c1", "answerable": True}], [t],
                        [{"query_id": "c1", "answer_grade": 2, "citation_support": [True]}])
        self.assertEqual(out["tool_use"], {"n": 1, "N": 1})
        self.assertEqual(out["citation_validity"], {"n": 1, "N": 1})
        json.dumps(t)  # trace must be JSON serialisable


if __name__ == "__main__":
    unittest.main()
