"""Search inside PSI documents. One endpoint, used by both the search page and the assistant."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app import catalogue, search

router = APIRouter(prefix="/api", tags=["search"])


class SearchHit(BaseModel):
    """One passage of about 150 words, with the investigation it belongs to."""

    accession: str
    title: str
    investigationAcronym: str
    doi: str
    file_id: str
    file_name: str  # PSI's name; a download link is asked for by this name
    category: str
    page: int | None  # PDF page or slide number, from 1; None for Word documents
    snippet: str  # the best-matching stretch, matched words between [[ and ]]
    text: str  # the whole passage, plain text as extracted from NASA's document


class SearchPage(BaseModel):
    query: str
    total: int  # matching passages, before paging
    limit: int
    offset: int
    items: list[SearchHit]


@router.get("/search")
def search_documents(
    q: Annotated[str, Query(min_length=1, max_length=300, description="Words or a question")],
    accession: str | None = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SearchPage:
    """Passages from PSI documents that match any word of `q`, best first."""
    records = catalogue.investigations()
    if accession is not None and accession not in records:
        raise HTTPException(status_code=404, detail=f"No investigation {accession!r} in the catalogue")
    if not search.words(q):
        raise HTTPException(status_code=422, detail="The query has no words to search for")
    try:
        total, hits = search.search(q, accession, limit, offset)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    items = []
    for hit in hits:
        record = records[hit["accession"]]
        items.append(SearchHit(**hit, title=record["title"], doi=record["doi"],
                               investigationAcronym=record["investigationAcronym"]))
    return SearchPage(query=q, total=total, limit=limit, offset=offset, items=items)
