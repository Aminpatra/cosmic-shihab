"""The runs loader, checked against the committed files in backend/data/runs/.

Expected counts are the brief's (master prompt, "Concrete checks"): a change fails here until it
is explained. Run from backend/: python -m unittest discover -s tests -v
"""

import unittest

from app import runs


class RunsTests(unittest.TestCase):
    def test_loads_every_table_and_row(self):
        data = runs.runs()
        self.assertEqual(len(data), 20)
        self.assertEqual(sum(len(t["tables"]) for t in data.values()), 22)
        self.assertEqual(sum(len(tb["rows"]) for t in data.values() for tb in t["tables"]), 2009)

    def test_known_counts(self):
        self.assertEqual(len(runs.runs()["PSI-69"]["tables"][0]["rows"]), 274)
        self.assertEqual(len(runs.runs()["PSI-25"]["tables"][0]["rows"]), 129)

    def test_flex_pressure_keeps_psi_value(self):
        pressure = runs.runs()["PSI-69"]["tables"][0]["rows"][0]["standard"]["pressure"]
        self.assertTrue(pressure["calculated"])
        self.assertEqual(pressure["original"], {"value": 757.7, "unit": "mmHg"})


if __name__ == "__main__":
    unittest.main()
