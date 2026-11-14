"""Checks for the hand-written investigation tags and where the catalogue serves them.

    python3 -m unittest discover -s pipeline/tests -v

AI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import build_catalogue as bc  # noqa: E402

DATA = os.path.join(ROOT, "backend", "data", "investigations")


class TagFile(unittest.TestCase):
    def test_every_investigation_is_tagged_with_a_source(self):
        tags = bc.load_tags()
        accessions = {name[:-5] for name in os.listdir(DATA) if name.endswith(".json")}
        self.assertEqual(set(tags), accessions)
        self.assertEqual(len(tags), 24)
        for accession, entry in tags.items():
            for tag in bc.TAGS:
                self.assertTrue(entry["sources"][tag].strip(), f"{accession} {tag}")

    def test_unknown_value_is_refused(self):
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        with open(os.path.join(bc.RESEARCH, "investigation_tags.csv"), encoding="utf-8") as src:
            text = src.read()
        with open(os.path.join(folder, "investigation_tags.csv"), "w", encoding="utf-8") as out:
            out.write(text.replace('"suppression","record.objective: \'measure',
                                   '"extinguishing","record.objective: \'measure', 1))
        with mock.patch.object(bc, "RESEARCH", folder):
            with self.assertRaisesRegex(ValueError, "PSI-69 fire_safety_role"):
                bc.load_tags()

    def test_catalogue_serves_the_tags(self):
        tags = bc.load_tags()
        for accession, entry in tags.items():
            with open(os.path.join(DATA, f"{accession}.json"), encoding="utf-8") as handle:
                served = json.load(handle)["derived"]["tags"]
            self.assertEqual(served["values"], entry["values"], accession)
            self.assertEqual(served["sources"], entry["sources"], accession)

    def test_run_data_label_matches_the_tables_held(self):
        for accession, entry in bc.load_tags().items():
            with open(os.path.join(DATA, f"{accession}.json"), encoding="utf-8") as handle:
                tables = json.load(handle)["derived"]["experimental_tables"]
            no_table = entry["values"]["flare_data"] == "catalogue metadata only"
            self.assertEqual(no_table, not tables, accession)


if __name__ == "__main__":
    unittest.main()
