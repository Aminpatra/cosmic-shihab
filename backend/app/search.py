"""Keyword search over PSI documents, read from backend/data/search.sqlite.

The file is written by pipeline/build_search_index.py (its docstring describes the tables) and is
opened read-only, because Vercel's filesystem is. A query's words are each quoted and joined with
OR, so a whole question works as well as a keyword, and nothing the user types can reach FTS5's
query syntax. Results are ordered by BM25, best first.
"""

import re
import sqlite3
from pathlib import Path

from app.catalogue import DATA_DIR

INDEX: Path = DATA_DIR / "search.sqlite"
MARK = ("[[", "]]")  # around matched words in a snippet; the text itself is plain, never HTML

_HITS = """
SELECT d.accession, d.file_id, d.file_name, d.category, passages.page,
       snippet(passages, 0, ?, ?, ' … ', 32), passages.text
FROM passages JOIN documents d USING (file_id)
WHERE passages MATCH ? {extra}
ORDER BY bm25(passages)
LIMIT ? OFFSET ?
"""
_TOTAL = "SELECT count(*) FROM passages JOIN documents d USING (file_id) WHERE passages MATCH ? {extra}"


MAX_TERMS = 32  # words a query searches for; each one more OR term costs time


def words(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def terms(text: str) -> list[str]:
    """The words searched for: each once, in the order typed, at most MAX_TERMS of them.

    A repeated word would add a repeated OR term that slows the query without finding anything new.
    """
    return list(dict.fromkeys(words(text)))[:MAX_TERMS]


def search(text: str, accession: str | None = None, limit: int = 10, offset: int = 0):
    """(total, hits) for a query. Raises FileNotFoundError when the index has not been built."""
    found = terms(text)
    if not found:
        return 0, []
    if not INDEX.exists():
        raise FileNotFoundError(f"{INDEX.name} has not been built; run pipeline/build_search_index.py")
    match = " OR ".join(f'"{word}"' for word in found)
    extra, scope = ("AND d.accession = ?", [accession]) if accession else ("", [])
    db = sqlite3.connect(f"{INDEX.as_uri()}?mode=ro&immutable=1", uri=True)
    try:
        total = db.execute(_TOTAL.format(extra=extra), [match, *scope]).fetchone()[0]
        rows = db.execute(_HITS.format(extra=extra), [*MARK, match, *scope, limit, offset]).fetchall()
    finally:
        db.close()
    keys = ("accession", "file_id", "file_name", "category", "page", "snippet", "text")
    return total, [dict(zip(keys, row)) for row in rows]
