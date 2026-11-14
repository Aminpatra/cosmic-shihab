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
| `GET /api/rank?` | `{scenario, method, notice, message, gravity_note, items, not_ranked}`. Scenario as query parameters, all optional: `environment` (`spacecraft`, `lunar`, `mars`, `custom`; sets gravity only), `gravity_g` (0 to 1, only with `custom`), `oxygen` (mole fraction), `pressure` (atm), `flow_velocity` (cm/s), `fuel` (text), `fuel_phase` (`gas`, `liquid`, `solid`), `concern` (`prevention`, `detection`, `suppression`), and `weight_<variable>` (0 to 10, default 1). Each item: `accession`, `title`, `investigationAcronym`, `doi`, `score` (0 to 100, the best test's), `close_tests`, `rows_scored`, `row_unit`, `used_variables`, `matches` and `differences` (`variable`, `scenario`, and for numbers `tested_min`, `tested_max`, `closest`, `unit`; else `tested`), `unavailable`, `best_tests` (up to 3: `file`, `line`, `run_id`, `score`, `values`), `measured_outcomes`, `gravity_note`. `not_ranked` items carry a `reason`. No condition set: 200 with `items: []` and `message`. 422 for values out of range |
| `GET /api/rank/options` | `{variables: {oxygen, pressure, flow_velocity: {unit, min, max, rows}}, fuels: [{name, rows}], fuel_phases, concerns, environments: {name: gravity in g}}`, all from the data |
| `GET /api/runs` | The 22 experimental tables, without rows: `accession`, `file`, `psi_file_name`, `doi_url`, `encoding`, `row_is`, `row_count`, `columns` (`[{name, unit, unit_inferred}]`, PSI's headers exactly), `standard_columns`. Filter: `accession` (404 if unknown; `[]` for an investigation with no table) |
| `GET /api/runs/rows` | `{total, limit, offset, items}`, rows in accession, table and line order, each as stored in `data/runs/` plus its `accession` and `table`. Filters: `accession` (404 if unknown), `table` (a `file` from `/api/runs`; 404 if unknown). `cells=false` leaves out the per-column cells and keeps `standard`, enough for charts (500 rows: 174 KB instead of 580 KB). `limit` 1 to 500, default 100; `offset` from 0 |

Field names are PSI's own; what FLARE computed is under `derived` (see `data/README.md`). In file
items, a blank `subcategory` or `updated` comes back as `null`.

Run rows keep each cell's original text in `raw`; the cell kinds, flags and `standard` fields are
described in `data/README.md`. Check `row_is` before counting tests: some tables have one row per
test day, session, fuel or published figure.

The API sends no CORS headers. The frontend calls relative `/api/...` paths: on Vercel both
services share one domain, and in development the Vite dev server proxies `/api` to
`http://127.0.0.1:8000`.

## Layout

| Path | What it is |
|---|---|
| `main.py` | Defines `app`, Vercel's entrypoint, and includes each router |
| `app/catalogue.py` | Loads `data/` once per process |
| `app/runs.py` | Loads `data/runs/` once per process (written by `pipeline/process_tables.py`); ranking can read rows from here too |
| `app/search.py` | Queries `data/search.sqlite` read-only (written by `pipeline/build_search_index.py`) |
| `app/runs.py` | Loads `data/runs/` once per process |
| `app/ranking.py` | Scores each PSI test against a scenario and rolls up to investigations (design: `docs/superpowers/specs/2026-11-14-ranking-engine-design.md`) |
| `app/routes/` | One module per group of endpoints, each defining `router` |
| `app/services/` | Calls made while answering a request: `psi_links.py` asks PSI for download links |
| `tests/` | Endpoint tests against the committed `data/` |
| `pyproject.toml` | Runtime dependencies only; this is what Vercel installs |
| `requirements-dev.txt` | Local server and test client |

**AI use:** the code in this folder was written with Claude Code (Claude Opus 5.5) and reviewed by
the team. It serves NASA's data unchanged; it does not generate any.
