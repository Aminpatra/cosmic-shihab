"""Download links for PSI files, asked from PSI on each request and never stored."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app import catalogue
from app.services import psi_links

router = APIRouter(prefix="/api", tags=["downloads"])


@router.get(
    "/files/{file_id}/download",
    response_class=RedirectResponse,
    status_code=307,
    responses={
        404: {"description": "No file with this id in the catalogue"},
        502: {"description": "PSI did not give a usable link"},
    },
)
def download(file_id: str) -> RedirectResponse:
    """Redirect to a fresh PSI link for one catalogue file. The link expires after about an hour.

    Only files in the catalogue can be asked for, so this never fetches anything else from PSI.
    """
    row = next((row for row in catalogue.files() if row["file_id"] == file_id), None)
    if row is None:
        raise HTTPException(status_code=404, detail=f"No file {file_id!r} in the catalogue")
    try:
        link = psi_links.download_link(row["accession"], row["file_name"])
    except psi_links.PSILinkError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return RedirectResponse(link, status_code=307, headers={"Cache-Control": "no-store"})
