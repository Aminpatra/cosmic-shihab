"""Ask PSI for a file's download link at the moment a user opens it.

PSI answers with a presigned S3 URL that expires after about an hour, so FLARE never stores it.
The call is number 4 under "How PSI must be read" in docs/DATA_PLAN.md. The pipeline has its own
copy (pipeline/psi_client.py) because the deployed backend cannot import from pipeline/.
"""

import urllib.error
import urllib.parse
import urllib.request

BASE = "https://psi.nasa.gov/geode-py/ws"
LINK_HOST = "psi-repo-prod.s3.amazonaws.com"
USER_AGENT = "FLARE-SpaceApps-2026 (student research project)"
TIMEOUT_SECONDS = 20


class PSILinkError(RuntimeError):
    """PSI did not answer with a usable download link."""


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.read(65536)  # a presigned link is a few KB
    except (urllib.error.URLError, TimeoutError) as error:  # HTTPError is a URLError
        raise PSILinkError(f"PSI did not answer: {error}") from error


def download_link(accession: str, file_name: str) -> str:
    """A fresh link to one PSI file, refused unless it points at PSI's own S3 storage."""
    query = urllib.parse.urlencode({"file": file_name, "redirect": "false"})
    raw = fetch(f"{BASE}/studies/{urllib.parse.quote(accession)}/download?{query}")
    link = raw.decode(errors="replace").strip()
    parts = urllib.parse.urlsplit(link)
    # netloc must be the bare host: no user info, no port, no lookalike suffix.
    if parts.scheme != "https" or parts.netloc != LINK_HOST or any(c.isspace() for c in link):
        raise PSILinkError(f"PSI answered with something other than a {LINK_HOST} link: {link[:80]!r}")
    return link
