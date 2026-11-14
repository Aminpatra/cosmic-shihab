"""Read-only endpoints for PSI's experimental tables, processed by pipeline/process_tables.py.

Every cell keeps PSI's original text in `raw`; what FLARE read from it sits beside it, and the
comparable conditions are under `standard`. The shape is in backend/data/README.md.
"""

from typing import Annotated, Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app import catalogue, runs

router = APIRouter(prefix="/api", tags=["runs"])

# What one row stands for. Only `test` rows are single tests; count the others separately.
RowIs = Literal["test", "test_day", "session", "fuel_summary", "published_figure"]


class Column(BaseModel):
    name: str  # PSI's header, exactly, spaces included
    unit: str | None  # the unit the header states, in FLARE's spelling; None when it states none
    unit_inferred: bool = False  # True where the header states no unit and FLARE assumed one


class TableSummary(BaseModel):
    accession: str
    file: str  # the table's name in datasets/, unchanged from PSI
    psi_file_name: str
    doi_url: str
    encoding: str
    row_is: RowIs
    row_count: int
    columns: list[Column]
    standard_columns: dict[str, str]  # FLARE field -> the PSI column it comes from


class RowPage(BaseModel):
    total: int  # rows matching the filters, before paging
    limit: int
    offset: int
    items: list[dict[str, Any]]


def _check_accession(accession: str) -> None:
    if accession not in catalogue.investigations():
        raise HTTPException(status_code=404, detail=f"No investigation {accession!r} in the catalogue")


@router.get("/runs")
def list_tables(accession: str | None = None) -> list[TableSummary]:
    """The 22 experimental tables, without their rows. An investigation with no table gives []."""
    if accession is not None:
        _check_accession(accession)
    return [TableSummary(**t) for t in runs.tables() if accession is None or t["accession"] == accession]


@router.get("/runs/rows")
def list_rows(
    accession: str | None = None,
    table: str | None = None,
    cells: bool = True,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> RowPage:
    """Rows in accession, table and line order. `cells=false` leaves out the per-column cells and
    keeps `standard`, which is enough for charts across investigations."""
    if accession is not None:
        _check_accession(accession)
    if table is not None and all(t["file"] != table for t in runs.tables()):
        raise HTTPException(status_code=404, detail=f"No experimental table {table!r}")
    matching = runs.rows(accession, table)
    page = matching[offset : offset + limit]
    if not cells:
        page = [{k: v for k, v in row.items() if k != "cells"} for row in page]
    return RowPage(total=len(matching), limit=limit, offset=offset, items=page)
