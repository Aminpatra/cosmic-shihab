# AI use: @Rahaf-Abubaker

| Date | Tool and model | What the AI did | Where the output is | Human check |
|---|---|---|---|---|
| 2026-11-14 | Claude Code, Claude Opus 5.5 | Surveyed every column of PSI's 22 experimental tables, then wrote the script that reads them into one shape (each cell kept as written, missing and impossible values marked, units converted only where exact) and 17 checks on the real rows. The data is NASA's; nothing was generated. | `pipeline/process_tables.py`, `pipeline/tests/test_process_tables.py`, `backend/data/runs/`, issue #12 | @Rahaf-Abubaker had Python installed and was shown the row shape before it was written; waiting for the team's review |
