"""The catalogue endpoints, checked against the committed files in backend/data/.

Expected numbers are counted straight from the files here, not through app.catalogue, so a
loader bug cannot hide behind itself. Run from backend/: python -m unittest discover -s tests -v
"""

import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from main import app

DATA = Path(__file__).resolve().parent.parent / "data"
JSON_FILES = sorted((DATA / "investigations").glob("*.json"))
CSV_ROWS = sum(1 for _ in open(DATA / "files.csv", encoding="utf-8")) - 1
client = TestClient(app)


def record(accession: str) -> dict:
    return json.loads((DATA / "investigations" / f"{accession}.json").read_text(encoding="utf-8"))


class Health(unittest.TestCase):
    def test_counts_match_the_files(self):
        body = client.get("/api/health").json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["investigations"], len(JSON_FILES))
        self.assertEqual(body["files"], CSV_ROWS)
        self.assertRegex(body["retrieved"], r"^\d{4}-\d{2}-\d{2}$")

    def test_docs_are_under_api(self):
        self.assertEqual(client.get("/api/openapi.json").status_code, 200)
        self.assertEqual(client.get("/api/docs").status_code, 200)


class Investigations(unittest.TestCase):
    def test_lists_every_investigation_as_a_summary(self):
        items = client.get("/api/investigations").json()
        self.assertEqual(len(items), len(JSON_FILES))
        for item in items:
            self.assertTrue(item["accession"] and item["title"] and item["doi"], item["accession"])
            self.assertIn("investigationAcronym", item)
            self.assertIn("file_count", item["derived"])
            self.assertNotIn("objective", item)  # long text stays on the detail endpoint
        numbers = [int(item["accession"].removeprefix("PSI-")) for item in items]
        self.assertEqual(numbers, sorted(numbers))

    def test_detail_is_the_stored_record_unchanged(self):
        for path in JSON_FILES:
            response = client.get(f"/api/investigations/{path.stem}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), record(path.stem))

    def test_unknown_accession_is_404(self):
        self.assertEqual(client.get("/api/investigations/PSI-0").status_code, 404)


class Files(unittest.TestCase):
    def test_unfiltered_total_is_every_row(self):
        body = client.get("/api/files").json()
        self.assertEqual(body["total"], CSV_ROWS)
        self.assertEqual(len(body["items"]), 100)

    def test_each_investigation_total_matches_its_file_count(self):
        for path in JSON_FILES:
            body = client.get("/api/files", params={"accession": path.stem, "limit": 1}).json()
            self.assertEqual(body["total"], record(path.stem)["derived"]["file_count"], path.stem)

    def test_kind_filter_matches_files_by_kind(self):
        expected = record("PSI-10")["derived"]["files_by_kind"]["table"]["files"]
        body = client.get("/api/files", params={"accession": "PSI-10", "kind": "table", "limit": 500}).json()
        self.assertEqual(body["total"], expected)
        self.assertTrue(all(item["kind"] == "table" for item in body["items"]))

    def test_category_filter(self):
        body = client.get("/api/files", params={"category": "Experimental table", "limit": 500}).json()
        self.assertGreater(body["total"], 0)
        self.assertTrue(all(item["extension"] == ".csv" for item in body["items"]))

    def test_pages_do_not_overlap(self):
        first = client.get("/api/files", params={"limit": 5, "offset": 0}).json()["items"]
        second = client.get("/api/files", params={"limit": 5, "offset": 5}).json()["items"]
        self.assertEqual(len(first), 5)
        self.assertFalse({i["file_id"] for i in first} & {i["file_id"] for i in second})

    def test_types(self):
        item = client.get("/api/files", params={"limit": 1}).json()["items"][0]
        self.assertIsInstance(item["bytes"], int)
        self.assertIsInstance(item["version"], int)

    def test_bad_requests(self):
        self.assertEqual(client.get("/api/files", params={"accession": "PSI-0"}).status_code, 404)
        self.assertEqual(client.get("/api/files", params={"kind": "video"}).status_code, 422)
        self.assertEqual(client.get("/api/files", params={"limit": 501}).status_code, 422)
        self.assertEqual(client.get("/api/files", params={"offset": -1}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
