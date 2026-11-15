"""Harvest PSI's combustion investigations: records, file lists, experimental tables.

    python3 pipeline/harvest.py                 # everything; skips what is cached
    python3 pipeline/harvest.py --only PSI-142  # one or more investigations

Raw API responses go to .cache/psi/raw/ (ignored by git). The small
"Experimental table" files go to datasets/, unchanged. Nothing else is
downloaded: PSI holds 13.5 TB and over 99% of it is zips and video.

Run pipeline/build_catalogue.py afterwards to write backend/data/.

SI use: written with Claude Code (Claude Fable 5.2), reviewed by the team.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psi_client as psi  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, ".cache", "psi", "raw")
DATASETS = os.path.join(ROOT, "datasets")
PAUSE = 1.0  # seconds between calls to PSI


def cached_json(path: str, what: str):
    """Return the parsed cached response, or None if it is absent or broken."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as handle:
            return psi.parse_json(handle.read(), what)
    except psi.PSIFormatError:
        return None


def harvest_one(accession: str) -> None:
    record_path = os.path.join(RAW, f"inv_{accession}.json")
    record = cached_json(record_path, accession)
    if record is None:
        raw = psi.fetch_bytes(psi.record_url(accession))
        record = psi.parse_json(raw, f"{accession} record")
        psi.check_record(record, accession)
        psi.save_atomic(record_path, raw)
        time.sleep(PAUSE)
    psi.check_record(record, accession)

    files_path = os.path.join(RAW, f"files_{accession}.json")
    tree = cached_json(files_path, f"{accession} file list")
    if tree is None:
        raw = psi.fetch_bytes(psi.FILES_URL, psi.files_body(accession, record["version"]))
        tree = psi.parse_json(raw, f"{accession} file list")
        psi.flatten_files(tree)
        psi.save_atomic(files_path, raw)
        time.sleep(PAUSE)

    listed, declared = psi.listed_bytes(tree), float(record["totalFileSize"] or 0)
    if abs(listed - declared) > 0.001 * max(declared, 1):
        raise psi.PSIFormatError(
            f"{accession}: file list adds up to {listed:.0f} bytes, record declares {declared:.0f}"
        )

    files = psi.flatten_files(tree)
    for entry in files:
        if entry["category"] != "Experimental table":
            continue
        target = os.path.join(DATASETS, entry["file_name"])
        if os.path.exists(target) and os.path.getsize(target) == entry["bytes"]:
            continue
        link = psi.download_url(accession, entry["file_name"])
        data = psi.fetch_bytes(link, timeout=120)
        if len(data) != entry["bytes"]:
            raise psi.PSIFormatError(
                f"{entry['file_name']}: got {len(data)} bytes, PSI lists {entry['bytes']}"
            )
        psi.save_atomic(target, data)
        print(f"  downloaded {entry['file_name']}")
        time.sleep(PAUSE)
    print(f"{accession}: {len(files)} files, {listed / 1e9:.1f} GB listed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", nargs="+", metavar="ACCESSION")
    args = parser.parse_args()
    accessions = args.only or psi.list_combustion_accessions()
    print(f"{len(accessions)} investigations")
    for accession in accessions:
        harvest_one(accession)


if __name__ == "__main__":
    main()
