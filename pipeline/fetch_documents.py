"""Download the PSI documents that FLARE's search index reads.

    python3 pipeline/fetch_documents.py                # all of them; skips what is cached
    python3 pipeline/fetch_documents.py --only PSI-69  # one or more investigations

Which documents: every file PSI lists as a document (files.csv `kind`), except the "Raw Data"
category, whose documents are test sheets and flow traces rather than reports. Of those, only
the formats build_search_index.py can read are downloaded (READABLE).

Files go to .cache/psi/documents/<accession>/<file_id><extension> (ignored by git). PSI's file
names can hold characters Windows refuses, such as ":", so the cache is keyed by PSI's file id.
A file already cached at the size PSI lists is skipped, so a second run downloads nothing.
Each download link is one request to PSI, followed by a pause of PAUSE seconds; the file
itself comes from S3. One failed file does not stop the run; rerun to pick it up.

SI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psi_client as psi  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_CSV = os.path.join(ROOT, "backend", "data", "files.csv")
CACHE = os.path.join(ROOT, ".cache", "psi", "documents")
PAUSE = 1.0  # seconds after each call to PSI: at most one request a second
READABLE = (".pdf", ".docx", ".pptx")
# Both of PSI's buckets: every file's size is checked against PSI's list, so a link to the older
# bucket is as safe here as one to the current bucket.
BUCKETS = (psi.S3_PREFIX, psi.LEGACY_S3_PREFIX)


def document_link(accession: str, file_name: str, fetch=psi.fetch_bytes) -> str:
    return psi.download_url(accession, file_name, fetch, allowed=BUCKETS)


def documents(files_csv: str = FILES_CSV) -> list[dict]:
    """The documents the search covers, readable or not, in files.csv order."""
    with open(files_csv, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    chosen = [row for row in rows if row["kind"] == "document" and row["category"] != "Raw Data"]
    for row in chosen:
        row["bytes"] = int(row["bytes"])
    return chosen


def cached_path(row: dict, cache: str = CACHE) -> str:
    return os.path.join(cache, row["accession"], row["file_id"] + row["extension"].lower())


def is_cached(row: dict, cache: str = CACHE) -> bool:
    path = cached_path(row, cache)
    return os.path.exists(path) and os.path.getsize(path) == row["bytes"]


def fetch_all(rows, cache=CACHE, link=document_link, get=psi.fetch_bytes, sleep=time.sleep):
    """Download every readable, uncached row. Returns (downloaded, skipped, failures)."""
    downloaded, skipped, failures = 0, 0, []
    for row in rows:
        if row["extension"].lower() not in READABLE or is_cached(row, cache):
            skipped += 1
            continue
        try:
            url = link(row["accession"], row["file_name"])
            sleep(PAUSE)
            data = get(url, timeout=900)
            if len(data) != row["bytes"]:
                raise psi.PSIFormatError(f"got {len(data)} bytes, PSI lists {row['bytes']}")
            psi.save_atomic(cached_path(row, cache), data)
            downloaded += 1
            print(f"  {row['accession']} {row['file_name']} ({row['bytes'] / 1e6:.1f} MB)", flush=True)
        except (psi.PSIFormatError, OSError) as error:
            failures.append((row["accession"], row["file_name"], str(error)))
            print(f"  FAILED {row['accession']} {row['file_name']}: {error}", flush=True)
    return downloaded, skipped, failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", nargs="+", metavar="ACCESSION")
    args = parser.parse_args()
    rows = [row for row in documents() if not args.only or row["accession"] in args.only]
    readable = [row for row in rows if row["extension"].lower() in READABLE]
    print(f"{len(rows)} documents, {len(readable)} in a readable format "
          f"({sum(row['bytes'] for row in readable) / 1e6:.0f} MB)", flush=True)
    downloaded, skipped, failures = fetch_all(rows)
    print(f"downloaded {downloaded}, skipped {skipped} (cached or unreadable), failed {len(failures)}")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
