"""Comparison readings: the ranking document, the generator with the model faked, and the endpoint.

No test calls Anthropic. Run from backend/: python -m unittest discover -s tests -v
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest import mock

from fastapi.testclient import TestClient

from app import ranking
from app.routes import assistant as assistant_routes
from main import app

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "pipeline"))
import write_summaries  # noqa: E402

client = TestClient(app)


class FakeClient:
    def __init__(self, response):
        self.calls = []
        self.beta = NS(messages=NS(create=lambda **kwargs: self.calls.append(kwargs) or response))


def reply(*blocks):
    return NS(content=list(blocks), stop_reason="end_turn", model="claude-opus-5-5")


def text(value, *cited):
    citations = [NS(type="char_location", document_index=i, cited_text=t) for i, t in cited] or None
    return NS(type="text", text=value, citations=citations)


def live(name):
    return ranking.rank(ranking.Scenario(**write_summaries.PRESETS[name]["scenario"]))


class RankingDocument(unittest.TestCase):
    def test_lists_the_live_order_with_the_notice_and_gravity_note(self):
        result = live("lunar-base")
        source = write_summaries.ranking_source("lunar-base", write_summaries.PRESETS["lunar-base"], result)
        self.assertEqual(source["kind"], "ranking")
        self.assertEqual(source["url"], "/api/rank?environment=lunar&oxygen=0.3&pressure=0.6941")
        lines = source["text"].splitlines()
        listed = [line for line in lines if line[:2] in {f"{n}." for n in range(1, 6)}]
        for line, item in zip(listed, result["items"]):
            self.assertIn(f"({item['accession']}), relevance score {item['score']} of 100", line)
        self.assertIn(ranking.NOTICE, source["text"])
        self.assertIn("not partial gravity", source["text"])
        self.assertIn("10.2 psi", source["text"])

    def test_no_preset_without_a_stated_source(self):
        for preset in write_summaries.PRESETS.values():
            self.assertIn("Flame in Freefall", preset["source"])


class Generator(unittest.TestCase):
    def test_reading_cites_the_ranking_and_keeps_its_order(self):
        fake = FakeClient(reply(text("FLEX ranks first.", (0, "1. FLEX (PSI-69), relevance score 100")),
                                text("This is not a safety assessment.")))
        reading = write_summaries.read_ranking("lunar-base", fake)
        self.assertEqual(reading["sources"][0]["id"], "ranking:lunar-base")
        self.assertEqual(reading["blocks"][0]["citations"][0]["source_id"], "ranking:lunar-base")
        self.assertEqual(reading["blocks"][1]["kind"], "explanation")
        expected = [item["accession"] for item in live("lunar-base")["items"][:write_summaries.TOP]]
        self.assertEqual([item["accession"] for item in reading["top"]], expected)
        self.assertFalse(reading["reviewed"])
        self.assertIsNone(reading["reviewed_by"])
        self.assertIn("AI-generated", reading["note"])
        sent = fake.calls[0]["messages"][0]["content"]
        self.assertEqual(sent[0]["title"], "FLARE ranking for Moon base or pressurized rover")
        self.assertIn("do not re-rank", sent[-1]["text"])  # the instruction forbids re-ranking


class Endpoint(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        patcher = mock.patch.object(assistant_routes, "READINGS_DIR", Path(self.folder.name))
        patcher.start()
        self.addCleanup(patcher.stop)

    def store(self, name, top):
        fake = FakeClient(reply(text("FLEX ranks first.", (0, "FLEX"))))
        reading = write_summaries.read_ranking(name, fake)
        reading["top"] = top or reading["top"]
        Path(self.folder.name, f"{name}.json").write_text(json.dumps(reading), encoding="utf-8")

    def test_empty_when_none_written(self):
        self.assertEqual(client.get("/api/assistant/readings").json(), [])

    def test_serves_a_stored_reading_and_says_it_is_current(self):
        self.store("sea-level-air", None)
        body = client.get("/api/assistant/readings").json()
        self.assertEqual([r["preset"] for r in body], ["sea-level-air"])
        self.assertTrue(body[0]["current"])
        self.assertEqual(body[0]["sources"][0]["kind"], "ranking")

    def test_flags_a_reading_whose_ranking_has_moved(self):
        self.store("spacesuit", [{"accession": "PSI-25", "label": "BASS-II", "score": 99}])
        self.assertFalse(client.get("/api/assistant/readings").json()[0]["current"])


if __name__ == "__main__":
    unittest.main()
