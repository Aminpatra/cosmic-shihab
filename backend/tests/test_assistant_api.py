"""The assistant: evidence gathering on the real catalogue and index, and the model call faked.

No test calls Anthropic. A fake client returns responses shaped like the SDK's, so the citation
mapping, the refusal and failure paths and the no-key fallback are all checked offline.
Run from backend/: python -m unittest discover -s tests -v
"""

import os
import unittest
from types import SimpleNamespace as NS
from unittest import mock

import anthropic
import httpx2
from fastapi.testclient import TestClient

from app import assistant
from main import app

client = TestClient(app)
NO_KEY = {"ANTHROPIC_API_KEY": ""}


def text(value, *cited):
    """A text block citing (document_index, cited_text) pairs."""
    citations = [NS(type="char_location", document_index=i, cited_text=t) for i, t in cited] or None
    return NS(type="text", text=value, citations=citations)


class FakeClient:
    """Records the request and answers with the given response, or raises the given error."""

    def __init__(self, response=None, error=None):
        self.calls = []
        self.response, self.error = response, error
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


def reply(*blocks, stop="end_turn"):
    return NS(content=list(blocks), stop_reason=stop, model="claude-opus-5-5")


class NamedInvestigations(unittest.TestCase):
    def test_longest_name_wins(self):
        self.assertEqual(assistant.named_investigations("How does FLEX-2 differ from FLEX?"), ["PSI-68", "PSI-69"])
        self.assertEqual(assistant.named_investigations("What did BASS-II burn?"), ["PSI-25"])

    def test_accession_and_case(self):
        self.assertEqual(assistant.named_investigations("tell me about psi-69 and same-r"), ["PSI-69", "PSI-101"])

    def test_part_of_a_combined_acronym(self):
        self.assertEqual(assistant.named_investigations("What was DAFT-2?"), ["PSI-47"])

    def test_no_false_match_inside_words(self):
        self.assertEqual(assistant.named_investigations("Is the reflexive flexibility relevant?"), [])


class Gathering(unittest.TestCase):
    def test_records_come_first_then_passages_of_that_investigation(self):
        sources = assistant.gather("Which suppressants did FLEX test?")
        self.assertEqual(sources[0]["id"], "record:PSI-69")
        self.assertIn("suppressants", sources[0]["text"])
        passages = [s for s in sources if s["kind"] == "document"]
        self.assertTrue(passages, "the FLEX documents in search.sqlite should match")
        self.assertTrue(all(s["accession"] == "PSI-69" for s in passages))
        self.assertTrue(all(s["url"].startswith("/api/files/") for s in passages))
        self.assertLessEqual(len(passages), assistant.MAX_PASSAGES)

    def test_record_text_carries_tags_and_tables(self):
        text_ = assistant.gather("x", ["PSI-60"])[0]["text"]
        self.assertIn("catalogue metadata only", text_)
        self.assertIn("FLARE's tags", text_)

    def test_unknown_accession(self):
        with self.assertRaises(KeyError):
            assistant.gather("anything", ["PSI-9999"])

    def test_nothing_matches(self):
        self.assertEqual(assistant.gather("zzzqx vbnmw"), [])


class Generation(unittest.TestCase):
    def test_request_sends_sources_as_cited_documents(self):
        fake = FakeClient(reply(text("FLEX tested CO2.", (0, "suppressants such as CO2"))))
        result = assistant.answer("Which suppressants did FLEX test?", client=fake)
        call = fake.calls[0]
        self.assertEqual(call["model"], "claude-opus-5-5")
        content = call["messages"][0]["content"]
        documents = [part for part in content if part["type"] == "document"]
        self.assertEqual(len(documents), len(result["sources"]))
        self.assertTrue(all(doc["citations"] == {"enabled": True} for doc in documents))
        self.assertEqual(content[-1], {"type": "text", "text": "Which suppressants did FLEX test?"})

    def test_cited_and_uncited_text_are_told_apart(self):
        fake = FakeClient(reply(
            text("FLEX tested CO2 and helium.", (0, "such as CO2, He")),
            text(" In plain terms, these gases dilute oxygen."),
            text(" Bad index.", (99, "nowhere")),
        ))
        result = assistant.answer("Which suppressants did FLEX test?", client=fake)
        self.assertEqual(result["mode"], "generated")
        kinds = [block["kind"] for block in result["blocks"]]
        self.assertEqual(kinds, ["source", "explanation", "explanation"])
        self.assertEqual(result["blocks"][0]["citations"][0]["source_id"], "record:PSI-69")

    def test_refusal_falls_back_to_sources(self):
        fake = FakeClient(reply(stop="refusal"))
        result = assistant.answer("Which suppressants did FLEX test?", client=fake)
        self.assertEqual(result["mode"], "retrieval_only")
        self.assertTrue(result["sources"])
        self.assertEqual(result["blocks"], [])

    def test_api_failure_falls_back_to_sources(self):
        error = anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages"))
        result = assistant.answer("Which suppressants did FLEX test?", client=FakeClient(error=error))
        self.assertEqual(result["mode"], "retrieval_only")
        self.assertIn("APIConnectionError", result["reason"])
        self.assertTrue(result["sources"])

    def test_cut_off_answer_says_so(self):
        fake = FakeClient(reply(text("FLEX tested", (0, "CO2")), stop="max_tokens"))
        result = assistant.answer("Which suppressants did FLEX test?", client=fake)
        self.assertIn("cut off", result["blocks"][-1]["text"])


@mock.patch.dict(os.environ, NO_KEY)
class Endpoints(unittest.TestCase):
    def test_status_without_key(self):
        self.assertEqual(client.get("/api/assistant/status").json(), {"mode": "retrieval_only", "model": None})

    def test_ask_without_key_is_retrieval_only(self):
        res = client.post("/api/assistant/ask", json={"question": "Which suppressants did FLEX test?"})
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["mode"], "retrieval_only")
        self.assertEqual(body["blocks"], [])
        self.assertIn("No AI key", body["reason"])
        self.assertEqual(body["sources"][0]["id"], "record:PSI-69")

    def test_ask_scoped(self):
        res = client.post("/api/assistant/ask", json={"question": "what materials burned", "accessions": ["PSI-26"]})
        self.assertEqual({s["accession"] for s in res.json()["sources"]}, {"PSI-26"})

    def test_ask_unknown_accession(self):
        res = client.post("/api/assistant/ask", json={"question": "anything at all", "accessions": ["PSI-1"]})
        self.assertEqual(res.status_code, 404)

    def test_ask_rejects_too_many_and_too_short(self):
        many = ["PSI-10", "PSI-20", "PSI-21", "PSI-22", "PSI-23"]
        self.assertEqual(client.post("/api/assistant/ask", json={"question": "abc def", "accessions": many}).status_code, 422)
        self.assertEqual(client.post("/api/assistant/ask", json={"question": "a"}).status_code, 422)

    def test_nothing_found(self):
        body = client.post("/api/assistant/ask", json={"question": "zzzqx vbnmw"}).json()
        self.assertEqual(body["sources"], [])
        self.assertIn("No NASA source", body["reason"])

    def test_summary_absent(self):
        self.assertEqual(client.get("/api/assistant/summaries/PSI-69").status_code, 404)
        self.assertEqual(client.get("/api/assistant/summaries/PSI-1").status_code, 404)

    def test_status_with_key(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            self.assertEqual(client.get("/api/assistant/status").json()["mode"], "generated")


if __name__ == "__main__":
    unittest.main()
