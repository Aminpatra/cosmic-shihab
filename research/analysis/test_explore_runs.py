"""Checks that the committed analysis is current and that its key findings hold.

    python3 -m unittest discover -s research/analysis -v

The CSV files and summary.md are rebuilt in memory and compared with the committed ones, so a
change to backend/data/runs/ that is not followed by a rerun fails here. The figures need
matplotlib and are not compared.

SI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

import csv
import io
import unittest

import explore_runs as e

TABLES = e.load()
SUSPECTS = e.suspects(TABLES)
KEYS = {(s["table"], s["line"], s["column"]) for s in SUSPECTS if s["line"] != ""}


def as_csv(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def committed(name):
    return (e.HERE / name).read_text(encoding="utf-8")


class Current(unittest.TestCase):
    def test_committed_files_match_a_fresh_run(self):
        coverage = e.standard_coverage(TABLES, KEYS)
        ranges = e.condition_ranges(TABLES, KEYS)
        relations = e.flex_relationships(TABLES, KEYS)
        ends = e.flex_test_end(TABLES, KEYS)
        expected = {
            "column_profile.csv": as_csv(e.column_profile(TABLES)),
            "standard_coverage.csv": as_csv(coverage),
            "condition_ranges.csv": as_csv(ranges),
            "suspect_values.csv": as_csv(SUSPECTS),
            "flex_relationships.csv": as_csv(relations),
            "flex_test_end.csv": as_csv(ends),
            "summary.md": e.summary(TABLES, coverage, ranges, SUSPECTS, relations, ends),
        }
        for name, text in expected.items():
            self.assertEqual(committed(name), text, f"{name} is stale: rerun explore_runs.py")


class Findings(unittest.TestCase):
    def rule(self, rule):
        return [s for s in SUSPECTS if s["rule"] == rule]

    def test_suspects_the_pipeline_does_not_flag(self):
        zero = self.rule("zero_or_negative_pressure")
        self.assertEqual([(s["accession"], s["run_id"], s["raw"]) for s in zero], [("PSI-69", "114", "0")])
        self.assertEqual(len(self.rule("negative_flow_velocity")), 8)
        self.assertEqual(len(self.rule("exact_duplicate_row")), 50)
        bre = self.rule("standard_value_from_flagged_cell")
        self.assertEqual(sorted(s["raw"] for s in bre), ["2100%", "3400%"])

    def test_suspect_values_stay_out_of_ranges(self):
        flex = next(r for r in e.condition_ranges(TABLES, KEYS)
                    if r["accession"] == "PSI-69" and r["field"] == "pressure")
        self.assertEqual((flex["n"], flex["left_out_suspect"]), (273, 1))
        self.assertGreater(flex["min"], 0.6)

    def test_flex_endings_cover_every_test(self):
        ends = e.flex_test_end(TABLES, KEYS)
        self.assertEqual(sum(row["tests"] for row in ends), 274)
        low_methanol = next(r for r in ends if r["fuel"] == "Methanol" and r["oxygen_band"] == "below 0.18")
        self.assertEqual((low_methanol["tests"], low_methanol["extinction"]), (54, 54))

    def test_correlations_use_plain_numbers_only(self):
        row = next(r for r in e.flex_relationships(TABLES, KEYS)
                   if (r["fuel"], r["condition"], r["outcome"]) == ("Heptane", "oxygen", "burn_time"))
        self.assertEqual((row["n"], row["spearman_rho"]), (111, 0.77))  # "~6" and "~9" left out


if __name__ == "__main__":
    unittest.main()
