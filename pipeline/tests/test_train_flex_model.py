"""Checks for train_flex_model.py on the real FLEX rows. They check how the data is read and split
and that the committed results come from this code; they assert nothing about how good it is.

    python3 -m unittest discover -s pipeline/tests -v

Skipped unless scikit-learn and shap are installed (pip install -r pipeline/requirements.txt).

AI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

import importlib.util
import json
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
HAVE_ML = all(importlib.util.find_spec(m) for m in ("sklearn", "shap"))


@unittest.skipUnless(HAVE_ML, "scikit-learn and shap are not installed (pipeline/requirements.txt)")
class FlexData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import train_flex_model as tfm
        cls.tfm = tfm
        cls.X, cls.y, cls.groups, cls.tests, cls.notes = tfm.load_flex()

    def test_reads_every_test_with_its_end(self):
        self.assertEqual(self.X.shape, (274, len(self.tfm.FEATURES)))
        counts = {c: int((self.y == c).sum()) for c in self.tfm.CLASSES}
        self.assertEqual(counts, {"Extinction": 186, "Disruption": 61, "Completion": 27})

    def test_no_input_was_measured_during_the_test(self):
        inputs = {column for _, _, column in self.tfm.FEATURES}
        self.assertEqual(inputs & self.tfm.OUTCOME_COLUMNS, set())
        self.assertEqual(len(self.tfm.OUTCOME_COLUMNS), 3)

    def test_zero_pressure_and_missing_diameters_are_missing_not_zero(self):
        self.assertEqual(self.notes["pressure_zero_read_as_missing"], [114])
        row = self.tests.index(114)
        self.assertTrue(math.isnan(self.X[row, 1]))
        self.assertEqual(self.notes["missing_droplet_diameter"], 12)

    def test_flex_pressure_is_converted_from_psi_mmhg(self):
        row = self.tests.index(1)  # PSI: 757.7 mmHg
        self.assertAlmostEqual(self.X[row, 1], 757.7 / 760)

    def test_dates_in_both_psi_formats(self):
        self.assertEqual(self.tfm.parse_date("3/5/2009"), "2009-03-05")
        self.assertEqual(self.tfm.parse_date("11/18/11"), "2011-11-18")
        self.assertEqual(len(set(self.groups)), 80)

    def test_split_keeps_each_day_on_one_side(self):
        train, test = self.tfm.split_days(self.y, self.groups)
        self.assertEqual(set(self.groups[train]) & set(self.groups[test]), set())
        self.assertEqual(len(train) + len(test), 274)
        self.assertTrue(0.15 <= len(test) / 274 <= 0.25, len(test))
        self.assertEqual(set(self.y[test]), set(self.tfm.CLASSES))


@unittest.skipUnless(HAVE_ML, "scikit-learn and shap are not installed (pipeline/requirements.txt)")
class CommittedResults(unittest.TestCase):
    def test_committed_results_are_what_this_code_produces(self):
        import train_flex_model as tfm
        with open(tfm.OUT, encoding="utf-8") as handle:
            committed = json.load(handle)
        if committed["reproduce"]["scikit_learn"] != tfm.sklearn.__version__:
            self.skipTest("results were made with another scikit-learn version")
        fresh = json.loads(json.dumps(tfm.train()))
        # The Python version is recorded for the reader; the numbers depend on the libraries,
        # checked above, so a teammate on another Python must still match.
        for results in (fresh, committed):
            results["reproduce"].pop("python")
        self.assertEqual(fresh, committed)


if __name__ == "__main__":
    unittest.main()
