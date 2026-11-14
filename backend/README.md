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

| `GET /api/assistant/status` | `{mode, model}`: `generated` with the model id when `ANTHROPIC_API_KEY` is set, else `retrieval_only` and `null` |
| `POST /api/assistant/ask` | Body `{question, accessions}` (question 3 to 1000 characters; up to 4 accessions, empty means those the question names, else all). Returns `{question, mode, reason, model, blocks, sources}`. `blocks`: `{text, kind, citations}`, where `kind` is `source` (rests on the cited `{source_id, cited_text}`) or `explanation`. `sources`: `{id, kind, accession, title, label, url, doi, text}` plus `file_id`, `file_name`, `page`, `snippet` for document passages. `mode` is `retrieval_only`, with `blocks` empty and `reason` saying why, when there is no key, the model declines, the call fails, or nothing matches. 404 for an unknown accession, 422 for a bad body |
| `GET /api/assistant/summaries/{accession}` | A stored, AI-generated summary (`pipeline/write_summaries.py`): `{accession, note, model, generated, reviewed, reviewed_by, blocks, sources}`. Show it as reviewed only when `reviewed` is true. 404 if none has been written |

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
| `app/assistant.py` | The research assistant: gathers records and passages for a question, asks Claude Opus 5.5 with citations, or returns the sources alone |
| `app/search.py` | Queries `data/search.sqlite` read-only (written by `pipeline/build_search_index.py`) |
| `app/routes/` | One module per group of endpoints, each defining `router` |
| `app/services/` | Calls made while answering a request: `psi_links.py` asks PSI for download links |
| `tests/` | Endpoint tests against the committed `data/` |
| `pyproject.toml` | Runtime dependencies only; this is what Vercel installs |
| `requirements-dev.txt` | Local server and test client |

**AI use:** the code in this folder was written with Claude Code (Claude Opus 5.5) and reviewed by
the team. It serves NASA's data unchanged; it does not generate any.

## The assistant's key

The assistant reads `ANTHROPIC_API_KEY` from the environment and works without it, returning
sources only. Locally, keep the key in the repo's `.env` (ignored by git) and load it into the
shell before starting the server:

```
set -a; source ../.env; set +a
.venv/bin/python -m uvicorn main:app --reload
```

On Vercel, set `ANTHROPIC_API_KEY` in the project's environment variables. An answer takes the
model several seconds to tens of seconds, so the function's timeout must allow for it.
