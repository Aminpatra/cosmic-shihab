"""Read-only access to PSI's processed experimental tables in backend/data/runs/.

The files are written by pipeline/process_tables.py (shape in backend/data/README.md) and never
changed here. Loaded once per process, on first use.
"""

import json
from functools import cache

from app.catalogue import DATA_DIR, _accession_number


@cache
def runs() -> dict[str, dict]:
    """Every runs file, keyed by accession, in accession-number order."""
    data = {}
    for path in (DATA_DIR / "runs").glob("*.json"):
        content = json.loads(path.read_text(encoding="utf-8"))
        if content.get("accession") != path.stem:
            raise ValueError(f"{path.name} holds accession {content.get('accession')!r}")
        data[path.stem] = content
    if not data:
        raise FileNotFoundError(f"No runs files in {DATA_DIR / 'runs'}")
    return dict(sorted(data.items(), key=lambda item: _accession_number(item[0])))


def tables() -> list[dict]:
    """Every table with its accession, in accession then file order."""
    return [table | {"accession": accession}
            for accession, entry in runs().items() for table in entry["tables"]]


def rows(accession: str | None = None, table: str | None = None) -> list[dict]:
    """Rows as stored, each with the `accession` and `table` (file name) it came from."""
    return [
        {"accession": t["accession"], "table": t["file"]} | row
        for t in tables()
        if (accession is None or t["accession"] == accession) and (table is None or t["file"] == table)
        for row in t["rows"]
    ]
