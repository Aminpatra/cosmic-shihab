"""The research assistant's endpoints. The logic is in app/assistant.py."""

import json
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app import assistant, catalogue

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


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
    kind: Literal["record", "document"]
    accession: str
    title: str
    label: str  # acronym, or accession when PSI gives none
    url: str  # PSI page for a record; /api/files/{file_id}/download for a document
    doi: str
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
