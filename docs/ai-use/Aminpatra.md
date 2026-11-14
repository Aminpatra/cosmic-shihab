# AI use: @Aminpatra

| Date | Tool and model | What the AI did | Where the output is | Human check |
|---|---|---|---|---|
| 2026-11-14 | Claude Code, Claude Opus 5.5 | Wrote the document downloader, the keyword search index builder and the `/api/search` endpoint, with tests on generated sample documents. The indexed text is NASA's, extracted unchanged. | `pipeline/fetch_documents.py`, `pipeline/build_search_index.py`, `backend/app/search.py`, `backend/app/routes/search.py`, issue #18 | @Aminpatra chose the scope (both the assistant and the search page use it); waiting for the team's review |
| 2026-11-14 | Claude Code, Claude Opus 5.5 | Drafted the ranking design and plan, then wrote the runs loader, the row-by-row scoring and explanations, and `/api/rank` with `/api/rank/options`, with 27 tests on the real PSI rows. The scores rank NASA's tests by closeness to a scenario; they are not safety assessments. | `docs/superpowers/specs/2026-11-14-ranking-engine-design.md`, `backend/app/ranking.py`, `backend/app/routes/ranking.py`, issue #7 | @Aminpatra chose the approach (score each test, then roll up) and approved the design; waiting for the team's review |
