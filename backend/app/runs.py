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
