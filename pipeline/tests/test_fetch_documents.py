"""Checks for fetch_documents.py. No test calls PSI or S3: both are replaced by fakes.

    python3 -m unittest discover -s pipeline/tests -v

AI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import fetch_documents as fd  # noqa: E402
import psi_client as psi  # noqa: E402


def row(file_id, file_name, data, extension=".pdf"):
    return {"accession": "PSI-69", "file_id": file_id, "file_name": file_name,
            "extension": extension, "bytes": len(data), "data": data}


class FakePSI:
    """Counts link requests and serves each row's bytes from its fake S3 URL."""

    def __init__(self, rows):
        self.by_url = {f"{psi.S3_PREFIX}{r['file_id']}": r["data"] for r in rows}
        self.ids = {r["file_name"]: r["file_id"] for r in rows}
        self.links = 0

    def link(self, accession, file_name):
        self.links += 1
        return f"{psi.S3_PREFIX}{self.ids[file_name]}"

    def get(self, url, timeout):
        return self.by_url[url]


class FetchTests(unittest.TestCase):
    def setUp(self):
        self.cache = tempfile.mkdtemp()
        self.rows = [row("a1", "FLEX: Overview.pdf", b"%PDF one"),
                     row("b2", "Notes.docx", b"PK two", ".docx"),
                     row("c3", "Old slides.ppt", b"old", ".ppt")]

    def run_once(self, fake):
        return fd.fetch_all(self.rows, self.cache, fake.link, fake.get, sleep=lambda s: None)

    def test_second_run_downloads_nothing(self):
        first = FakePSI(self.rows)
        self.assertEqual(self.run_once(first), (2, 1, []))
        self.assertEqual(first.links, 2)
        second = FakePSI(self.rows)
        self.assertEqual(self.run_once(second), (0, 3, []))
        self.assertEqual(second.links, 0)

    def test_cache_is_named_by_file_id_not_by_psi_name(self):
        self.run_once(FakePSI(self.rows))
        path = fd.cached_path(self.rows[0], self.cache)
        self.assertEqual(os.path.basename(path), "a1.pdf")
        with open(path, "rb") as handle:
            self.assertEqual(handle.read(), b"%PDF one")

    def test_unreadable_formats_are_not_requested(self):
        fake = FakePSI(self.rows)
        self.run_once(fake)
        self.assertFalse(os.path.exists(fd.cached_path(self.rows[2], self.cache)))

    def test_wrong_size_is_a_failure_and_leaves_no_file(self):
        fake = FakePSI(self.rows)
        fake.by_url[f"{psi.S3_PREFIX}a1"] = b"%PDF"  # cut short: 4 bytes, PSI lists 8
        downloaded, _, failures = self.run_once(fake)
        self.assertEqual(downloaded, 1)
        self.assertEqual([f[1] for f in failures], ["FLEX: Overview.pdf"])
        folder = os.path.join(self.cache, "PSI-69")
        self.assertEqual(sorted(os.listdir(folder)), ["b2.docx"])

    def test_pauses_after_every_psi_request(self):
        pauses = []
        fd.fetch_all(self.rows, self.cache, FakePSI(self.rows).link, FakePSI(self.rows).get,
                     sleep=pauses.append)
        self.assertEqual(pauses, [fd.PAUSE, fd.PAUSE])


class SelectionTests(unittest.TestCase):
    def test_covers_non_raw_documents_from_the_committed_manifest(self):
        rows = fd.documents()
        self.assertTrue(rows)
        self.assertTrue(all(r["category"] != "Raw Data" for r in rows))
        self.assertEqual(len({(r["accession"], r["file_id"]) for r in rows}), len(rows))


if __name__ == "__main__":
    unittest.main()
