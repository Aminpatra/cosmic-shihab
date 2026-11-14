# backend/data

Read-only files the FLARE API serves. The catalogue is written by `pipeline/build_catalogue.py`
and the search index by `pipeline/build_search_index.py`; do not edit by hand. Rebuild with the
commands in `pipeline/README.md`.

**Source:** NASA Physical Sciences Informatics (PSI) repository, https://psi.nasa.gov, retrieved
14 November 2026. Cite each investigation by its DOI.

| File | Contents |
|---|---|
| `investigations/<ACCESSION>.json` | One PSI combustion investigation (24 in all): title, acronym, DOI, licence, objective, hypothesis, approach, hardware, people and publications |
| `files.csv` | One row for each of PSI's 60,866 files for those investigations: name, category, type, size, version, date. 13.5 TB is listed; none of it is stored here |
| `search.sqlite` | Keyword index (21.5 MB) of the text of 256 PSI documents: 18,036 passages of about 150 words. Its `documents` table lists all 352 documents in scope (every non-"Raw Data" document) with a status: 256 indexed, 72 with no text (mostly engineering drawings), 15 in old .ppt/.doc formats, 7 that PSI could not serve on 14 November 2026 (5 of them SAFFIRE), 2 broken PDFs |

In the investigation files, every field except `derived` is copied from PSI under PSI's own name
and with its value unchanged. `derived` holds what FLARE computed: the links, file counts by kind,
and the row and column counts of each experimental table. Contact e-mail addresses and phone
numbers are left out.

`kind` in `files.csv` is FLARE's grouping by file extension: `archive_or_video`, `document`,
`table`, `text`, `numeric` or `other`.

To download a file, ask PSI for a link at the moment it is needed (`download_url` in
`pipeline/psi_client.py`). The link expires after about an hour, so it is never stored.

**Licence:** 23 investigations are CC0-1.0. PSI-10 states no licence (`derived.licence_stated` is
false).

**AI use:** the script that wrote these files was written with Claude Code. The contents are
NASA's data, rearranged, not AI-generated.
