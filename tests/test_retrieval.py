"""Offline tests for BM25, RRF fusion, context packing and per-question metrics.

The fake retriever below only tests code paths; it is never used for reported results.
"""
import unittest

from src.context import pack_context
from src.eval_retrieval import evaluate_question
from src.retrievers import BM25Retriever, HybridRetriever, rrf_fuse, tokenize


def chunk(cid, text, page=1, chapter="ch01"):
    return {"id": cid, "text": text, "source_id": "doc", "source": "s", "page": page,
            "metadata": {"chapter_id": chapter}}


CHUNKS = [chunk("a", "The floor division operator // divides and rounds down", 61, "ch05"),
          chunk("b", "Lists are mutable sequences of values", 111, "ch10"),
          chunk("c", "Dictionaries map keys to values; a list cannot be a key", 130, "ch11")]


class TokenizeTest(unittest.TestCase):
    def test_word_mode_drops_operators_code_mode_keeps_them(self):
        self.assertNotIn("//", tokenize("What does // do?"))
        self.assertIn("//", tokenize("What does // do?", "code"))
        self.assertNotIn("?", tokenize("What does // do?", "code"))


class BM25Test(unittest.TestCase):
    def test_ranks_and_filters(self):
        bm = BM25Retriever(CHUNKS)
        res = bm.search("can a list be a dictionary key", top_k=3)
        self.assertEqual(res[0]["id"], "c")
        self.assertEqual([r["rank"] for r in res], list(range(1, len(res) + 1)))
        self.assertTrue(all(r["metadata"]["chapter_id"] == "ch10"
                            for r in bm.search("list values", top_k=3, filters={"chapter_id": "ch10"})))

    def test_no_query_terms_returns_empty(self):
        self.assertEqual(BM25Retriever(CHUNKS).search("//", top_k=3), [])


class FakeRetriever:
    method = "fake"

    def __init__(self, order):
        self.order = order

    def search(self, query, *, top_k=3, filters=None):
        by_id = {c["id"]: c for c in CHUNKS}
        return [{**by_id[i], "score": 1.0 / r, "rank": r, "method": self.method}
                for r, i in enumerate(self.order[:top_k], 1)]


class FusionTest(unittest.TestCase):
    def test_rrf_prefers_items_ranked_high_by_both(self):
        fused = rrf_fuse([FakeRetriever(["a", "b", "c"]).search("q"), FakeRetriever(["b", "c", "a"]).search("q")],
                         top_k=3)
        self.assertEqual(fused[0]["id"], "b")
        self.assertEqual(fused[0]["component_ranks"], {"fake": 1})  # same method name collapses
        hybrid = HybridRetriever([FakeRetriever(["a", "b"]), FakeRetriever(["b", "a"])], candidates=2)
        self.assertEqual(len(hybrid.search("q", top_k=1)), 1)


class ContextTest(unittest.TestCase):
    def test_dedup_budget_and_headers(self):
        ctx, ids = pack_context([CHUNKS[0], CHUNKS[0], CHUNKS[1]], budget_chars=10_000)
        self.assertEqual(ids, ["a", "b"])
        self.assertIn("[a | doc", ctx)
        ctx, ids = pack_context(CHUNKS, budget_chars=90)
        self.assertEqual(ids, ["a"])
        self.assertLessEqual(len(ctx), 90)


class NeighborTest(unittest.TestCase):
    def test_expands_within_same_section_only(self):
        from src.context import NeighborIndex
        mk = lambda cid, page, sec: {**chunk(cid, "t " + cid, page), "metadata": {"section": sec}}
        idx = NeighborIndex([mk("p1:000", 1, "A"), mk("p1:001", 1, "B"), mk("p2:000", 2, "B"), mk("p3:000", 3, "C")])
        hit = {**mk("p1:001", 1, "B"), "rank": 1, "score": 0.9}
        self.assertEqual([c["id"] for c in idx.expand([hit], "next")], ["p1:001", "p2:000"])
        self.assertEqual([c["id"] for c in idx.expand([hit], "both")], ["p1:001", "p2:000"])  # p1:000 other section
        last = {**mk("p2:000", 2, "B"), "rank": 1, "score": 0.5}
        out = idx.expand([last], "both")
        self.assertEqual([c["id"] for c in out], ["p1:001", "p2:000"])
        self.assertEqual(out[0]["neighbor_of"], "p2:000")


class MetricTest(unittest.TestCase):
    Q = {"id": "q", "split": "dev", "question": "what does // do",
         "gold": [{"source_id": "doc", "page": 61, "evidence": "rounds  down"}]}
    CFG = {"method": "fake", "top_k": 3, "budget_chars": 10_000}

    def test_hit_at_rank_two(self):
        t = evaluate_question(self.Q, FakeRetriever(["b", "a", "c"]), self.CFG)
        self.assertEqual((t["hit1"], t["hit3"], t["rr"], t["context_hit"]), (False, True, 0.5, True))

    def test_error_is_recorded_as_miss(self):
        class Broken:
            def search(self, *a, **k):
                raise ConnectionError("db down")
        t = evaluate_question(self.Q, Broken(), self.CFG)
        self.assertEqual(t["status"], "error")
        self.assertFalse(t["hit3"])


if __name__ == "__main__":
    unittest.main()
