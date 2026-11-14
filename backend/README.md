# backend

The FLARE API: a FastAPI app that serves the read-only PSI catalogue in `data/`. On Vercel it is
the backend service, and every request under `/api/` reaches it with the path unchanged, so all
routes start with `/api`. Python 3.12 to 3.14.

```
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt     # macOS/Linux: .venv/bin/python
.venv/Scripts/python -m uvicorn main:app --reload               # http://127.0.0.1:8000/api/docs
.venv/Scripts/python -m unittest discover -s tests -v
```

## Endpoints

Interactive docs: `/api/docs`. Schema: `/api/openapi.json`.

| Endpoint | Returns |
|---|---|
| `GET /api/health` | `{status, investigations, files, retrieved}` |
| `GET /api/investigations` | All 24 investigations, summary fields only: `accession`, `title`, `investigationAcronym`, `doi`, `licenseIdentifier`, `researchArea`, `subResearchArea`, `projectType`, `flightProgram`, `experimentHardware`, `investigationStartDate`, `investigationEndDate`, `derived` |
| `GET /api/investigations/{accession}` | The whole stored record (objective, hypothesis, approach, contacts, publications, ...). 404 if unknown |
| `GET /api/files` | `{total, limit, offset, items}`, one item per `files.csv` row. Filters: `accession` (404 if unknown), `kind`, `category`. `limit` 1 to 500, default 100; `offset` from 0 |
| `GET /api/files/{file_id}/download` | A `307` redirect to a fresh PSI download link, with `Cache-Control: no-store`. Asks PSI each time (about 2 s); the link expires after about an hour and is never stored. 404 if the id is not in the catalogue, 502 if PSI fails or answers with anything but a `psi-repo-prod.s3.amazonaws.com` link. Use it as a plain link: `<a href="/api/files/{file_id}/download">` |
| `GET /api/search?q=` | `{query, total, limit, offset, items}`: passages of about 150 words from PSI documents matching any word of `q`, best first. Each item: `accession`, `title`, `investigationAcronym`, `doi`, `file_id`, `file_name`, `category`, `page` (PDF page or slide from 1; `null` for Word), `snippet` (matched words between `[[` and `]]`), `text` (the whole passage). Filter: `accession` (404 if unknown). `limit` 1 to 50, default 10. 422 if `q` has no words; 503 if `data/search.sqlite` is not built |

Field names are PSI's own; what FLARE computed is under `derived` (see `data/README.md`). In file
items, a blank `subcategory` or `updated` comes back as `null`.

The API sends no CORS headers. The frontend calls relative `/api/...` paths: on Vercel both
services share one domain, and in development the Vite dev server proxies `/api` to
`http://127.0.0.1:8000`.

## Layout

| Path | What it is |
|---|---|
| `main.py` | Defines `app`, Vercel's entrypoint, and includes each router |
| `app/catalogue.py` | Loads `data/` once per process |
| `app/search.py` | Queries `data/search.sqlite` read-only (written by `pipeline/build_search_index.py`) |
| `app/routes/` | One module per group of endpoints, each defining `router` |
| `app/services/` | Calls made while answering a request: `psi_links.py` asks PSI for download links |
| `tests/` | Endpoint tests against the committed `data/` |
| `pyproject.toml` | Runtime dependencies only; this is what Vercel installs |
| `requirements-dev.txt` | Local server and test client |

**AI use:** the code in this folder was written with Claude Code (Claude Opus 5.5) and reviewed by
the team. It serves NASA's data unchanged; it does not generate any.
