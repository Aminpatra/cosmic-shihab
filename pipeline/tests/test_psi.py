"""Checks for the PSI client and for the catalogue committed to the repo.

    python3 -m unittest discover -s pipeline/tests -v

No test calls PSI. The client tests use small saved responses in fixtures/;
the catalogue tests read the committed files in backend/data/ and datasets/.

SI use: written with Claude Code (Claude Fable 5.2), reviewed by the team.
"""

import csv
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import psi_client as psi  # noqa: E402
from build_catalogue import table_shape  # noqa: E402

FIXTURES = os.path.join(HERE, "fixtures")
DATA = os.path.join(ROOT, "backend", "data")
DATASETS = os.path.join(ROOT, "datasets")


def fixture(name: str) -> bytes:
    with open(os.path.join(FIXTURES, name), "rb") as handle:
        return handle.read()


def fake_search(url: str) -> bytes:
    offset = url.rsplit("from=", 1)[1]
    return fixture(f"search_from_{offset}.json")


class ClientTests(unittest.TestCase):
    def test_search_pages_through_and_keeps_only_combustion(self):
        accessions = psi.list_combustion_accessions(fetch=fake_search)
        self.assertEqual(len(accessions), 24)
        self.assertNotIn("PSI-181", accessions)  # Materials Science
        self.assertNotIn("PSI-108", accessions)  # Fluid Physics
        self.assertIn("PSI-101", accessions)     # the one hit on the second page

    def test_search_without_hits_fails_loudly(self):
        with self.assertRaises(psi.PSIFormatError):
            psi.list_combustion_accessions(fetch=lambda url: b'{"results": []}')

    def test_cut_short_response_fails_loudly(self):
        whole = fixture("inv_PSI-142.json")
        with self.assertRaises(psi.PSIFormatError):
            psi.parse_json(whole[: len(whole) // 2], "PSI-142 record")

    def test_record_must_be_the_one_asked_for(self):
        record = psi.parse_json(fixture("inv_PSI-142.json"), "PSI-142 record")
        self.assertEqual(psi.check_record(record, "PSI-142")["doi"], "10.60555/80qf-vj95")
        with self.assertRaises(psi.PSIFormatError):
            psi.check_record(record, "PSI-69")
        with self.assertRaises(psi.PSIFormatError):
            psi.check_record({"accession": "PSI-142"}, "PSI-142")

    def test_file_list_flattens_and_matches_declared_size(self):
        record = psi.parse_json(fixture("inv_PSI-142.json"), "record")
        tree = psi.parse_json(fixture("files_PSI-142.json"), "file list")
        files = psi.flatten_files(tree)
        self.assertEqual(len(files), 3)
        self.assertEqual({f["category"] for f in files},
                         {"Analyzed Data", "Experimental table", "Investigation Metadata Files"})
        self.assertAlmostEqual(psi.listed_bytes(tree), record["totalFileSize"], delta=1)

    def test_file_list_removes_repeated_entries(self):
        tree = psi.parse_json(fixture("files_PSI-142.json"), "file list")
        doubled = {"files": tree["files"] + tree["files"]}
        self.assertEqual(len(psi.flatten_files(doubled)), 3)

    def test_file_list_without_files_fails_loudly(self):
        with self.assertRaises(psi.PSIFormatError):
            psi.flatten_files({"message": "Version Required"})

    def test_download_link_must_point_at_psi_storage(self):
        good = "https://psi-repo-prod.s3.amazonaws.com/psi-data/PSI-142/x.csv?Signature=abc"
        self.assertEqual(psi.download_url("PSI-142", "x.csv", fetch=lambda url: good.encode()), good)
        for bad in (b"https://example.com/x.csv", b'{"message": "File not found"}'):
            with self.assertRaises(psi.PSIFormatError):
                psi.download_url("PSI-142", "x.csv", fetch=lambda url, bad=bad: bad)


class CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = os.path.join(DATA, "investigations")
        cls.investigations = {}
        for name in os.listdir(folder):
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                cls.investigations[name[:-5]] = json.load(handle)
        with open(os.path.join(DATA, "files.csv"), encoding="utf-8", newline="") as handle:
            cls.files = list(csv.DictReader(handle))

    def test_all_24_combustion_investigations_are_present(self):
        self.assertEqual(len(self.investigations), 24)
        for accession, item in self.investigations.items():
            self.assertEqual(item["accession"], accession)
            self.assertEqual(item["researchArea"], "Combustion Science")

    def test_every_investigation_can_be_cited(self):
        for accession, item in self.investigations.items():
            self.assertTrue(item["doi"], accession)
            self.assertTrue(item["title"], accession)
            self.assertEqual(item["derived"]["doi_url"], "https://doi.org/" + item["doi"])

    def test_licence_is_stated_or_flagged(self):
        unstated = sorted(a for a, item in self.investigations.items()
                          if not item["derived"]["licence_stated"])
        self.assertEqual(unstated, ["PSI-10"])

    def test_manifest_has_every_file_once(self):
        self.assertEqual(len(self.files), 60866)
        keys = {(row["accession"], row["file_id"]) for row in self.files}
        self.assertEqual(len(keys), len(self.files))
        for accession, item in self.investigations.items():
            count = sum(1 for row in self.files if row["accession"] == accession)
            self.assertEqual(count, item["derived"]["file_count"], accession)

    def test_file_list_adds_up_to_what_psi_declares(self):
        for accession, item in self.investigations.items():
            declared = item["totalFileSize"] or 0
            self.assertAlmostEqual(item["derived"]["bytes_listed"], declared,
                                   delta=0.001 * max(declared, 1), msg=accession)

    def test_experimental_tables_are_unchanged_and_counted(self):
        tables = [row for row in self.files if row["category"] == "Experimental table"]
        self.assertEqual(len(tables), 22)
        total_rows = 0
        for row in tables:
            path = os.path.join(DATASETS, row["file_name"])
            self.assertEqual(os.path.getsize(path), int(row["bytes"]), row["file_name"])
            total_rows += table_shape(path)[0]
        self.assertEqual(total_rows, 2009)

    def test_nothing_private_or_expiring_is_committed(self):
        email = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
        for folder in (os.path.join(DATA, "investigations"), FIXTURES):
            for name in os.listdir(folder):
                with open(os.path.join(folder, name), encoding="utf-8") as handle:
                    text = handle.read()
                self.assertIsNone(email.search(text), name)
                self.assertNotIn("Signature=", text, name)
                self.assertNotIn("x-amz-security-token", text, name)


if __name__ == "__main__":
    unittest.main()
