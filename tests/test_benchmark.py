"""Offline tests for benchmark helpers and the committed benchmark files."""
import json
import unittest

from src import benchmark as bm


class MatchingTest(unittest.TestCase):
    def test_match_key_ignores_whitespace_case_and_eol_hyphen(self):
        self.assertEqual(bm.match_key("The floor\n division  Oper-\nator"), "thefloordivisionoperator")

    def test_exact_span_recovers_original_text(self):
        text = "Intro. These errors are also called\nexceptions because they happen."
        span = bm.exact_span(text, "These errors are also called exceptions")
        self.assertEqual(span, "These errors are also called\nexceptions")
        self.assertIn(span, text)
        self.assertIsNone(bm.exact_span(text, "not in the text"))

    def test_evidence_hit_needs_same_source_and_page(self):
        chunk = {"source_id": "s", "page": 3, "text": "a  b c"}
        self.assertTrue(bm.evidence_hit(chunk, [{"source_id": "s", "page": 3, "evidence": "ab c"}]))
        self.assertFalse(bm.evidence_hit(chunk, [{"source_id": "s", "page": 4, "evidence": "ab c"}]))


class CommittedBenchmarkTest(unittest.TestCase):
    def setUp(self):
        if not bm.QUESTIONS_OUT.exists() or not bm.CASES_OUT.exists() or not bm.CHUNKS.exists():
            self.skipTest("run export-chunks and build-benchmark first")
        self.chunks = bm.load_chunks()
        self.questions = json.loads(bm.QUESTIONS_OUT.read_text(encoding="utf-8"))
        self.cases = json.loads(bm.CASES_OUT.read_text(encoding="utf-8"))

    def test_verify_has_no_problems(self):
        report = bm.verify(self.chunks, self.questions, self.cases)
        self.assertEqual(report["problems"], [])

    def test_agent_cases_contain_no_gold(self):
        for c in self.cases:
            self.assertFalse({"gold", "expected_answer", "evidence"} & set(c), c["id"])


if __name__ == "__main__":
    unittest.main()
