"""Offline test of the Day 6 -> Day 7 field mapping (no database, no model)."""
import unittest

from src.day6_store import to_day7


class Day6AdapterTest(unittest.TestCase):
    def test_maps_fields_to_day7_contract(self):
        row = {"chunk_id": "B:thinkpython2:p061:000", "text": "The floor division operator, //, ...",
               "document_id": "thinkpython2", "source": "data/thinkpython2.pdf", "page": 61,
               "chapter_id": "ch05", "chapter_title": "Conditionals and recursion",
               "section": "5.1 Floor division and modulus", "metadata": {"content_hash": "abc"}}
        c = to_day7(row, "B")
        self.assertEqual(set(c), {"id", "text", "source_id", "source", "page", "metadata"})
        self.assertEqual(c["id"], "B:thinkpython2:p061:000")
        self.assertEqual(c["source_id"], "thinkpython2")
        self.assertEqual(c["page"], 61)
        self.assertEqual(c["metadata"]["chapter_id"], "ch05")
        self.assertEqual(c["metadata"]["strategy"], "B")
        self.assertEqual(c["metadata"]["content_hash"], "abc")
        self.assertNotIn("version", c["metadata"])

    def test_adds_document_version_from_sources(self):
        row = {"chunk_id": "B:d:p001:000", "text": "t", "document_id": "d", "source": "s", "page": 1,
               "chapter_id": "ch01", "chapter_title": "x", "section": None, "metadata": {}}
        sources = {"d": {"version": "2nd Edition", "pdf_sha256": "ff", "accessed_at": "2026-11-14"}}
        meta = to_day7(row, "B", sources)["metadata"]
        self.assertEqual((meta["version"], meta["pdf_sha256"], meta["accessed_at"]),
                         ("2nd Edition", "ff", "2026-11-14"))
        with self.assertRaises(KeyError):
            to_day7(row | {"document_id": "unknown"}, "B", sources)

    def test_real_sources_file_has_version_fields(self):
        from src import config
        doc = config.load_sources()["thinkpython2"]
        for key in config.VERSION_FIELDS:
            self.assertTrue(doc[key])


if __name__ == "__main__":
    unittest.main()
