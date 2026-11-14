# pipeline

Collects NASA PSI data and prepares the files the backend reads. It runs by hand on a laptop and
is never deployed. Standard library only; tested on Python 3.12 to 3.15.

```
python3 pipeline/harvest.py            # fetch records, file lists and experimental tables from PSI
python3 pipeline/build_catalogue.py    # write backend/data/ and datasets/SOURCES.csv
python3 pipeline/process_tables.py     # write backend/data/runs/ from the tables in datasets/
python3 -m unittest discover -s pipeline/tests -v
```

| File | What it does |
|---|---|
| `psi_client.py` | The four PSI calls, each checking the response's shape and failing loudly |
| `harvest.py` | Saves raw responses to `.cache/psi/raw/` (ignored by git) and the experimental tables to `datasets/`. Skips what is already there; pauses a second between calls |
| `build_catalogue.py` | Normalizes the raw responses into `backend/data/` |
| `process_tables.py` | Reads the 22 experimental tables in `datasets/` into `backend/data/runs/`: every cell kept as written, with what it says read out beside it |
| `tests/` | Client tests on small saved responses; checks on the committed catalogue |

A first harvest takes about twenty minutes, because PSI's larger records are slow. It downloads
about 50 MB of metadata and 210 KB of tables, none of PSI's 13.5 TB of zips and video.

How PSI behaves, which investigations are reliable, and what is still to build are in
`docs/DATA_PLAN.md`.

The fixtures in `tests/fixtures/` are real PSI responses from 14 November 2026. The search pages
are cut down to the two fields the client reads, and contact details are blanked in the record.

**AI use:** the code in this folder was written with Claude Code (Claude Fable 5.2) and reviewed
by the team. It fetches and rearranges NASA data; it does not generate any.
