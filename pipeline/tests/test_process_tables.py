"""Checks for pipeline/process_tables.py and the runs it wrote to backend/data/runs/.

    python3 -m unittest discover -s pipeline/tests -v

Each case named in the master prompt (section 4, "Real cases the pipeline must handle") has a test
here, run against the real PSI rows in datasets/, not against made-up ones.

SI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import process_tables as pt  # noqa: E402

RUNS = os.path.join(ROOT, "backend", "data", "runs")


def load(accession):
    with open(os.path.join(RUNS, f"{accession}.json"), encoding="utf-8") as f:
        return json.load(f)


def row(accession, run_id, table=0):
    rows = load(accession)["tables"][table]["rows"]
    return next(r for r in rows if r["run_id"] == run_id)


class ParseCell(unittest.TestCase):
    def test_original_text_is_always_kept(self):
        for raw in ["", "none", "-1", "0.9   1.3   2.75", "1.4 incr to 10.0", "~ 21.5", "#DIV/0!"]:
            self.assertEqual(pt.parse_cell(raw)["raw"], raw)

    def test_several_values_in_one_cell_stay_a_list(self):
        self.assertEqual(pt.parse_cell("0.9   1.3   2.75")["values"], [0.9, 1.3, 2.75])
        self.assertEqual(pt.parse_cell("0.5; 1.0; 1.5; 2.0; or 3.0 ")["values"], [0.5, 1.0, 1.5, 2.0, 3.0])
        self.assertEqual(pt.parse_cell("1.4 incr to 10.0")["kind"], "text")  # never averaged or picked

    def test_none_and_empty_are_missing_and_not_zero(self):
        none, empty, zero = pt.parse_cell("none"), pt.parse_cell(""), pt.parse_cell("0")
        self.assertEqual((none["kind"], none["missing"]), ("missing", "text"))
        self.assertEqual((empty["kind"], empty["missing"]), ("missing", "empty"))
        self.assertNotIn("value", none)
        self.assertNotIn("value", empty)
        self.assertEqual(zero["value"], 0)

    def test_dashes_and_spreadsheet_errors_are_missing(self):
        self.assertEqual(pt.parse_cell("–")["missing"], "dash")
        self.assertEqual(pt.parse_cell("#VALUE!")["missing"], "spreadsheet_error")

    def test_units_ranges_and_qualifiers(self):
        self.assertEqual(pt.parse_cell("30 cm/s") | {}, {"raw": "30 cm/s", "kind": "number", "value": 30,
                                                       "unit": "cm/s"})
        self.assertEqual(pt.parse_cell("21.5 - 21.7")["range"], [21.5, 21.7])
        self.assertEqual(pt.parse_cell("~ 21.5")["approx"], True)
        self.assertEqual(pt.parse_cell(">500")["bound"], ">")

    def test_header_units(self):
        self.assertEqual(pt.header_unit("Ambient pressure; mmHg"), "mmHg")
        self.assertEqual(pt.header_unit("Calibrated  initial O2 % by vol "), "% by vol")
        self.assertEqual(pt.header_unit("burn time (sec)"), "s")
        self.assertIsNone(pt.header_unit("Fan display"))
        self.assertIsNone(pt.header_unit("Percent O2 (Note 1)"))


class RealCases(unittest.TestCase):
    """The cases the master prompt lists, on PSI's own rows."""

    def test_fuel_text_is_kept_and_split_only_as_far_as_it_says(self):
        fuel = row("PSI-25", "B1")["standard"]["fuel"]
        self.assertEqual(fuel["text"], "100 micron PMMA film   2 cm wide")
        self.assertEqual((fuel["material"], fuel["shape"]), ("PMMA", "film"))
        self.assertEqual([(s["value"], s["unit"], s.get("label")) for s in fuel["sizes"]],
                         [(100, "micron", None), (2, "cm", "wide")])
        # "2 cm 0.1 mm PMMA film" does not say which size is the width, so neither gets a label.
        fuel = row("PSI-25", "B6")["standard"]["fuel"]
        self.assertEqual(fuel["text"], "2 cm 0.1 mm PMMA film")
        self.assertEqual([(s["value"], s["unit"], s.get("label")) for s in fuel["sizes"]],
                         [(2, "cm", None), (0.1, "mm", None)])

    def test_several_values_for_one_run(self):
        cells = row("PSI-25", "B6")["cells"]
        self.assertEqual(cells["Fan display"]["values"], [0.9, 1.3, 2.75])
        self.assertEqual(cells["Air display"]["kind"], "text")
        self.assertEqual(cells["Air display"]["raw"], "3   5   approaching 10")

    def test_none_in_a_numeric_column_and_an_empty_cell(self):
        cells = row("PSI-25", "B2")["cells"]
        self.assertEqual(cells["Total Frames Shot"]["missing"], "text")
        self.assertEqual(cells["Final CO2 % by vol"]["missing"], "empty")
        self.assertEqual(cells["Initial CO (ppm)"]["value"], 6)

    def test_impossible_reading_is_kept_and_flagged(self):
        cell = row("PSI-25", "B4")["cells"]["Initial CO (ppm)"]
        self.assertEqual(cell["value"], -1)
        self.assertIn("negative_concentration", cell["flags"])

    def test_oxygen_units_are_kept_and_the_conversion_is_marked(self):
        o2 = row("PSI-25", "B1")["standard"]["oxygen"]  # BASS-II: percent by volume
        self.assertEqual((o2["value"], o2["unit"], o2["calculated"]), (0.222, "mole fraction", True))
        self.assertEqual(o2["original"], {"value": 22.2, "unit": "% by vol"})
        o2 = load("PSI-69")["tables"][0]["rows"][0]["standard"]["oxygen"]  # FLEX: already a mole fraction
        self.assertEqual((o2["value"], o2["unit"]), (0.21, "mole fraction"))
        self.assertNotIn("calculated", o2)

    def test_flex_pressure_in_mmhg_is_converted_and_marked(self):
        p = load("PSI-69")["tables"][0]["rows"][0]["standard"]["pressure"]
        self.assertEqual(p["original"], {"value": 757.7, "unit": "mmHg"})
        self.assertAlmostEqual(p["value"], 757.7 / 760, places=9)
        self.assertTrue(p["calculated"])

    def test_bass2_table_and_test_matrix_are_one_test_each(self):
        rows = load("PSI-25")["tables"][0]["rows"]
        self.assertEqual(len(rows), 129)
        links = [(r["linked"][0]["sheet"], r["linked"][0]["row"]) for r in rows]
        self.assertEqual(len(set(links)), 129)  # every test links to its own matrix row
        self.assertEqual(sum(len(rows) - 1 for rows in pt.read_xlsx(pt.DATASETS / pt.BASS2_MATRIX).values()), 129)
        self.assertEqual(row("PSI-25", "B1")["linked"][0] | {}, {
            "file": pt.BASS2_MATRIX, "sheet": "Bhattacharjee", "row": 2, "date": "2014-02-19"})

    def test_spreadsheet_damage_is_flagged_not_fixed(self):
        bre = load("PSI-20")["tables"][0]["rows"]
        cell = next(r["cells"]["Oxygen Conc (percent)"] for r in bre
                    if r["cells"]["Oxygen Conc (percent)"]["raw"] == "3400%")
        self.assertEqual(cell["value"], 3400)
        self.assertIn("percent_over_100", cell["flags"])
        cld = [r["cells"]["Fuel Bottle"] for r in load("PSI-21")["tables"][0]["rows"]]
        self.assertIn("impossible_formula", next(c for c in cld if c["raw"] == "40% CH5")["flags"])
        self.assertNotIn("flags", next(c for c in cld if c["raw"] == "40% CH4"))


class CommittedRuns(unittest.TestCase):
    def test_committed_files_match_a_fresh_build(self):
        fresh = pt.build()
        self.assertEqual(sorted(f[:-5] for f in os.listdir(RUNS) if f.endswith(".json")), sorted(fresh))
        for accession, entry in fresh.items():
            self.assertEqual(load(accession), json.loads(json.dumps(entry)), accession)

    def test_row_counts_match_the_data_plan(self):
        counts = {a: sum(t["row_count"] for t in load(a)["tables"]) for a in pt.build()}
        self.assertEqual(sum(counts.values()), 2009)  # 1,850 tier 1 + 159 tier 2 in docs/DATA_PLAN.md
        self.assertEqual(counts["PSI-159"], 333)       # 861 empty lines in the inverse-flame table skipped

    def test_every_row_points_back_to_its_source_line(self):
        for accession in pt.build():
            for table in load(accession)["tables"]:
                self.assertTrue(table["doi_url"].startswith("https://doi.org/10.60555/"))
                lines = [r["line"] for r in table["rows"]]
                self.assertEqual(lines, sorted(set(lines)))
                self.assertGreaterEqual(min(lines), 2)


if __name__ == "__main__":
    unittest.main()
