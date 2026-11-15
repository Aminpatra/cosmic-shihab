# FLARE: Fire Learning, Analysis & Research Explorer

A research tool for NASA's microgravity combustion data, built by team **Cosmic Shihab** for the
NASA Space Apps Challenge 2026, challenge **Flame in Freefall**.

**Live:** https://cosmic-shihab.vercel.app

Describe a fire scenario (a spacecraft, a Moon base, a spacesuit, or your own conditions) and FLARE
ranks NASA's 24 combustion investigations in the Physical Sciences Informatics (PSI) repository by
how closely their actual tests match it, explains every score, lays investigations side by side,
and answers questions from NASA's own records and documents with citations. A relevance score is
not a safety assessment, and FLARE says so.

## What is where

| Folder | What it holds |
|---|---|
| `pipeline/` | Python scripts that read PSI once and write the data files, the search index and the one model |
| `backend/` | The read-only FastAPI service: catalogue, ranking, search, runs, model results, assistant |
| `frontend/` | The React website |
| `research/analysis/` | The offline profiling of the experimental tables |
| `submission/` | The Space Apps submission: description, ranking method, limitations, test report and more |
| `docs/` | Team decisions, the deploy guide and each member's SI-use log |

## Run it locally

```
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt     # macOS/Linux: .venv/bin/python
.venv/Scripts/python -m uvicorn main:app --reload               # API on http://127.0.0.1:8000

cd ../frontend
npm ci
npm run dev                                                     # site on http://localhost:5173
```

The assistant answers with Claude Opus 5.5 when `ANTHROPIC_API_KEY` is set in `.env`; without it,
it returns the matching NASA sources and no generated text. Tests and data steps are in
`backend/README.md`, `pipeline/` and `submission/test_report.md`.

## Data

All data is NASA's, from PSI (https://psi.nasa.gov), research area Combustion Science, retrieved
14 November 2026, and kept as NASA published it. See `submission/datasets.md`.

## How it was built

FLARE was built by the team with **Claude Code** (Anthropic), running Claude Opus 5.5 and Claude
Fable 5.2, under our direction; the idea and the design choices are the team's. Commits an agent
helped write name the model in a `Co-Authored-By` line, and each member's log is in
`docs/ai-use/`. How SI was used is in `submission/ai_use.md`; every external resource is in
`submission/references.md`.

## Team

Amin Mohamed Amin, Gheath Wahab, Mohammed Al-julandani, Samin Rezaei, Rahaf Abubaker Mustafa
Mubarak and Ruayma Khair Mohammed Albalushi.
