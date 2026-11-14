# Data dictionary

What every file in `research/` holds, what each tag means, and how to read the PSI experimental
tables in `datasets/`. Retrieved from NASA PSI on 14 November 2026.

## Files

| File | Written by | One row per |
|---|---|---|
| `investigation_tags.csv` | hand, from the PSI records and tables | investigation (24) |
| `investigation_inventory.csv` | `pipeline/build_catalogue.py` (do not edit) | investigation (24) |
| `dataset_inventory.csv` | hand (counts computed from the files, units and limitations written by hand) | file in `datasets/` (24) |
| `source_references.csv` | hand (investigation rows taken from the catalogue) | external source (34) |
| `data_limitations.md` | hand | |

`build_catalogue.py` copies the tags into each record, under `derived.tags` in
`backend/data/investigations/<ACCESSION>.json` (`values`, `sources`, `notes`), and the API serves
them from there. Edit the tags only in `investigation_tags.csv`, then rebuild (`pipeline/README.md`).

## How a source is cited

- `record.<field>`: that field of the investigation's own PSI record, as copied into
  `backend/data/investigations/<ACCESSION>.json`. A quoted phrase is copied word for word.
- `table ...` or `datasets: ...`: the investigation's experimental table in `datasets/`.
- `challenge page`: the Space Apps "Flame in Freefall" page (`space-apps-challenge` in
  `source_references.csv`).
- A role, phase or level not found in these sources is written `not stated`, never guessed.

## Tags (`investigation_tags.csv`)

Each tag has a `<tag>_source` column. Several values are joined by `; `.

| Tag | Allowed values | Rule |
|---|---|---|
| `hardware_facility` | free text | The rack, glovebox or module the test ran in, with its apparatus. `not applicable (...)` for computational studies |
| `platform` | `ISS`, `Cygnus (after leaving the ISS)`, `computation`, `ground laboratory and computation` | Where the data was made |
| `fuel_phase` | `solid`, `liquid`, `gas`, `none (no fuel burned)`, `not stated` | Phase of the fuel as supplied: a gaseous fuel through a burner is `gas`, a droplet is `liquid`, a fabric or PMMA sample is `solid`. For studies of other investigations' data, the phase of the fuel studied |
| `fire_safety_role` | `prevention`, `detection`, `suppression`, `not stated` | Tagged only when the record's `objective`, `hypothesis` or `approach` names the role as the investigation's aim. Comparing flammability with NASA's material screening test (NASA-STD-6001) is tagged `prevention`, because that test decides which materials fly. A role named only in `researchImpacts`, as an expected benefit, is left `not stated` and quoted in `notes` |
| `gravity_level` | `microgravity`, `normal gravity`, `not stated` | Gravity under which the data was recorded, or which a simulation represents. Drop towers and orbit both count as microgravity |
| `flare_data` | see below | What FLARE holds for the investigation |

`flare_data` values:

| Value | Meaning | Investigations |
|---|---|---|
| `run table` | One row per test, run, flame or sample, with its conditions | 12 |
| `test-day log` | One row per test day or session: date, fuel, number of flames ignited | 6 |
| `test matrix` | One row per fuel, with ranges of conditions rather than individual tests | 1 (FLEX-2) |
| `figure index` | Points to figures in publications; no test data | 1 (PSI-142) |
| `catalogue metadata only` | No experimental table at PSI. FLARE shows the record, DOI and links, labelled "catalogued, no run data in FLARE" | 4 |

## `investigation_inventory.csv`

| Column | Meaning |
|---|---|
| `accession`, `acronym`, `title` | PSI's `accession`, `investigationAcronym`, `title` (acronym is blank for the five ground studies) |
| `project_type`, `flight_program` | PSI's `projectType`, `flightProgram` |
| `start_date`, `end_date` | PSI's `investigationStartDate`, `investigationEndDate`, as given (MM-DD-YYYY; blank where PSI gives none) |
| `doi_url`, `page_url` | Links to cite and to open the PSI page |
| `licence` | PSI's `licenseIdentifier`, or `not stated` |
| `file_count`, `bytes_listed` | Files PSI lists for the investigation and their total size |
| `experimental_tables`, `table_rows` | Number of experimental tables in `datasets/` and their data rows |
| tag columns | As in `investigation_tags.csv` (sources are there, not here) |
| `retrieved` | Date the PSI record was fetched |

## `dataset_inventory.csv`

| Column | Meaning |
|---|---|
| `file` | Name in `datasets/` (unchanged from PSI except the two `.xlsx` workbooks, renamed earlier) |
| `psi_file_name`, `psi_category` | The file's name and category at PSI |
| `source_link` | DOI of the investigation; open the PSI page from `investigation_inventory.csv` to download |
| `download_date` | When the copy in `datasets/` was fetched. `unknown` where someone added it by hand; the size check still ties it to PSI's file |
| `bytes`, `same_size_as_psi` | Size here, and whether it equals PSI's listed size |
| `rows`, `columns` | Data rows (blank rows not counted) and columns. Blank for the workbooks |
| `encoding` | Text encoding of the CSV |
| `variables` | Column headers exactly as written (spaces collapsed), separated by ` \| ` |
| `units` | Units as the headers or cells give them. Nothing is converted |
| `limitations` | Problems found in that file; summarised in `data_limitations.md` |

## Reading the experimental tables

Column names, spelling and units are PSI's. Columns differ between investigations, so nothing is
merged across tables unless the columns mean the same thing. Columns whose meaning is not obvious:

| Table | Column | Meaning |
|---|---|---|
| ACME (PSI-10, PSI-159) | `X...` | Mole fraction (no unit) |
| ACME (PSI-10, PSI-159) | `Zst` | Stoichiometric mixture fraction (standard combustion notation; the records use it without defining it) |
| ACME (PSI-10, PSI-159) | `Tad (K)` | Adiabatic flame temperature (standard notation, as above) |
| ACME (PSI-10, PSI-159) | Normal and inverse flames | Normal: fuel flows into oxidizer. Inverse: oxidizer flows into fuel |
| PSI-159 | `Self-ext or flow term` | `SE` self-extinguished, `FT` flow terminated, `-` neither |
| PSI-159 | `TFP` | Not defined in the table or the record; left as is |
| PSI-20, 22, 23 | `Flames Ignited` | Flames ignited that day (each table's own note) |
| PSI-21, 22, 23 | `Test Day` | YYDDD: two-digit year, then day of the year (table notes) |
| PSI-69 FLEX | `O`, `N`, `CO`, `He` initial ambient composition | O2, N2, CO2, He mole fractions; the subscripts were lost. FLEX names CO2 and He as suppressants (`record.objective`) |
| PSI-69 FLEX | `Test end` | `Extinction`, `Disruption` or `Completion`; the table and record do not define them |
| PSI-107 SPICE | `GMT date` | Day of the year; the year is not given |
| PSI-101 SAME-R | `Rt/R0` | Not defined in the table or the record; left as is |
| PSI-99 SAFFIRE-II | `?-g` | µ-g (microgravity); the µ was lost and stored as `?` |

Where the record and table do not define a column, it is described here only by its header.

**AI use:** the files in `research/` were drafted with Claude Code (Claude Opus 5.5) from the
PSI records and tables, and every number was computed from the files in this session. The
underlying data is NASA's. A team member should check the tags against the cited fields before
the submission.
