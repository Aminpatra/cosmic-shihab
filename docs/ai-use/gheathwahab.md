# AI use: @gheathwahab

| Date | Tool and model | What the AI did | Where the output is | Human check |
|---|---|---|---|---|
| 2026-11-14 | Claude Code, Claude Opus 5.5 | Read Vercel's FastAPI and Services docs, then wrote the FastAPI app shell that serves the PSI catalogue read-only (health, investigations, file list) with 12 automated checks against the committed data. The data is NASA's, served unchanged. | `backend/` (except `data/`), `docs/DECISIONS.md`, issue #8 | @gheathwahab chose how to split the work with #7; waiting for the team's review |
