"""Read-only access to the PSI catalogue in backend/data/.

The files are written by pipeline/build_catalogue.py and never changed here. Each is loaded once
per process, on first use.
"""

import csv
import json
from functools import cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _accession_number(accession: str) -> int:
    """PSI-10 -> 10, so investigations sort PSI-10, PSI-25, ..., PSI-159. Fails on any other form."""
    return int(accession.removeprefix("PSI-"))


@cache
def investigations() -> dict[str, dict]:
    """Every investigation record, keyed by accession, in accession-number order."""
    records = {}
    for path in (DATA_DIR / "investigations").glob("*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("accession") != path.stem:
            raise ValueError(f"{path.name} holds accession {record.get('accession')!r}")
        records[path.stem] = record
    if not records:
        raise FileNotFoundError(f"No investigation files in {DATA_DIR / 'investigations'}")
    return dict(sorted(records.items(), key=lambda item: _accession_number(item[0])))


@cache
def files() -> list[dict]:
    """Every row of files.csv, with sizes and versions as integers and blanks as None."""
    with open(DATA_DIR / "files.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["bytes"] = int(row["bytes"])
        row["version"] = int(row["version"])
        row["subcategory"] = row["subcategory"] or None
        row["updated"] = row["updated"] or None
    return rows
