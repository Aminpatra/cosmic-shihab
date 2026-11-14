"""Read-only catalogue endpoints: health, investigations and their file lists.

Vercel passes the original path to the backend (/api/x arrives as /api/x), so every route
carries the /api prefix.
"""

from typing import Annotated, Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app import catalogue

router = APIRouter(prefix="/api", tags=["catalogue"])

Kind = Literal["archive_or_video", "document", "table", "text", "numeric", "other"]


class Health(BaseModel):
    status: Literal["ok"]
    investigations: int
    files: int
    retrieved: str  # the day the catalogue was harvested from PSI


class InvestigationSummary(BaseModel):
    """The fields the explorer lists and filters on. PSI's own names; FLARE's additions in `derived`."""

    accession: str
    title: str
    investigationAcronym: str
    doi: str
    licenseIdentifier: str  # "" for PSI-10, which states no licence
    researchArea: str
    subResearchArea: str
    projectType: str
    flightProgram: str
    experimentHardware: str
    investigationStartDate: str  # PSI's format, MM-DD-YYYY
    investigationEndDate: str
    derived: dict[str, Any]


class FileRow(BaseModel):
    accession: str
    file_id: str
    file_name: str
    category: str
    subcategory: str | None
    extension: str
    kind: Kind
    bytes: int
    version: int
    updated: str | None


class FilePage(BaseModel):
    total: int  # rows matching the filters, before paging
    limit: int
    offset: int
    items: list[FileRow]


def _known(accession: str) -> dict:
    record = catalogue.investigations().get(accession)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No investigation {accession!r} in the catalogue")
    return record


@router.get("/health")
def health() -> Health:
    records = catalogue.investigations().values()
    return Health(
        status="ok",
        investigations=len(records),
        files=len(catalogue.files()),
        retrieved=max(record["derived"]["retrieved"] for record in records),
    )


@router.get("/investigations", response_model=list[InvestigationSummary])
def list_investigations() -> Any:
    """All 24 investigations, summary fields only. The full record is at /api/investigations/{accession}."""
    return list(catalogue.investigations().values())


@router.get("/investigations/{accession}")
def get_investigation(accession: str) -> dict[str, Any]:
    """The whole record as stored: PSI's fields unchanged, FLARE's additions under `derived`."""
    return _known(accession)


@router.get("/files")
def list_files(
    accession: str | None = None,
    kind: Kind | None = None,
    category: str | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> FilePage:
    """PSI's file list, filtered and paged. None of the files is stored by FLARE."""
    if accession is not None:
        _known(accession)
    rows = [
        row
        for row in catalogue.files()
        if (accession is None or row["accession"] == accession)
        and (kind is None or row["kind"] == kind)
        and (category is None or row["category"] == category)
    ]
    return FilePage(total=len(rows), limit=limit, offset=offset, items=rows[offset : offset + limit])
