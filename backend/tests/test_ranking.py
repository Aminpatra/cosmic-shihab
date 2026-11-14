"""The ranking, on the real PSI rows in backend/data/runs/ and the tags in the catalogue.

Plan: docs/superpowers/plans/2026-11-14-ranking-engine.md. Run from backend/:
python -m unittest discover -s tests -v
"""

import unittest

from app import catalogue, ranking, runs


def tags(accession: str) -> dict:
    return catalogue.investigations()[accession]["derived"]["tags"]["values"]


def rows_of(accession: str):
    for table in runs.runs()[accession]["tables"]:
        yield from table["rows"]


def first(rows, test, what):
    for row in rows:
        if test(row):
            return row
    raise AssertionError(f"No row found: {what}")


def fuel_text(row) -> str:
    return row.get("standard", {}).get("fuel", {}).get("text", "")


class Fixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.flex_tags, cls.bass2_tags = tags("PSI-69"), tags("PSI-25")
        cls.psi10_tags, cls.spice_tags = tags("PSI-10"), tags("PSI-107")
        cls.flex1 = runs.runs()["PSI-69"]["tables"][0]["rows"][0]
        cls.spice_row = runs.runs()["PSI-107"]["tables"][0]["rows"][0]
        cls.pmma_row = first(rows_of("PSI-25"), lambda r: "PMMA film" in fuel_text(r), "PSI-25 PMMA film")
        cls.c2h4_row = first(rows_of("PSI-10"), lambda r: fuel_text(r) == "C2H4", "PSI-10 C2H4")
        cls.heptane_row = first((r for acc in runs.runs() for r in rows_of(acc)),
                                lambda r: fuel_text(r) == "Heptane", "Heptane")

        def flagged_oxygen(row):
            oxygen = row.get("standard", {}).get("oxygen")
            return bool(oxygen) and "percent_over_100" in row["cells"][oxygen["column"]].get("flags", [])

        cls.psi20_flagged_row = first(rows_of("PSI-20"), flagged_oxygen, "PSI-20 oxygen over 100%")


class RowScoring(Fixtures):
    def test_tolerances_come_from_the_data(self):
        t = ranking.tolerances()
        self.assertAlmostEqual(t["oxygen"], 0.1825, places=4)
        self.assertAlmostEqual(t["pressure"], 1.25, places=4)
        self.assertAlmostEqual(t["flow_velocity"], 22.8, places=4)

    def test_closeness_falls_linearly_to_zero(self):
        self.assertEqual(ranking.closeness(0.21, 0.21, 0.2), 1.0)
        self.assertAlmostEqual(ranking.closeness(0.21, 0.31, 0.2), 0.5)
        self.assertEqual(ranking.closeness(0.21, 0.90, 0.2), 0.0)

    def test_fuel_names_match_formulas_case_and_punctuation(self):  # Review Focus 1
        for typed in ["c2h4", " Ethylene", "ETHYLENE"]:
            self.assertEqual(ranking.normalize_fuel(typed), "ethylene")
            self.assertTrue(ranking.fuel_matches(typed, self.c2h4_row["standard"]["fuel"]))
        self.assertTrue(ranking.fuel_matches("n-heptane", self.heptane_row["standard"]["fuel"]))
        self.assertTrue(ranking.fuel_matches("PMMA film", self.pmma_row["standard"]["fuel"]))

    def test_missing_variable_counts_as_zero_not_skipped(self):
        score, parts = ranking.score_row(ranking.Scenario(oxygen=0.21, flow_velocity=20),
                                         self.flex1, self.flex_tags)
        self.assertEqual(parts, {"oxygen": 1.0, "flow_velocity": None})
        self.assertAlmostEqual(score, 0.5)

    def test_fuel_scores_from_material_list_and_formula_text(self):
        def fuel_part(fuel, row, row_tags):
            return ranking.score_row(ranking.Scenario(fuel=fuel), row, row_tags)[1]["fuel"]

        self.assertEqual(fuel_part("PMMA", self.pmma_row, self.bass2_tags), 1.0)
        self.assertEqual(fuel_part("Kapton", self.pmma_row, self.bass2_tags), 0.0)
        self.assertEqual(fuel_part("ethylene", self.c2h4_row, self.psi10_tags), 1.0)

    def test_phase_and_concern_come_from_tags(self):  # FLEX: liquid, suppression; PSI-10: not stated
        scenario = ranking.Scenario(fuel_phase="liquid", concern="suppression")
        self.assertEqual(ranking.score_row(scenario, self.flex1, self.flex_tags)[1],
                         {"fuel_phase": 1.0, "concern": 1.0})
        self.assertEqual(ranking.score_row(scenario, self.c2h4_row, self.psi10_tags)[1],
                         {"fuel_phase": 0.0, "concern": None})

    def test_flagged_value_is_unavailable(self):  # PSI-20 oxygen "3400%", flag percent_over_100
        self.assertIsNone(ranking.scorable_value(self.psi20_flagged_row, "oxygen"))

    def test_zero_weight_drops_the_variable(self):
        scenario = ranking.Scenario(oxygen=0.21, flow_velocity=20, weights={"flow_velocity": 0})
        self.assertEqual(scenario.set_variables(), ["oxygen"])


if __name__ == "__main__":
    unittest.main()
