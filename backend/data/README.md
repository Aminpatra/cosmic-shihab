# backend/data

Read-only files the FLARE API serves. The catalogue is written by `pipeline/build_catalogue.py`,
`runs/` by `pipeline/process_tables.py` and `search.sqlite` by `pipeline/build_search_index.py`;
do not edit by hand. Rebuild with the commands in `pipeline/README.md`.

**Source:** NASA Physical Sciences Informatics (PSI) repository, https://psi.nasa.gov, retrieved
14 November 2026. Cite each investigation by its DOI.

| File | Contents |
|---|---|
| `investigations/<ACCESSION>.json` | One PSI combustion investigation (24 in all): title, acronym, DOI, licence, objective, hypothesis, approach, hardware, people and publications |
| `runs/<ACCESSION>.json` | PSI's experimental tables for 20 investigations (22 tables, 2,009 rows): every cell as PSI wrote it, what FLARE read from it, and a few conditions in common units. Shape below |
| `files.csv` | One row for each of PSI's 60,866 files for those investigations: name, category, type, size, version, date. 13.5 TB is listed; none of it is stored here |
| `search.sqlite` | Keyword index (21.5 MB) of the text of 256 PSI documents: 18,036 passages of about 150 words. Its `documents` table lists all 352 documents in scope (every non-"Raw Data" document) with a status: 256 indexed, 72 with no text (mostly engineering drawings), 15 in old .ppt/.doc formats, 7 that PSI could not serve on 14 November 2026 (5 of them SAFFIRE), 2 broken PDFs |
| `flex_model/results.json` | Results of the FLEX test-outcome model (`pipeline/train_flex_model.py`): scores against a majority baseline, confusion matrices, a chance check, SHAP summaries and limitations. Computed by FLARE from NASA's FLEX table; a pattern in those tests, not a prediction of a real fire |

In the investigation files, every field except `derived` is copied from PSI under PSI's own name
and with its value unchanged. `derived` holds what FLARE computed: the links, file counts by kind,
and the row and column counts of each experimental table. Contact e-mail addresses and phone
numbers are left out.

`kind` in `files.csv` is FLARE's grouping by file extension: `archive_or_video`, `document`,
`table`, `text`, `numeric` or `other`.

To download a file, ask PSI for a link at the moment it is needed (`download_url` in
`pipeline/psi_client.py`). The link expires after about an hour, so it is never stored.

**Licence:** 23 investigations are CC0-1.0. PSI-10 states no licence (`derived.licence_stated` is
false).

## The runs files

One file per investigation with an experimental table. Read `row_is` before counting anything:
a row is one `test` in most tables, but one `test_day` in SLICE and the ACME BRE, CLD, E-FIELD and
s-Flame tables, one `session` in DAFT, one `fuel_summary` in FLEX-2 (ranges of conditions, not
tests) and one `published_figure` in PSI-142.

```
{"accession": "PSI-25", "tables": [{
  "file": "PSI-25_Experimental table_BASS-II.csv",          // in datasets/, unchanged
  "psi_file_name": "...", "doi_url": "https://doi.org/...", "encoding": "utf-8",
  "row_is": "test", "row_count": 129,
  "columns": [{"name": "Initial CO (ppm)", "unit": "ppm"}, ...],   // PSI's headers, exactly
  "standard_columns": {"oxygen": "Calibrated  initial O2 % by vol ", ...},
  "rows": [{
    "line": 3, "run_id": "B2",                              // line in the CSV; PSI's test ID
    "cells": {"Total Frames Shot": {"raw": "none", "kind": "missing", "missing": "text"}, ...},
    "standard": {"oxygen": {"column": "...", "role": "condition", "value": 0.222,
                 "unit": "mole fraction", "calculated": true,
                 "original": {"value": 22.2, "unit": "% by vol"}}, ...},
    "linked": [{"file": "BASS-II Test Matrix by PI Final.xlsx", "sheet": "Bhattacharjee",
                "row": 3, "date": "2014-02-19"}]          // BASS-II only; same test, not a second run
  }]}]}
```

**Cells.** `raw` is always PSI's text, unchanged. `kind` says what FLARE read from it:

| kind | Extra keys | Example |
|---|---|---|
| `number` | `value`, and `unit`, `approx` (`~`) or `bound` (`<`, `>`) when the cell says so | `"~ 21.5"`, `"30 cm/s"`, `">500"` |
| `list` | `values`, never averaged | `"0.9   1.3   2.75"`, `"21; 26.5; 40"` |
| `range` | `range: [low, high]` | `"21.5 - 21.7"`, `"0.1 - 5"` |
| `text` | none; read `raw` | `"1.4 incr to 10.0"`, `"RAMP"`, `"OR"` |
| `missing` | `missing`: `empty`, `text` (none, n/a), `dash` or `spreadsheet_error` (`#DIV/0!`) | never 0 |

**Flags** mark what looks wrong and is left as written: `negative_concentration` (BASS-II CO of
-1 ppm), `percent_over_100` (ACME BRE "3400%", probably 34 typed into a cell formatted as a percent), `impossible_formula`
("40% CH5": a spreadsheet counted CH4 upwards when filling the column) and `leading_zero`
(SAFFIRE-II "037 mm").

**Standard fields** copy a few conditions that mean the same thing in every investigation, in one
unit: `oxygen` (mole fraction), `pressure` (atm), `flow_velocity` (cm/s) and `fuel` are
`condition`s, known before the test; `burn_time` (s) and `test_end` are `outcome`s, measured during
or after it, so they are never inputs to a model. A converted value has `calculated: true` and
keeps the `original`. The conversions are exact ones only: volume percent to mole fraction (ideal
gas), mmHg and bar to atm. A cell that says something else ("RAMP", "Insignificant") keeps it in
`text` and has no value. `fuel` keeps the `text` and adds `material`, `shape` and `sizes` only as far
as the text states them; a size gets a `label` (`wide`, `thick`) only when the text gives one.

Where a header states no unit and FLARE assumed one, the column has `unit_inferred: true`: XO2 in
ACME Flame Design and CFI-G (the usual symbol for mole fraction), and CFI's Oxygen, Nitrogen and
Helium (they add up to 1).

**SI use:** the scripts that wrote these files were written with Claude Code. The contents are
NASA's data, rearranged, not SI-generated.
