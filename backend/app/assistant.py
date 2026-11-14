"""The research assistant: answers a question from FLARE's NASA sources, with citations.

Two steps, kept apart so the second can be skipped:

1. `gather` collects the evidence: the PSI records of the investigations a question names (or the
   caller picks) and the best-matching passages from PSI's documents (backend/data/search.sqlite).
2. `answer` sends that evidence to Claude Opus 5.5 as documents with citations turned on. Every
   sentence Claude bases on a source comes back tied to the exact passage; sentences without a
   citation are marked as the assistant's own explanation.

Without ANTHROPIC_API_KEY, or when the call fails or is declined, the answer is retrieval only: the
sources themselves, with their links, and no generated prose. The assistant never touches the
ranking (#7); it only reads the catalogue.

AI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

from __future__ import annotations

import logging
import os
import re

from app import catalogue, search

log = logging.getLogger(__name__)

MODEL = "claude-opus-5-5"
MAX_INVESTIGATIONS = 4  # records sent with one question
MAX_PASSAGES = 8  # document passages sent with one question
PAGE_URL = "https://psi.nasa.gov/physci/repo/data/investigations/{accession}"

SYSTEM = """You are FLARE's research assistant. You help researchers and mission planners read \
NASA's microgravity combustion investigations from the Physical Sciences Informatics (PSI) \
repository.

You answer only from the documents given with the question: PSI investigation records and \
passages from PSI documents. Rules:
- Base every factual statement on the documents, so that it carries a citation.
- If the documents do not answer the question, or answer only part of it, say plainly what is \
missing. Do not fill the gap from general knowledge.
- Never invent or estimate experimental results, conditions, materials or numbers.
- You may explain terms or connect findings in your own words; keep such explanation short and \
clearly separate from what the sources say.
- Do not give safety recommendations or operational advice for spacecraft. If asked, say that \
FLARE reports what NASA's investigations found and that design decisions need qualified review.
- Where investigations used different conditions or measures, say so rather than merging them.
Write in plain English for a technical reader, in short paragraphs, without headings."""

_STOP = set("""a about after all also an and any are as at be been being but by can could did do
does each for from had has have how i if in into is it its may more most of on or our should so
some such than that the their them then there these they this those to under up was we were what
when where which while who why will with would you your""".split())


def key_present() -> bool:
    """The deployment decides by the environment alone (docs/DECISIONS.md, #10)."""
    return bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


def _names() -> list[tuple[str, str]]:
    """(name, accession) for every acronym and accession, longest name first.

    Longest first, so "FLEX-2" is found before "FLEX" and "BASS-II" before "BASS". Acronyms such
    as "DAFT / DAFT-2" contribute each part.
    """
    pairs = []
    for accession, record in catalogue.investigations().items():
        pairs.append((accession, accession))
        for part in record["investigationAcronym"].split("/"):
            if part.strip():
                pairs.append((part.strip(), accession))
    return sorted(pairs, key=lambda pair: -len(pair[0]))


def named_investigations(question: str) -> list[str]:
    """Accessions the question names by acronym or accession, in order of first mention."""
    found: dict[str, int] = {}
    taken: list[tuple[int, int]] = []
    for name, accession in _names():
        pattern = r"(?<![\w-])" + re.escape(name) + r"(?![\w-])"
        for match in re.finditer(pattern, question, flags=re.IGNORECASE):
            span = match.span()
            if any(start < span[1] and span[0] < end for start, end in taken):
                continue  # inside a longer name already found
            taken.append(span)
            found.setdefault(accession, span[0])
    return sorted(found, key=found.get)


def _record_text(record: dict) -> str:
    """The parts of a PSI record that answer questions, as plain text with labelled fields."""
    tags = record["derived"].get("tags", {}).get("values", {})
    tables = record["derived"]["experimental_tables"]
    lines = [
        f"Investigation: {record['title']} ({record['investigationAcronym'] or record['accession']})",
        f"Accession: {record['accession']}. DOI: {record['doi']}.",
        f"Project type: {record['projectType']}. Flight program: {record['flightProgram'] or 'not stated'}.",
        f"Dates: {record['investigationStartDate'] or 'not stated'} to "
        f"{record['investigationEndDate'] or 'not stated'}.",
        f"Hardware: {record['experimentHardware'] or 'not stated'}.",
    ]
    for label, key in (("Objective", "objective"), ("Hypothesis", "hypothesis"),
                       ("Approach", "approach"), ("Research impacts", "researchImpacts")):
        if record[key].strip():
            lines.append(f"{label}: {' '.join(record[key].split())}")
    if tags:
        lines.append("FLARE's tags (hand-written from this record; see research/investigation_tags.csv): "
                     + "; ".join(f"{key.replace('_', ' ')} = {value}" for key, value in tags.items()) + ".")
    if tables:
        lines.append("Experimental tables held by FLARE: " + "; ".join(
            f"{table['file_name']} ({table['rows']} rows, {table['columns']} columns)" for table in tables) + ".")
    else:
        lines.append("FLARE holds no experimental table for this investigation (catalogue metadata only).")
    return "\n".join(lines)


def _query_words(question: str) -> str:
    kept = [word for word in search.words(question) if word not in _STOP and len(word) > 1]
    return " ".join(kept)


def gather(question: str, accessions: list[str] | None = None) -> list[dict]:
    """The sources for one question: records first, then document passages, best first.

    Each source is {id, kind, accession, title, label, url, text}; document passages also carry
    file_id, file_name and page. Raises KeyError for an accession not in the catalogue.
    """
    records = catalogue.investigations()
    chosen = list(dict.fromkeys(accessions or named_investigations(question)))
    for accession in chosen:
        if accession not in records:
            raise KeyError(accession)
    chosen = chosen[:MAX_INVESTIGATIONS]

    sources = []
    for accession in chosen:
        record = records[accession]
        sources.append({
            "id": f"record:{accession}",
            "kind": "record",
            "accession": accession,
            "title": f"PSI record {accession}: {record['title']}",
            "label": record["investigationAcronym"] or accession,
            "url": PAGE_URL.format(accession=accession),
            "doi": record["doi"],
            "text": _record_text(record),
        })

    words = _query_words(question)
    hits: list[dict] = []
    if words:
        try:
            if chosen:
                share = max(1, MAX_PASSAGES // len(chosen))
                for accession in chosen:
                    hits.extend(search.search(words, accession, share)[1])
            else:
                hits = search.search(words, None, MAX_PASSAGES)[1]
        except FileNotFoundError:
            hits = []  # no document index in this deployment: records only
    for hit in hits[:MAX_PASSAGES]:
        record = records[hit["accession"]]
        page = f", page {hit['page']}" if hit["page"] else ""
        sources.append({
            "id": f"passage:{hit['file_id']}:{hit['page'] or 0}",
            "kind": "document",
            "accession": hit["accession"],
            "title": f"{hit['file_name']}{page} ({record['investigationAcronym'] or hit['accession']})",
            "label": record["investigationAcronym"] or hit["accession"],
            "url": f"/api/files/{hit['file_id']}/download",
            "doi": record["doi"],
            "file_id": hit["file_id"],
            "file_name": hit["file_name"],
            "page": hit["page"],
            "snippet": hit["snippet"],
            "text": hit["text"],
        })
    return sources


def retrieval_only(question: str, sources: list[dict], reason: str) -> dict:
    """The answer without generated prose: the sources, and why there is nothing more."""
    return {"question": question, "mode": "retrieval_only", "reason": reason,
            "model": None, "blocks": [], "sources": sources}


def _client():
    import anthropic  # imported here so the no-key path needs no SDK at all

    return anthropic.Anthropic()


def generate(question: str, sources: list[dict], client=None) -> dict:
    """Ask Claude with the sources attached as cited documents; returns the answer dict.

    Raises the SDK's errors; `answer` turns them into a retrieval-only reply.
    """
    client = client or _client()
    documents = [
        {"type": "document",
         "source": {"type": "text", "media_type": "text/plain", "data": source["text"]},
         "title": source["title"],
         "citations": {"enabled": True}}
        for source in sources
    ]
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        output_config={"effort": "medium"},
        # On a policy decline the API reruns the request on a fallback model inside this call.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": [*documents, {"type": "text", "text": question}]}],
    )
    if response.stop_reason == "refusal":
        return retrieval_only(question, sources, "The model declined to answer; these are the matching sources.")

    blocks = []
    for block in response.content:
        if block.type != "text" or not block.text:
            continue
        citations = []
        for citation in block.citations or []:
            index = getattr(citation, "document_index", None)
            if index is None or not 0 <= index < len(sources):
                continue
            citations.append({"source_id": sources[index]["id"], "cited_text": citation.cited_text})
        blocks.append({"text": block.text,
                       "kind": "source" if citations else "explanation",
                       "citations": citations})
    if response.stop_reason == "max_tokens":
        blocks.append({"text": " [The answer was cut off at the length limit.]",
                       "kind": "explanation", "citations": []})
    return {"question": question, "mode": "generated", "reason": None,
            "model": response.model, "blocks": blocks, "sources": sources}


def answer(question: str, accessions: list[str] | None = None, client=None) -> dict:
    """The full reply to one question. Raises KeyError for an unknown accession."""
    sources = gather(question, accessions)
    if not sources:
        return retrieval_only(question, [], "No NASA source in FLARE matches this question.")
    if client is None and not key_present():
        return retrieval_only(question, sources,
                              "No AI key is configured, so FLARE shows the matching NASA sources "
                              "without a generated answer.")
    import anthropic

    try:
        return generate(question, sources, client)
    except anthropic.APIError as error:  # status errors, timeouts, network failures
        log.warning("assistant: Claude call failed: %r", error)
        name = type(error).__name__
        return retrieval_only(question, sources,
                              f"The AI service could not answer ({name}); these are the matching sources.")
