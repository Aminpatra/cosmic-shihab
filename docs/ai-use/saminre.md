# AI use: @saminre

| Date | Tool and model | What the AI did | Where the output is | Human check |
|---|---|---|---|---|
| 2026-11-14 | Claude Code, Claude Opus 5.5 | Read the 24 PSI records and 22 experimental tables, drafted the research inventory and the per-investigation tags (hardware, platform, fuel phase, fire-safety role, gravity level, data held), each citing the record field or table it came from, and listed the data problems it counted in the files. Changed `build_catalogue.py` to copy the tags into each record, with checks. The data is NASA's; no values were generated. | `research/`, `pipeline/build_catalogue.py`, `pipeline/tests/test_tags.py`, `backend/data/investigations/` (`derived.tags`), issue #17 | @saminre directed the work and re-ran the PSI harvest; the tags still need a team member to check them against the cited fields |
