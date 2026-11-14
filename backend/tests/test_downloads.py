"""The download-link endpoint, with PSI replaced by a fake answer. Nothing here calls PSI.

Run from backend/: python -m unittest discover -s tests -v
"""

import csv
import unittest
import urllib.error
import urllib.parse
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient

from app.services import psi_links
from main import app

DATA = Path(__file__).resolve().parent.parent / "data"
with open(DATA / "files.csv", newline="", encoding="utf-8") as f:
    ROW = next(row for row in csv.DictReader(f) if row["file_name"] == "PSI-10_Engineering Documents_ACME Engineering Implementation Rpt..pdf")
GOOD = "https://psi-repo-prod.s3.amazonaws.com/psi-data/PSI-10/x.pdf?X-Amz-Signature=abc"
# PSI serves older ("legacy") files from a second bucket; seen live on 15 November 2026 (#73).
LEGACY = "https://psi-curation-prod.s3.amazonaws.com/legacy/Filestreamdb/7292/FLEX_EIRD_v4?X-Amz-Signature=abc"
client = TestClient(app, follow_redirects=False)


def fake_psi(answer: bytes):
    return mock.patch.object(psi_links, "fetch", return_value=answer)


class DownloadLink(unittest.TestCase):
    def test_redirects_to_the_link_and_forbids_caching(self):
        with fake_psi(GOOD.encode() + b"\n") as fetch:
            response = client.get(f"/api/files/{ROW['file_id']}/download")
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], GOOD)
        self.assertEqual(response.headers["cache-control"], "no-store")
        fetch.assert_called_once()

    def test_redirects_to_psis_legacy_bucket_too(self):
        with fake_psi(LEGACY.encode() + b"\n"):
            response = client.get(f"/api/files/{ROW['file_id']}/download")
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], LEGACY)

    def test_accepts_exactly_psis_two_buckets(self):
        self.assertEqual(psi_links.LINK_HOSTS, {"psi-repo-prod.s3.amazonaws.com", "psi-curation-prod.s3.amazonaws.com"})

    def test_asks_psi_for_the_right_file(self):
        with fake_psi(GOOD.encode()) as fetch:
            client.get(f"/api/files/{ROW['file_id']}/download")
        url = urllib.parse.urlsplit(fetch.call_args.args[0])
        self.assertEqual(f"{url.scheme}://{url.netloc}{url.path}", f"{psi_links.BASE}/studies/PSI-10/download")
        self.assertEqual(urllib.parse.parse_qs(url.query), {"file": [ROW["file_name"]], "redirect": ["false"]})

    def test_unknown_file_is_404_without_asking_psi(self):
        with fake_psi(GOOD.encode()) as fetch:
            response = client.get("/api/files/not-a-file/download")
        self.assertEqual(response.status_code, 404)
        fetch.assert_not_called()

    def test_refuses_anything_but_psi_storage(self):
        lookalikes = [
            answer
            for host in sorted(psi_links.LINK_HOSTS)
            for answer in (
                f"https://{host}.evil.example/x.pdf",
                f"http://{host}/x.pdf",
                f"https://user@{host}/x.pdf",
                f"https://{host}:8443/x.pdf",
                f"https://{host}/x.pdf\r\nSet-Cookie: a=b",
            )
        ]
        for answer in (
            "https://example.com/x.pdf",
            "https://psi-other-prod.s3.amazonaws.com/x.pdf",
            *lookalikes,
            '{"message": "File not found"}',
            "",
        ):
            with self.subTest(answer=answer), fake_psi(answer.encode()):
                response = client.get(f"/api/files/{ROW['file_id']}/download")
                self.assertEqual(response.status_code, 502)
                self.assertNotIn("location", response.headers)

    def test_psi_unreachable_is_502(self):
        error = urllib.error.URLError("timed out")
        with mock.patch.object(psi_links.urllib.request, "urlopen", side_effect=error):
            response = client.get(f"/api/files/{ROW['file_id']}/download")
        self.assertEqual(response.status_code, 502)
        self.assertIn("PSI did not answer", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
