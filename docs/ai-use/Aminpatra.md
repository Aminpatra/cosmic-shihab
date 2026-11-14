# AI use: @Aminpatra

| Date | Tool and model | What the AI did | Where the output is | Human check |
|---|---|---|---|---|
| 2026-11-14 | Claude Code, Claude Opus 5.5 | Wrote the document downloader, the keyword search index builder and the `/api/search` endpoint, with tests on generated sample documents. The indexed text is NASA's, extracted unchanged. | `pipeline/fetch_documents.py`, `pipeline/build_search_index.py`, `backend/app/search.py`, `backend/app/routes/search.py`, issue #18 | @Aminpatra chose the scope (both the assistant and the search page use it); waiting for the team's review |
