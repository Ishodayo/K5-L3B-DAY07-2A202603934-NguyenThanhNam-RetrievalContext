"""Offline tests for the advanced pipeline helpers (no PDF, model or database needed)."""
import json
import unittest

from src.advanced import ingest as I


class TableHeaderTest(unittest.TestCase):
    ROWS = [["", "Total population (000s)", "", "", "Life expectancy", "", ""],
            ["Data type", "Comparable estimates", "", "", "Comparable estimates", "", ""],
            ["", "Male", "Female", "Both sexes", "Male", "Female", "Both sexes"],
            ["Countries and area", "2021", "", "", "2019", "", ""],
            ["Viet Nam", "48 136", "49 332", "97 468", "69.6", "78.1", "73.7"]]

    def test_split_and_labels(self):
        head, data = I._split_header(self.ROWS)
        self.assertEqual(len(head), 4)
        self.assertEqual(data[0][0], "Viet Nam")
        labels = I._labels(head, 7, True)
        self.assertEqual(labels[0], "Country/area")
        self.assertEqual(labels[3], "Total population (000s) | Comparable estimates | Both sexes | 2021")
        self.assertEqual(labels[6], "Life expectancy | Comparable estimates | Both sexes | 2019")

    def test_no_year_row_raises(self):
        with self.assertRaises(ValueError):
            I._split_header([["a", "b"], ["c", "d"]])


class VisualChunkTest(unittest.TestCase):
    def test_split_by_figure_and_length_keeps_title(self):
        long = "\n".join(f"- value {i}: {'x' * 60}" for i in range(60))
        cache = {"p019": {"page": 19, "model": "m", "dpi": 150,
                          "text": f"## Figure 1.4: Trends\n{long}\n## Figure 1.5: Deaths\n- a: 1"}}
        chunks = I.visual_chunks(cache, {19: "1.1 Trends"})
        self.assertTrue(all(c["metadata"]["kind"] == "visual" and c["page"] == 19 for c in chunks))
        self.assertTrue(all(len(c["text"]) <= I.MAX_CHARS + 200 for c in chunks))
        self.assertTrue(any("(continued)" in c["text"] for c in chunks))
        self.assertEqual(chunks[-1]["metadata"]["figure"], "Figure 1.5: Deaths")
        self.assertEqual(len({c["id"] for c in chunks}), len(chunks))


class BenchmarkFileTest(unittest.TestCase):
    def test_counts_and_no_gold_in_cases(self):
        q_path, c_path = I.ADV_DIR / "questions.json", I.ADV_DIR / "cases.json"
        if not q_path.exists() or not c_path.exists():
            self.skipTest("advanced benchmark not built")
        qs = json.loads(q_path.read_text(encoding="utf-8"))
        test = [q for q in qs if q["split"] == "test"]
        self.assertGreaterEqual(len(test), 30)
        self.assertGreaterEqual(sum(q["answerable"] for q in test), 24)
        for c in json.loads(c_path.read_text(encoding="utf-8")):
            self.assertFalse({"expected_answer", "evidence", "absence_check"} & set(c))


if __name__ == "__main__":
    unittest.main()
