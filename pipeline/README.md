# pipeline

Collects NASA PSI data and prepares the files the backend reads. It runs by hand on a laptop and
is never deployed. Standard library only, except `pypdf` for the search index
(`requirements.txt`); tested on Python 3.12 to 3.15.

```
python3 pipeline/harvest.py              # fetch records, file lists and experimental tables from PSI
python3 pipeline/build_catalogue.py      # write backend/data/ and datasets/SOURCES.csv
python3 pipeline/process_tables.py       # write backend/data/runs/ from the tables in datasets/

python3 -m pip install -r pipeline/requirements.txt   # once, for the search index
python3 pipeline/fetch_documents.py      # download PSI's reports and presentations into .cache/
python3 pipeline/build_search_index.py   # write backend/data/search.sqlite
python3 pipeline/train_flex_model.py     # write backend/data/flex_model/results.json (about 80 s)

python3 -m unittest discover -s pipeline/tests -v
```

| File | What it does |
|---|---|
| `psi_client.py` | The four PSI calls, each checking the response's shape and failing loudly |
| `harvest.py` | Saves raw responses to `.cache/psi/raw/` (ignored by git) and the experimental tables to `datasets/`. Skips what is already there; pauses a second between calls |
| `build_catalogue.py` | Normalizes the raw responses into `backend/data/` |
| `process_tables.py` | Reads the 22 experimental tables in `datasets/` into `backend/data/runs/`: every cell kept as written, with what it says read out beside it |
| `fetch_documents.py` | Downloads every non-"Raw Data" document in a readable format (PDF, Word, PowerPoint) to `.cache/psi/documents/`, named by PSI file id. Resumable; one request a second to PSI |
| `build_search_index.py` | Cuts the documents' text into passages of about 150 words and writes `backend/data/search.sqlite`, with every document's status (indexed, no text, unreadable format, not downloaded, failed) |
| `train_flex_model.py` | Trains FLARE's one model on the 274 FLEX tests: majority baseline, logistic regression and random forest, compared by macro-F1 with test days kept together; scores the chosen one on held-out days, checks it against shuffled labels and explains it with SHAP. Writes `backend/data/flex_model/results.json` |
| `tests/` | Client tests on small saved responses; checks on the committed catalogue |

A first harvest takes about twenty minutes, because PSI's larger records are slow. It downloads
about 50 MB of metadata and 210 KB of tables, none of PSI's 13.5 TB of zips and video.

How PSI behaves, which investigations are reliable, and what is still to build are in
`docs/DATA_PLAN.md`.

The fixtures in `tests/fixtures/` are real PSI responses from 14 November 2026. The search pages
are cut down to the two fields the client reads, and contact details are blanked in the record.

**SI use:** the code in this folder was written with Claude Code (Claude Fable 5.2) and reviewed
by the team. It fetches and rearranges NASA data; it does not generate any.
