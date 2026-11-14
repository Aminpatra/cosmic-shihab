"""The research assistant's endpoints. The logic is in app/assistant.py."""

import json
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app import assistant, catalogue, ranking

router = APIRouter(prefix="/api/assistant", tags=["assistant"])
READINGS_DIR = catalogue.DATA_DIR / "summaries" / "readings"


class Question(BaseModel):
    question: Annotated[str, Field(min_length=3, max_length=1000)]
    # Investigations to answer about. Empty: those the question names, else all of them.
    accessions: Annotated[list[str], Field(max_length=assistant.MAX_INVESTIGATIONS)] = []


class Citation(BaseModel):
    source_id: str  # an `id` in `sources`
    cited_text: str  # the words of the source the sentence rests on


class Block(BaseModel):
    text: str
    kind: Literal["source", "explanation"]  # "source": rests on a cited passage
    citations: list[Citation]


class Source(BaseModel):
    id: str
    kind: Literal["record", "document", "ranking"]  # "ranking": only in comparison readings
    accession: str  # empty for a ranking
    title: str
    label: str  # acronym, or accession when PSI gives none
    url: str  # PSI page for a record; /api/files/{file_id}/download for a document; /api/rank?... for a ranking
    doi: str  # empty for a ranking
    text: str
    file_id: str | None = None
    file_name: str | None = None
    page: int | None = None
    snippet: str | None = None  # matched words between [[ and ]]


class Answer(BaseModel):
    question: str
    mode: Literal["generated", "retrieval_only"]
    reason: str | None  # why the answer is retrieval only
    model: str | None
    blocks: list[Block]
    sources: list[Source]


class Summary(BaseModel):
    """A stored, AI-generated summary of one investigation (pipeline/write_summaries.py)."""

    accession: str
    note: str
    model: str
    generated: str  # date written, YYYY-MM-DD
    reviewed: bool  # true only after a person read it against its sources
    reviewed_by: str | None
    blocks: list[Block]
    sources: list[Source]


class Ranked(BaseModel):
    accession: str
    label: str
    score: float


class Reading(BaseModel):
    """A stored, AI-generated reading of the ranking for one preset scenario (pipeline/write_summaries.py)."""

    preset: str
    label: str
    scenario: dict[str, str | float]  # /api/rank parameters
    scenario_source: str  # where the scenario's values come from
    ranking_version: str
    top: list[Ranked]  # the ranking's top investigations when the reading was written
    current: bool  # the live ranking still puts the same investigations in the same order
    note: str
    model: str
    generated: str
    reviewed: bool
    reviewed_by: str | None
    blocks: list[Block]
    sources: list[Source]


class Status(BaseModel):
    mode: Literal["generated", "retrieval_only"]
    model: str | None


@router.get("/status")
def status() -> Status:
    """Whether answers are generated (a key is configured) or retrieval only."""
    if assistant.key_present():
        return Status(mode="generated", model=assistant.MODEL)
    return Status(mode="retrieval_only", model=None)


@router.post("/ask")
def ask(body: Question) -> Answer:
    """Answer one question from FLARE's NASA sources, each sentence tied to the source it uses."""
    unknown = [accession for accession in body.accessions if accession not in catalogue.investigations()]
    if unknown:
        raise HTTPException(status_code=404, detail=f"No investigation {unknown[0]!r} in the catalogue")
    return Answer(**assistant.answer(body.question.strip(), body.accessions or None))


@router.get("/summaries/{accession}")
def summary(accession: str) -> Summary:
    """The stored summary of one investigation; 404 when none has been written yet."""
    if accession not in catalogue.investigations():
        raise HTTPException(status_code=404, detail=f"No investigation {accession!r} in the catalogue")
    path = catalogue.DATA_DIR / "summaries" / f"{accession}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No summary of {accession} has been written yet")
    return Summary(**json.loads(path.read_text(encoding="utf-8")))


@router.get("/readings")
def readings() -> list[Reading]:
    """The stored readings of the ranking for the preset scenarios; an empty list when none exist."""
    out = []
    for path in sorted(READINGS_DIR.glob("*.json")):
        stored = json.loads(path.read_text(encoding="utf-8"))
        # A reading explains one ranking. If the data or the method has moved since it was written,
        # say so rather than show an explanation of an order the page no longer displays.
        live = ranking.rank(ranking.Scenario(**stored["scenario"]))["items"][: len(stored["top"])]
        current = [item["accession"] for item in live] == [item["accession"] for item in stored["top"]]
        out.append(Reading(**stored, current=current))
    return out
