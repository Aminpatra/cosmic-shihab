"""Read-only access to the processed experimental tables in backend/data/runs/.

The files are written by pipeline/process_tables.py (#12) and never changed here; the row shape is
described in backend/data/README.md. Loaded once per process, on first use.
"""

import json
from functools import cache

from app.catalogue import DATA_DIR, _accession_number

RUNS_DIR = DATA_DIR / "runs"


@cache
def investigations() -> dict[str, dict]:
    """Each investigation's tables, rows included, keyed by accession, in accession-number order."""
    entries = {}
    for path in RUNS_DIR.glob("*.json"):
        entry = json.loads(path.read_text(encoding="utf-8"))
        if entry.get("accession") != path.stem:
            raise ValueError(f"{path.name} holds accession {entry.get('accession')!r}")
        for table in entry["tables"]:
            if table["row_count"] != len(table["rows"]):
                raise ValueError(f"{table['file']}: row_count {table['row_count']} but {len(table['rows'])} rows")
        entries[path.stem] = entry
    if not entries:
        raise FileNotFoundError(f"No run files in {RUNS_DIR}")
    return dict(sorted(entries.items(), key=lambda item: _accession_number(item[0])))


def tables() -> list[dict]:
    """Every table with its accession, in accession then file order."""
    return [table | {"accession": accession}
            for accession, entry in investigations().items() for table in entry["tables"]]


def rows(accession: str | None = None, table: str | None = None) -> list[dict]:
    """Rows as stored, each with the `accession` and `table` (file name) it came from."""
    return [
        {"accession": t["accession"], "table": t["file"]} | row
        for t in tables()
        if (accession is None or t["accession"] == accession) and (table is None or t["file"] == table)
        for row in t["rows"]
    ]
