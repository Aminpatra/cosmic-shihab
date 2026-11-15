"""Build FLARE's keyword search index from the downloaded PSI documents.

    python3 pipeline/fetch_documents.py      # first: download the documents into .cache/
    python3 pipeline/build_search_index.py   # then: write backend/data/search.sqlite

The index is one SQLite file with two tables, read by backend/app/search.py:

- `documents`: one row per document the search covers (fetch_documents.documents()), with
  `status` saying whether it made it in: indexed, no_text (nothing readable, for example a scan),
  unreadable_format (.ppt, .doc), not_downloaded, or failed.
- `passages`: an FTS5 full-text table. Each row is about PASSAGE_WORDS words of one page (PDF),
  one slide (PowerPoint) or one stretch of a Word document, with its `file_id` and `page`
  (None for Word, which has no fixed pages). English stemming, so "flames" finds "flame".

The text is NASA's, extracted unchanged apart from joining lines, collapsing whitespace, spelling
out ligature characters ("ﬂ" becomes "fl") and replacing invalid characters with U+FFFD.
PDFs need `pypdf` (pipeline/requirements.txt); Word and PowerPoint use the standard library.

SI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

from __future__ import annotations

import os
import re
import sqlite3
import sys
import unicodedata
import zipfile
from datetime import date
from xml.etree import ElementTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_documents as fd  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "backend", "data", "search.sqlite")
PASSAGE_WORDS = 150

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

SCHEMA = """
CREATE TABLE documents (
    file_id TEXT PRIMARY KEY, accession TEXT NOT NULL, file_name TEXT NOT NULL,
    category TEXT NOT NULL, extension TEXT NOT NULL, bytes INTEGER NOT NULL,
    status TEXT NOT NULL, page_count INTEGER, passage_count INTEGER NOT NULL
);
CREATE VIRTUAL TABLE passages USING fts5(
    text, file_id UNINDEXED, page UNINDEXED, tokenize = 'porter unicode61'
);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def pdf_pages(path: str) -> list[tuple[int, str]]:
    from pypdf import PdfReader  # pipeline-only dependency; see pipeline/requirements.txt

    reader = PdfReader(path)
    return [(number, page.extract_text() or "") for number, page in enumerate(reader.pages, 1)]


def docx_pages(path: str) -> list[tuple[None, str]]:
    with zipfile.ZipFile(path) as archive:
        root = ElementTree.fromstring(archive.read("word/document.xml"))
    paragraphs = ("".join(t.text or "" for t in p.iter(f"{W}t")) for p in root.iter(f"{W}p"))
    return [(None, "\n".join(paragraphs))]


def pptx_pages(path: str) -> list[tuple[int, str]]:
    with zipfile.ZipFile(path) as archive:
        slides = [n for n in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
        slides.sort(key=lambda name: int(re.search(r"\d+", name).group()))
        pages = []
        for number, name in enumerate(slides, 1):
            root = ElementTree.fromstring(archive.read(name))
            pages.append((number, " ".join(t.text or "" for t in root.iter(f"{A}t"))))
    return pages


READERS = {".pdf": pdf_pages, ".docx": docx_pages, ".pptx": pptx_pages}


# PDFs often store "fl", "fi", "ff" as one ligature character ("ﬂame"), which a search for
# "flame" would miss (425 passages on 2026-11-14). Only these seven are spelled out; full NFKC
# would also rewrite superscripts and change how units such as cm² read.
LIGATURES = {code: unicodedata.normalize("NFKC", chr(code)) for code in range(0xFB00, 0xFB07)}


def clean(text: str) -> str:
    """Spell out ligatures, rejoin surrogate pairs and replace lone surrogates with U+FFFD. pypdf
    returns surrogates for some mathematical symbols, and SQLite refuses text that is not UTF-8."""
    text = text.encode("utf-16", "surrogatepass").decode("utf-16", "replace")
    return text.translate(LIGATURES)


def passages(text: str, size: int = PASSAGE_WORDS) -> list[str]:
    words = clean(text).split()
    return [" ".join(words[start : start + size]) for start in range(0, len(words), size)]


def index_one(row: dict, cache: str):
    """(status, pages, [(page, passage), ...]) for one document."""
    extension = row["extension"].lower()
    if extension not in READERS:
        return "unreadable_format", None, []
    if not fd.is_cached(row, cache):
        return "not_downloaded", None, []
    try:
        pages = READERS[extension](fd.cached_path(row, cache))
    except ImportError:
        raise  # pypdf missing: every PDF would "fail", so stop instead of writing that index
    except Exception as error:  # a broken file must not stop the build; it is recorded instead
        print(f"  FAILED {row['accession']} {row['file_name']}: {error}", flush=True)
        return "failed", None, []
    found = [(page, chunk) for page, text in pages for chunk in passages(text)]
    page_count = len(pages) if extension != ".docx" else None
    return ("indexed" if found else "no_text"), page_count, found


def build(rows: list[dict], cache: str = fd.CACHE, out: str = OUT) -> dict[str, int]:
    """Write the index to `out` (via a temporary name) and return the count per status."""
    temporary = out + ".part"
    if os.path.exists(temporary):
        os.remove(temporary)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    counts: dict[str, int] = {}
    db = sqlite3.connect(temporary)
    try:
        db.executescript(SCHEMA)
        for row in rows:
            status, pages, found = index_one(row, cache)
            counts[status] = counts.get(status, 0) + 1
            db.execute(
                "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (row["file_id"], row["accession"], row["file_name"], row["category"],
                 row["extension"], row["bytes"], status, pages, len(found)),
            )
            db.executemany(
                "INSERT INTO passages (text, file_id, page) VALUES (?, ?, ?)",
                [(chunk, row["file_id"], page) for page, chunk in found],
            )
        db.execute("INSERT INTO passages (passages) VALUES ('optimize')")
        db.executemany("INSERT INTO meta VALUES (?, ?)", [
            ("built", date.today().isoformat()),
            ("source", "NASA PSI documents, https://psi.nasa.gov"),
            ("passage_words", str(PASSAGE_WORDS)),
        ])
        db.commit()
        db.execute("VACUUM")
    finally:
        db.close()  # Windows cannot rename a file SQLite still holds open
    os.replace(temporary, out)
    return counts


def main() -> None:
    rows = fd.documents()
    counts = build(rows)
    db = sqlite3.connect(OUT)
    total = db.execute("SELECT count(*) FROM passages").fetchone()[0]
    db.close()
    print(f"{len(rows)} documents: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print(f"{total} passages, {os.path.getsize(OUT) / 1e6:.1f} MB at {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
