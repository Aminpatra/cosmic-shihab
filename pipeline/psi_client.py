"""Read NASA's Physical Sciences Informatics (PSI) repository.

The PSI API is undocumented, so every function here checks the shape of what it
gets back and raises PSIFormatError when it is not what we saw on 2026-11-14.
How the API behaves, and the traps in it, are written up in docs/DATA_PLAN.md.

AI use: this file was written with Claude Code (Claude Fable 5.2) and reviewed
by the team. It fetches NASA data; it never alters or generates any.
"""

from __future__ import annotations

import gzip
import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://psi.nasa.gov/geode-py/ws"
S3_PREFIX = "https://psi-repo-prod.s3.amazonaws.com/"
PAGE_URL = "https://psi.nasa.gov/physci/repo/data/investigations/{accession}"
USER_AGENT = "FLARE-SpaceApps-2026 (student research project)"

# Fields of an investigation record that the rest of FLARE relies on.
RECORD_KEYS = ("accession", "title", "doi", "version", "totalFileSize", "researchArea")


class PSIFormatError(RuntimeError):
    """PSI answered, but not in the format this code was written against."""


def fetch_bytes(url: str, body: dict | None = None, timeout: int = 900) -> bytes:
    """GET (or POST when a body is given) and return the decoded response body.

    Records can be 8 MB and take two minutes; without gzip one of them arrived
    cut short, so gzip is always requested and the timeout is long.
    """
    headers = {"Accept-Encoding": "gzip", "User-Agent": USER_AGENT}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            if response.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return raw
    except urllib.error.HTTPError as error:
        detail = error.read()[:200].decode(errors="replace")
        raise PSIFormatError(f"{url} answered HTTP {error.code}: {detail}") from error


def parse_json(raw: bytes, what: str):
    """Parse a response, turning a cut-short or non-JSON body into a clear error."""
    try:
        return json.loads(raw)
    except ValueError as error:
        raise PSIFormatError(f"{what}: response is not complete JSON ({error})") from error


def search_url(offset: int) -> str:
    return f"{BASE}/repo/search?term=combustion&source=psi&type=investigation&from={offset}"


def list_combustion_accessions(fetch=fetch_bytes) -> list[str]:
    """Page through the search and keep the Combustion Science investigations."""
    accessions: list[str] = []
    offset = 0
    while True:
        page = parse_json(fetch(search_url(offset)), f"search page from={offset}")
        try:
            hits = page["hits"]["hits"]
            total = page["hits"]["total"]
        except (KeyError, TypeError) as error:
            raise PSIFormatError("search page has no hits.hits / hits.total") from error
        if not isinstance(hits, list) or not isinstance(total, int):
            raise PSIFormatError("search page: hits.hits is not a list or hits.total not a number")
        for hit in hits:
            try:
                source = hit["_source"]
                accession, area = source["Accession"], source["Research Area"]
            except (KeyError, TypeError) as error:
                raise PSIFormatError("search hit lacks _source.Accession / Research Area") from error
            if area == "Combustion Science":
                accessions.append(accession)
        offset += len(hits)
        if not hits or offset >= total:
            break
    return accessions


def record_url(accession: str) -> str:
    return f"{BASE}/repo/investigations/{accession}"


def check_record(record, accession: str) -> dict:
    """Make sure a record is the one asked for and has the fields we rely on."""
    if not isinstance(record, dict):
        raise PSIFormatError(f"{accession}: record is not an object")
    missing = [key for key in RECORD_KEYS if key not in record]
    if missing:
        raise PSIFormatError(f"{accession}: record lacks {missing}")
    if record["accession"] != accession:
        raise PSIFormatError(f"asked for {accession}, got {record['accession']}")
    return record


FILES_URL = f"{BASE}/files/v2"


def files_body(accession: str, version: int) -> dict:
    """The file list needs the record's version; without it PSI answers 400."""
    return {"folder": "psi-data/", "fileType": "study", "studyId": accession, "version": version}


def _leaves(nodes, category, out):
    for node in nodes:
        here = category or node.get("displayName")
        if node.get("directory") is False:
            out.append((node, node.get("sortingCategory") or here))
        _leaves(node.get("files") or [], here, out)


def listed_bytes(tree) -> float:
    """Sum of every listed entry, repeats included.

    PSI's totalFileSize equals this sum, which makes it a completeness check.
    """
    out: list = []
    _leaves(_tree_files(tree), None, out)
    return sum(float(node.get("bytes_size") or 0) for node, _ in out)


def _tree_files(tree):
    if not isinstance(tree, dict) or not isinstance(tree.get("files"), list):
        raise PSIFormatError("file list has no top-level 'files' list")
    return tree["files"]


def flatten_files(tree) -> list[dict]:
    """Turn PSI's folder tree into one row per file.

    The record's added/removed/modified lists are a change log, not the file
    list; this tree is the only correct source. PSI repeats some entries, so
    rows are de-duplicated by id.
    """
    out: list = []
    _leaves(_tree_files(tree), None, out)
    seen: dict[str, dict] = {}
    for node, category in out:
        try:
            file_id, key = node["id"], node["key"]
        except KeyError as error:
            raise PSIFormatError(f"file entry lacks {error}") from error
        name = key.rsplit("/", 1)[-1]
        seen[file_id] = {
            "file_id": file_id,
            "file_name": name,
            "category": category or "",
            "subcategory": node.get("subcategory") or "",
            "extension": os.path.splitext(name)[1].strip().lower(),
            "bytes": int(float(node.get("bytes_size") or 0)),
            "version": node.get("version"),
            "updated": node.get("updated") or "",
            "status": node.get("status"),
            "restricted": bool(node.get("restricted") or node.get("restrictedAccess")),
            "visible": node.get("visible"),
        }
    return list(seen.values())


def download_url(accession: str, file_name: str, fetch=fetch_bytes) -> str:
    """Ask PSI for a download link. It is a presigned S3 URL that expires after
    about an hour, so callers use it at once and never store it."""
    query = urllib.parse.urlencode({"file": file_name, "redirect": "false"})
    url = f"{BASE}/studies/{urllib.parse.quote(accession)}/download?{query}"
    link = fetch(url).decode(errors="replace").strip()
    if not link.startswith(S3_PREFIX):
        raise PSIFormatError(f"{accession}/{file_name}: unexpected download link {link[:60]!r}")
    return link


def save_atomic(path: str, data: bytes) -> None:
    """Write to a temporary name, then rename, so a failed run leaves no half file."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    temporary = path + ".part"
    with open(temporary, "wb") as handle:
        handle.write(data)
    os.replace(temporary, path)
