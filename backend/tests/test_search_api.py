"""The search endpoint, on a small index built from test documents by the real pipeline builder.

Building it with pipeline/build_search_index.py, not by hand, keeps the file the pipeline writes
and the file the API reads in step. The sample documents are Word and PowerPoint only, so these
checks need no PDF library. Run from backend/: python -m unittest discover -s tests -v
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import search
from main import app

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "pipeline"), str(ROOT / "pipeline" / "tests")]
import build_search_index  # noqa: E402
from sample_documents import write_samples  # noqa: E402

client = TestClient(app)


def record(accession: str) -> dict:
    path = ROOT / "backend" / "data" / "investigations" / f"{accession}.json"
    return json.loads(path.read_text(encoding="utf-8"))


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = Path(tempfile.mkdtemp())
        cls.saved = search.INDEX
        search.INDEX = folder / "search.sqlite"
        rows = write_samples(str(folder / "cache"), with_pdfs=False)
        build_search_index.build(rows, str(folder / "cache"), str(search.INDEX))

    @classmethod
    def tearDownClass(cls):
        search.INDEX = cls.saved

    def get(self, **params):
        return client.get("/api/search", params=params)

    def test_hit_carries_title_acronym_doi_file_and_page(self):
        body = self.get(q="PMMA").json()
        self.assertEqual(body["total"], 1)
        hit, psi25 = body["items"][0], record("PSI-25")
        self.assertEqual((hit["accession"], hit["title"], hit["investigationAcronym"], hit["doi"]),
                         ("PSI-25", psi25["title"], psi25["investigationAcronym"], psi25["doi"]))
        self.assertEqual(hit["file_name"], "PSI-25_Science Documents_Fixture ReadMe.docx")
        self.assertIsNone(hit["page"])
        self.assertIn("[[PMMA]]", hit["snippet"])
        self.assertIn("2 cm wide", hit["text"])

    def test_a_question_matches_on_any_of_its_words(self):
        body = self.get(q="What did the cotton flames do?").json()
        hits = [(h["accession"], h["page"]) for h in body["items"]]
        # The slide matching "cotton" and "flames" ranks above the readme that only has "the".
        self.assertEqual(hits, [("PSI-98", 2), ("PSI-25", None)])

    def test_paging_and_total(self):
        body = self.get(q="fixture", limit=1, offset=1).json()
        self.assertEqual((body["total"], body["limit"], body["offset"], len(body["items"])), (4, 1, 1, 1))

    def test_accession_filter(self):
        items = self.get(q="fixture", accession="PSI-98").json()["items"]
        self.assertEqual({h["accession"] for h in items}, {"PSI-98"})
        self.assertEqual(self.get(q="fixture", accession="PSI-999").status_code, 404)

    def test_no_match_is_empty_not_an_error(self):
        body = self.get(q="zirconium").json()
        self.assertEqual((body["total"], body["items"]), (0, []))

    def test_query_syntax_cannot_break_the_search(self):
        for q in ['pmma" OR NEAR(', "AND OR NOT", "flame*", "-cotton"]:
            self.assertEqual(self.get(q=q).status_code, 200, q)

    def test_queries_without_words_are_refused(self):
        self.assertEqual(self.get(q="").status_code, 422)
        self.assertEqual(self.get(q="?! …").status_code, 422)

    def test_missing_index_is_a_clear_503(self):
        built, search.INDEX = search.INDEX, search.INDEX.with_name("absent.sqlite")
        try:
            response = self.get(q="pmma")
        finally:
            search.INDEX = built
        self.assertEqual(response.status_code, 503)
        self.assertIn("build_search_index", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
