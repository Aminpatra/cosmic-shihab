"""The experimental-run endpoints, checked against the committed files in backend/data/runs/.

Expected numbers are counted straight from the files here, not through app.runs, so a loader bug
cannot hide behind itself. Run from backend/: python -m unittest discover -s tests -v

SI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from main import app

RUNS = Path(__file__).resolve().parent.parent / "data" / "runs"
FILES = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in RUNS.glob("*.json")}
ALL_TABLES = [t for entry in FILES.values() for t in entry["tables"]]
ALL_ROWS = sum(len(t["rows"]) for t in ALL_TABLES)
client = TestClient(app)


def rows(**params) -> dict:
    response = client.get("/api/runs/rows", params=params)
    response.raise_for_status()
    return response.json()


class Tables(unittest.TestCase):
    def test_every_table_is_listed_without_its_rows(self):
        body = client.get("/api/runs").json()
        self.assertEqual(len(body), len(ALL_TABLES))
        self.assertEqual(len(body), 22)
        self.assertEqual(sum(t["row_count"] for t in body), ALL_ROWS)
        self.assertTrue(all("rows" not in t for t in body))

    def test_tables_keep_psis_headers_units_and_source(self):
        bass2 = client.get("/api/runs", params={"accession": "PSI-25"}).json()
        self.assertEqual(len(bass2), 1)
        t = bass2[0]
        self.assertEqual((t["file"], t["row_is"], t["row_count"]), ("PSI-25_Experimental table_BASS-II.csv", "test", 129))
        self.assertTrue(t["doi_url"].startswith("https://doi.org/"))
        self.assertIn({"name": "Initial CO (ppm)", "unit": "ppm", "unit_inferred": False}, t["columns"])
        cfi = client.get("/api/runs", params={"accession": "PSI-39"}).json()[0]
        self.assertIn({"name": "Oxygen", "unit": "mole fraction", "unit_inferred": True}, cfi["columns"])

    def test_an_investigation_with_two_tables_and_one_with_none(self):
        self.assertEqual(len(client.get("/api/runs", params={"accession": "PSI-159"}).json()), 2)
        self.assertEqual(client.get("/api/runs", params={"accession": "PSI-60"}).json(), [])  # modelling study

    def test_unknown_investigation_is_404(self):
        self.assertEqual(client.get("/api/runs", params={"accession": "PSI-999"}).status_code, 404)
        self.assertEqual(client.get("/api/runs/rows", params={"accession": "PSI-999"}).status_code, 404)


class Rows(unittest.TestCase):
    def test_all_rows_page_through(self):
        first = rows(limit=500)
        self.assertEqual(first["total"], ALL_ROWS)
        self.assertEqual(first["total"], 2009)
        seen = [(r["accession"], r["table"], r["line"]) for offset in range(0, ALL_ROWS, 500)
                for r in rows(limit=500, offset=offset)["items"]]
        self.assertEqual(len(seen), ALL_ROWS)
        self.assertEqual(len(set(seen)), ALL_ROWS)

    def test_default_page_and_limits(self):
        body = rows()
        self.assertEqual((body["limit"], body["offset"], len(body["items"])), (100, 0, 100))
        self.assertEqual(client.get("/api/runs/rows", params={"limit": 501}).status_code, 422)
        self.assertEqual(rows(offset=ALL_ROWS)["items"], [])

    def test_rows_are_returned_as_stored(self):
        body = rows(accession="PSI-25", limit=500)
        stored = FILES["PSI-25"]["tables"][0]
        self.assertEqual(body["total"], 129)
        self.assertEqual(body["items"], [{"accession": "PSI-25", "table": stored["file"]} | r for r in stored["rows"]])

    def test_concrete_checks_from_the_master_prompt(self):
        """Section 8: 129 BASS-II runs, 274 FLEX tests, and 757.7 mmHg kept and marked as calculated."""
        self.assertEqual(rows(accession="PSI-25")["total"], 129)
        flex = rows(accession="PSI-69", limit=1)
        self.assertEqual(flex["total"], 274)
        row = flex["items"][0]
        self.assertEqual(row["cells"]["Ambient pressure; mmHg"]["raw"], "757.7")
        pressure = row["standard"]["pressure"]
        self.assertEqual(pressure["original"], {"value": 757.7, "unit": "mmHg"})
        self.assertTrue(pressure["calculated"])

    def test_table_filter(self):
        name = "PSI-159_Experimental table_CFI-G_Normal Flames.csv"
        body = rows(table=name, limit=500)
        self.assertEqual(body["total"], 179)
        self.assertTrue(all(r["table"] == name for r in body["items"]))
        self.assertEqual(client.get("/api/runs/rows", params={"table": "nope.csv"}).status_code, 404)

    def test_cells_can_be_left_out_for_charts(self):
        body = rows(accession="PSI-69", cells="false", limit=3)
        self.assertEqual(body["total"], 274)
        for r in body["items"]:
            self.assertNotIn("cells", r)
            self.assertIn("oxygen", r["standard"])


if __name__ == "__main__":
    unittest.main()
