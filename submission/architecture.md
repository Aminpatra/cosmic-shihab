# How FLARE is built

FLARE is a web application in three parts: an offline **pipeline** that reads NASA PSI once and
writes plain files, a read-only **API** that serves those files, and a **website** that lets people
explore, rank and compare. It is deployed on Vercel at https://cosmic-shihab.vercel.app.

```
NASA PSI web service
        │  (run offline, by hand)
        ▼
pipeline/            Python scripts: fetch records, file lists, tables and documents;
        │            clean the tables; build the search index; train the one model
        ▼
backend/data/        Read-only files: one JSON record per investigation, the file list (CSV),
        │            the processed tables (JSON), the search index (SQLite), the model's results
        ▼
backend/             FastAPI: 14 read-only endpoints under /api, plus the assistant
        │
        ▼
frontend/            React website: Home, Explorer (and a page per investigation), Scenario,
                     Comparison, Visualization, Assistant, Methodology, Sources
```

## Pipeline (offline, Python)

The pipeline runs on a team member's machine, never on the live site, and is the only code that
writes data.

- `harvest.py` fetches PSI's record, complete file list and experimental tables for each of the
  24 combustion investigations through PSI's web service (`psi_client.py`). `build_catalogue.py`
  arranges them into the catalogue and adds FLARE's tags (platform, fuel phase, fire-safety role,
  gravity level, data held).
- `process_tables.py` reads the 22 experimental tables into one shape. Every cell keeps its
  original text; missing and impossible values are marked; units are converted only where the
  conversion is exact, and converted values are marked as calculated.
- `fetch_documents.py` and `build_search_index.py` download PSI documents and index their text
  (SQLite full-text search, one passage of about 150 words per result).
- `train_flex_model.py` trains FLARE's one machine-learning model (scikit-learn, explained with
  SHAP) on the FLEX tests and stores its results; the live site only reads them.
- `write_summaries.py` asks the assistant for a cited summary of each investigation, and a plain
  reading of the ranking for the three scenarios the challenge page states, and stores each marked
  "not reviewed" until a team member has checked it against its sources. All 27 have been reviewed.

## API (backend, Python FastAPI)

The API only reads the files above, so there is no database server to run and nothing for a
visitor to change. Every route starts with `/api`.

| Area | Endpoints |
|---|---|
| Catalogue | `/api/health`, `/api/investigations`, `/api/investigations/{accession}`, `/api/files` |
| PSI downloads | `/api/files/{file_id}/download` redirects to a fresh, short-lived link from PSI; FLARE never stores or copies the file |
| Experimental runs | `/api/runs`, `/api/runs/rows` |
| Ranking | `/api/rank` ranks every investigation against a scenario and explains each score; `/api/rank/options` gives the real ranges and fuels in the data |
| Search | `/api/search` searches the indexed documents |
| Model | `/api/flex-model` serves the stored model results with their limitations |
| Assistant | `/api/assistant/status`, `/api/assistant/ask`, `/api/assistant/summaries/{accession}`, `/api/assistant/readings` |

**The assistant** gathers the investigation records and document passages that match a question
and sends them to Claude Opus 5.5 (Anthropic) with the instruction to answer only from those
sources and cite them. Every sentence that rests on a source cites the words it uses; the
assistant's own explanation is marked apart. The live site has a key set and answers with Claude
Opus 5.5. Without an API key it still works: it returns the matching NASA passages and facts with
their links, and no generated text.

## Website (frontend, React)

React 19 with React Router and Vite, plain CSS, Lucide icons, and the Fira Sans, Fira Code and
Overpass typefaces. Charts are drawn as SVG directly, with no chart library. The palette and
typefaces follow the NASA Space Apps brand guidelines, and pages are checked at phone width
(375px) as well as desktop. Data is shown with where it came from: the PSI accession, the table
and the DOI.

## Deployment

One Vercel project runs two services from the same repository: the frontend as a static Vite
site and the backend as a Python function. Requests to `/api/...` go to the backend; everything
else goes to the website.

## Languages and tools

- **Languages:** Python (pipeline and API, Python 3.12 to 3.14), JavaScript with JSX (website),
  CSS, SQL (SQLite full-text search).
- **Testing:** Python tests for the pipeline and API against the committed data, Node's
  built-in test runner for the website's logic, and Playwright in a real browser for QA at phone
  and desktop widths.
- **Teamwork:** six people working in parallel on GitHub, each task on its own branch and pull
  request, coordinated by a small task server the team wrote (`coordinator/`).

<!--
For the team (not for the form). Draft for the "how it works" and "tools and languages" parts of
the Detailed Project Description, issue #36. Sources:
- Live URL: docs/DEPLOY.md. Two services and the /api rewrite: vercel.json.
- Pipeline scripts: pipeline/*.py (git ls-files, 2026-11-14) and their docstrings; summaries
  are stored with `reviewed: false` (pipeline/write_summaries.py docstring).
- Not claimed on purpose: a measured contrast ratio (CLAUDE.md asks for >= 4.5:1, but no run in
  this session measured it).
- 14 endpoints: the endpoint table in backend/README.md.
- Read-only, no CORS, /api prefix, fresh PSI links: docs/DECISIONS.md (#8, #19).
- Assistant behaviour: backend/app/assistant.py, docs/DECISIONS.md (#10, #41). The live site's key:
  GET /api/assistant/status on https://cosmic-shihab.vercel.app gave {"mode": "generated", "model":
  "claude-opus-5-5"} on 15 Nov 2026 (#15). 27 reviewed: backend/data/summaries/ (#63).
- ~150-word passages: docs/DECISIONS.md (#18).
- Model: pipeline/train_flex_model.py, backend/data/flex_model/results.json, DECISIONS (#16).
  No metric is quoted here; the results are in submission/description.md and limitations.md (#15).
- Frontend stack: frontend/package.json (react 19.3.1, react-router 8.5.1, vite 8.3.8,
  lucide-react 1.73.0, @fontsource fira-sans, fira-code, overpass). SVG charts:
  frontend/src/pages/Visualization.jsx (no chart library in package.json; CLAUDE.md mentions
  Recharts and Motion but neither is installed).
- Pages: frontend/src/pages.js and frontend/src/pages/*.jsx.
- Python versions: docs/DECISIONS.md and backend/pyproject.toml (>=3.12,<3.15).
- Tests: backend/tests (unittest), pipeline/tests, frontend/src/pages/*.test.js (node:test);
  Playwright QA: submission/qa_results.md (#37).
-->
