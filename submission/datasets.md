# NASA data

Everything FLARE shows comes from NASA's **Physical Sciences Informatics (PSI)** repository
(https://psi.nasa.gov), research area Combustion Science, retrieved on 14 November 2026 through
PSI's public web service. NASA's data is never altered: FLARE keeps every value as PSI published
it, marks anything it converts, and links each investigation back to PSI and its DOI.

## What FLARE took from PSI

| What | How much | What FLARE does with it |
|---|---|---|
| Investigation records (title, objective, hardware, DOI, licence, publications) | All 24 combustion investigations | The Explorer, one page per investigation, and the facts the assistant cites |
| The file list (name, category, size, date, no content) | 60,866 files, 13.5 TB | Lists and links every file; a download link is fetched fresh from PSI each time and never stored |
| Experimental tables (one row per test or test day, with its conditions) | 22 tables from 20 investigations, 2,009 rows, copied unchanged | Ranking, comparison, charts and the one model |
| Documents (reports, papers, presentations) | 256 documents from 19 investigations indexed, 8,754 pages | Full-text search, and the passages the assistant quotes |

Of the 352 documents FLARE tried to index, 72 had no text layer (scanned pages), 15 were in
formats it cannot read, 7 were not downloaded and 2 failed. The rest of PSI's 1,926 documents are
listed and linked, not indexed.

**How the tables are read.** Each cell keeps its original text. Where tables mean the same thing,
FLARE also gives a comparable value: oxygen as a mole fraction, pressure in atmospheres, flow
velocity in cm/s, the fuel, and outcomes such as burn time and how a test ended. A converted value
is marked as calculated and keeps PSI's original beside it (FLEX's ambient pressure of 757.7 mmHg
stays 757.7 mmHg). Nothing is merged across investigations unless the columns mean the same thing.

**Licence.** 23 investigations are published under CC0-1.0. PSI-10 (ACME Flame Design) states no
licence, and FLARE shows its licence as "Not stated".

## The 24 investigations

| Accession | Investigation | Where it ran | Experimental table in FLARE | DOI |
|---|---|---|---|---|
| PSI-10 | ACME Flame Design | ISS | 327 runs (2 tables) | [10.60555/w4zy-bt45](https://doi.org/10.60555/w4zy-bt45) |
| PSI-20 | ACME Burning Rate Emulator (BRE) | ISS | 18 test days | [10.60555/vb93-3y72](https://doi.org/10.60555/vb93-3y72) |
| PSI-21 | ACME Coflow Laminar Diffusion Flame (CLD Flame) | ISS | 32 test days | [10.60555/23e1-9950](https://doi.org/10.60555/23e1-9950) |
| PSI-22 | ACME Electric-Field Effects on Laminar Diffusion Flames (E-FIELD Flames) | ISS | 32 test days | [10.60555/se5a-8c73](https://doi.org/10.60555/se5a-8c73) |
| PSI-23 | ACME Structure and Response of Spherical Diffusion Flames (s-Flame) | ISS | 18 test days | [10.60555/k57n-p030](https://doi.org/10.60555/k57n-p030) |
| PSI-25 | Burning and Suppression of Solids II (BASS-II) | ISS | 129 runs | [10.60555/4qc4-de67](https://doi.org/10.60555/4qc4-de67) |
| PSI-26 | Burning and Suppression of Solids (BASS) | ISS | 122 runs | [10.60555/58h4-dy80](https://doi.org/10.60555/58h4-dy80) |
| PSI-39 | Cool Flames Investigation (CFI) | ISS | 87 runs | [10.60555/m6pj-a914](https://doi.org/10.60555/m6pj-a914) |
| PSI-47 | Dust and Aerosol Measurement Feasibility Test (DAFT / DAFT-2) | ISS | 2 test days | [10.60555/ztgj-d202](https://doi.org/10.60555/ztgj-d202) |
| PSI-60 | Computational and Experimental Analysis of SPICE Data Sets | Computation | None | [10.60555/mzjm-yv57](https://doi.org/10.60555/mzjm-yv57) |
| PSI-62 | Concurrent Flame Spread Modeling using Flamelet Generated Manifolds, compared with BASS | Computation | None | [10.60555/e9xp-ex83](https://doi.org/10.60555/e9xp-ex83) |
| PSI-68 | Flame Extinguishment Experiment 2 (FLEX-2) | ISS | 8-row test matrix | [10.60555/byp8-h018](https://doi.org/10.60555/byp8-h018) |
| PSI-69 | Flame Extinguishment Experiment (FLEX) | ISS | 274 runs | [10.60555/mbq8-0451](https://doi.org/10.60555/mbq8-0451) |
| PSI-98 | Spacecraft Fire Safety Experiment I (Saffire-I) | Cygnus, after leaving the ISS | 4 runs | [10.60555/0t15-1z43](https://doi.org/10.60555/0t15-1z43) |
| PSI-99 | Spacecraft Fire Experiment II (Saffire-II) | Cygnus, after leaving the ISS | 15 runs | [10.60555/2chp-m469](https://doi.org/10.60555/2chp-m469) |
| PSI-100 | Spacecraft Fire Experiment III (Saffire-III) | Cygnus, after leaving the ISS | 2 runs | [10.60555/040q-4h36](https://doi.org/10.60555/040q-4h36) |
| PSI-101 | Smoke Aerosol Measurement Experiment Reflight (SAME-R) | ISS | 109 runs | [10.60555/2np7-jv14](https://doi.org/10.60555/2np7-jv14) |
| PSI-102 | Smoke and Aerosol Measurement Experiment (SAME) | ISS | 8 runs | [10.60555/gd4k-8h62](https://doi.org/10.60555/gd4k-8h62) |
| PSI-106 | Structure and Liftoff In Combustion Experiment (SLICE) | ISS | 12 test days | [10.60555/pm12-rg61](https://doi.org/10.60555/pm12-rg61) |
| PSI-107 | Smoke Point In Co-flow Experiment (SPICE) | ISS | 469 runs | [10.60555/9kbh-e962](https://doi.org/10.60555/9kbh-e962) |
| PSI-115 | Utilization of the SAME Data for Modeling and Simulation of Smoke Generation | Computation | None | [10.60555/q0v5-1v28](https://doi.org/10.60555/q0v5-1v28) |
| PSI-117 | Effect of External Thermo-Convective Perturbation on Cool Flame Dynamics | Computation | None | [10.60555/gz0q-b577](https://doi.org/10.60555/gz0q-b577) |
| PSI-142 | Quantitative Studies of Cool Flame Transitions at Radiation / Stretch Extinction | Ground laboratory and computation | 8-row index of published figures | [10.60555/80qf-vj95](https://doi.org/10.60555/80qf-vj95) |
| PSI-159 | ACME Cool Flames Investigation with Gases (CFI-G) | ISS | 333 runs (2 tables) | [10.60555/cyt1-kh64](https://doi.org/10.60555/cyt1-kh64) |

## What the data cannot support

- **Few rows where it matters most.** The three Saffire experiments, which burned samples inside
  an uncrewed Cygnus spacecraft, have 21 rows between them. FLARE shows them in full and says
  plainly how few there are.
- **Four investigations are catalogue only.** PSI-60, PSI-62, PSI-115 and PSI-117 analyse other
  investigations' data and publish no test table. FLARE lists them with their summary and links.
- **Conditions are often missing.** Of the 2,009 rows, 1,147 record oxygen, 1,001 pressure and 570
  airflow. A missing condition is shown as "not recorded", never filled in.
- **Some values look wrong.** FLARE's profiling found 117 suspect values in the tables, listed
  with file, line and rule so a researcher can check each against PSI.
- **One model, on one investigation.** FLARE trains a single model, on FLEX's 274 droplet tests.
  It describes a pattern in those tests, not real fires.

<!--
For the team (not for the form). Draft for the "NASA Data" field, issue #36. Sources:
- Retrieval date 2026-11-14 and the PSI calls: backend/data/investigations/*.json `derived.retrieved`,
  docs/DATA_PLAN.md "How PSI must be read".
- 24 investigations, titles, acronyms, DOIs, licences, platforms, table kinds ("run table",
  "test-day log", "test matrix", "figure index", "catalogue metadata only"):
  backend/data/investigations/*.json and their `derived.tags` (research/investigation_tags.csv).
  Titles are PSI's, with "Advanced Combustion via Microgravity Experiments" written as ACME and
  subtitles dropped for PSI-62, PSI-115 and PSI-117 (checked against the records 2026-11-14).
- "Burned samples inside an uncrewed Cygnus": platform tag "Cygnus (after leaving the ISS)".
- 60,866 files, 13.5 TB, 1,926 documents: backend/data/files.csv.
- 22 tables, 20 investigations, 2,009 rows, rows per investigation: backend/data/runs/*.json.
- 757.7 mmHg: backend/tests/test_runs.py (the master prompt's concrete check).
- Search index: backend/data/search.sqlite `documents` (256 indexed, 72 no_text, 15
  unreadable_format, 7 not_downloaded, 2 failed; 19 accessions; 8,754 pages), written by
  pipeline/build_search_index.py.
- 1,147 / 1,001 / 570: GET /api/rank/options on the committed data.
- 117 suspect values: research/analysis/suspect_values.csv.
- FLEX 274 tests, the model's scope: backend/data/flex_model/results.json `question`, `notice`.
  No model result is quoted here; they are in submission/description.md and limitations.md (#15).
-->
