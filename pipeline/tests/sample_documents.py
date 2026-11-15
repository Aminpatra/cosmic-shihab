"""Small test documents for the search index: a Word file, a PowerPoint file and PDFs.

Their text is test text, labelled "Fixture", not NASA's. Each row borrows a real accession so
the backend can join it to the catalogue for title, acronym and DOI. Used by
test_build_search_index.py and by backend/tests/test_search_api.py.

SI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

from __future__ import annotations

import os
import zipfile

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def pdf_bytes(pages: list[str]) -> bytes:
    """A valid PDF with one line of Helvetica text per page ("" makes a page with no text)."""
    page_ids = [4 + 2 * i for i in range(len(pages))]
    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [" + b" ".join(b"%d 0 R" % p for p in page_ids)
           + b"] /Count %d >>" % len(pages),
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    for page_id, text in zip(page_ids, pages):
        stream = b"BT /F1 12 Tf 72 720 Td (" + text.encode("latin-1") + b") Tj ET" if text else b""
        objects[page_id] = (b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                            b"/Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>" % (page_id + 1))
        objects[page_id + 1] = b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
    out, offsets = bytearray(b"%PDF-1.4\n"), {}
    for number in sorted(objects):
        offsets[number] = len(out)
        out += b"%d 0 obj\n" % number + objects[number] + b"\nendobj\n"
    xref, size = len(out), max(objects) + 1
    out += b"xref\n0 %d\n0000000000 65535 f \n" % size
    out += b"".join(b"%010d 00000 n \n" % offsets[n] for n in range(1, size))
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (size, xref)
    return bytes(out)


def docx_bytes(paragraphs: list[str], path: str) -> None:
    body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml",
                         f'<w:document xmlns:w="{W_NS}"><w:body>{body}</w:body></w:document>')


def pptx_bytes(slides: list[str], path: str) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        # Stored last slide first, so the reader has to sort them by number.
        for number in reversed(range(1, len(slides) + 1)):
            archive.writestr(f"ppt/slides/slide{number}.xml",
                             f'<p:sld xmlns:a="{A_NS}" xmlns:p="p"><a:t>{slides[number - 1]}</a:t></p:sld>')


def write_samples(cache: str, with_pdfs: bool = True) -> list[dict]:
    """Write the sample files into a fetch_documents-style cache and return their rows."""
    rows = []

    def add(accession, file_id, file_name, category, extension, write=None):
        path = os.path.join(cache, accession, file_id + extension)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if write is not None:
            write(path)
        size = os.path.getsize(path) if write is not None else 1000
        rows.append({"accession": accession, "file_id": file_id, "file_name": file_name,
                     "category": category, "extension": extension, "bytes": size})

    def raw(data):
        def write(path):
            with open(path, "wb") as handle:
                handle.write(data)
        return write

    add("PSI-25", "fixture-docx", "PSI-25_Science Documents_Fixture ReadMe.docx", "Science Documents",
        ".docx", lambda p: docx_bytes(["Fixture readme.", "The PMMA film samples were 2 cm wide."], p))
    add("PSI-98", "fixture-pptx", "PSI-98_Presentations_Fixture: Overview.pptx", "Presentations",
        ".pptx", lambda p: pptx_bytes(["Fixture title slide",
                                       "Fixture slide two: flame spread over cotton fabric",
                                       "Fixture slide three: concluding remarks"], p))
    add("PSI-102", "fixture-ppt", "PSI-102_Presentations_Fixture old slides.ppt", "Presentations",
        ".ppt", raw(b"old binary format"))
    add("PSI-39", "fixture-missing", "PSI-39_Reports_Fixture never downloaded.pdf", "Reports", ".pdf")
    if with_pdfs:
        add("PSI-69", "fixture-pdf", "PSI-69_Reports_Fixture Report.pdf", "Reports", ".pdf",
            raw(pdf_bytes(["Fixture page one about droplet burning in air.",
                           "Fixture page two: methanol droplets reached radiative extinction."])))
        add("PSI-26", "fixture-scan", "PSI-26_Reports_Fixture scan.pdf", "Reports", ".pdf",
            raw(pdf_bytes(["", ""])))
    return rows
