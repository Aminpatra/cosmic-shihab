# AI use: @Rahaf-Abubaker

| Date | Tool and model | What the AI did | Where the output is | Human check |
|---|---|---|---|---|
| 2026-11-14 | Claude Code, Claude Opus 5.5 | Surveyed every column of PSI's 22 experimental tables, then wrote the script that reads them into one shape (each cell kept as written, missing and impossible values marked, units converted only where exact) and 17 checks on the real rows. The data is NASA's; nothing was generated. | `pipeline/process_tables.py`, `pipeline/tests/test_process_tables.py`, `backend/data/runs/`, issue #12 | @Rahaf-Abubaker had Python installed and was shown the row shape before it was written; waiting for the team's review |
| 2026-11-14 | Claude Code, Claude Opus 5.5 | Profiled the 22 processed PSI tables, found 117 suspect values (76 the pipeline does not flag), wrote the exploratory analysis script, three charts with a validated colour palette, a findings README and 5 checks; the key numbers were recounted from the raw PSI files. The data is NASA's; nothing was generated. | `research/analysis/`, issue #27 | Waiting for the team's review |
