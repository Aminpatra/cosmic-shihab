"""Checks for build_search_index.py on the small sample documents. No network.

    python3 -m unittest discover -s pipeline/tests -v

The PDF checks need pypdf (pipeline/requirements.txt) and are skipped without it.

SI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

import importlib.util
import os
import sqlite3
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import build_search_index as bsi  # noqa: E402
from sample_documents import write_samples  # noqa: E402

HAVE_PYPDF = importlib.util.find_spec("pypdf") is not None


def build(with_pdfs):
    folder = tempfile.mkdtemp()
    cache, out = os.path.join(folder, "cache"), os.path.join(folder, "search.sqlite")
    counts = bsi.build(write_samples(cache, with_pdfs), cache, out)
    return counts, out


def query(out, sql, *args):
    db = sqlite3.connect(out)
    try:
        return db.execute(sql, args).fetchall()
    finally:
        db.close()


def match(out, terms):
    return query(out, "SELECT d.accession, d.file_name, passages.page FROM passages "
                      "JOIN documents d USING (file_id) WHERE passages MATCH ? ORDER BY bm25(passages)",
                 terms)


class WithoutPdfs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.counts, cls.out = build(with_pdfs=False)

    def test_every_document_is_listed_with_its_status(self):
        rows = dict(query(self.out, "SELECT file_id, status FROM documents"))
        self.assertEqual(rows, {"fixture-docx": "indexed", "fixture-pptx": "indexed",
                                "fixture-ppt": "unreadable_format", "fixture-missing": "not_downloaded"})
        self.assertEqual(self.counts, {"indexed": 2, "unreadable_format": 1, "not_downloaded": 1})

    def test_word_passage_is_found_with_accession_file_and_no_page(self):
        self.assertEqual(match(self.out, "pmma"),
                         [("PSI-25", "PSI-25_Science Documents_Fixture ReadMe.docx", None)])

    def test_slides_are_numbered_in_order_and_stemmed(self):
        self.assertEqual(match(self.out, "flames"),  # stemming: the slide says "flame"
                         [("PSI-98", "PSI-98_Presentations_Fixture: Overview.pptx", 2)])
        self.assertEqual(match(self.out, "concluding")[0][2], 3)

    def test_rebuild_replaces_the_file_and_leaves_no_temporary(self):
        self.assertFalse(os.path.exists(self.out + ".part"))
        self.assertEqual(query(self.out, "SELECT value FROM meta WHERE key = 'passage_words'"),
                         [(str(bsi.PASSAGE_WORDS),)])


class Passages(unittest.TestCase):
    def test_long_text_is_cut_into_fixed_size_passages(self):
        chunks = bsi.passages(" ".join(f"w{i}" for i in range(320)), size=150)
        self.assertEqual([len(c.split()) for c in chunks], [150, 150, 20])
        self.assertEqual(bsi.passages("  \n "), [])

    def test_surrogates_from_pdf_text_become_valid_utf8(self):
        # A lone high surrogate (seen in a real PSI PDF) and a split pair for U+1D400.
        chunk = bsi.passages("bad\ud835 pair𝐀")[0]
        self.assertEqual(chunk, "bad� pair\U0001d400")
        chunk.encode("utf-8")  # raises if anything invalid is left

    def test_ligatures_are_spelled_out_but_superscripts_kept(self):
        self.assertEqual(bsi.passages("ﬂame eﬃcient 5 cm²")[0], "flame efficient 5 cm²")


@unittest.skipUnless(HAVE_PYPDF, "pypdf is not installed (pip install -r pipeline/requirements.txt)")
class WithPdfs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.counts, cls.out = build(with_pdfs=True)

    def test_pdf_passage_carries_its_page(self):
        self.assertEqual(match(self.out, "extinction"),
                         [("PSI-69", "PSI-69_Reports_Fixture Report.pdf", 2)])

    def test_pdf_without_text_is_marked_no_text(self):
        self.assertEqual(query(self.out, "SELECT status, page_count, passage_count FROM documents "
                                         "WHERE file_id = 'fixture-scan'"), [("no_text", 2, 0)])


if __name__ == "__main__":
    unittest.main()
