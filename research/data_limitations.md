# Data limitations

What FLARE's PSI data can and cannot support. Every problem below was found by reading the files
on 14 November 2026; the counts come from the files themselves. Per-file details are in the
`limitations` column of `dataset_inventory.csv`.

## What FLARE holds

- **Catalogue for all 24 combustion investigations**, from PSI's records: title, DOI, licence,
  objective, hardware, people, publications and the full list of 60,866 files (13.5 TB). None of
  those files is stored except the tables below.
- **22 experimental tables (2,009 rows)** for 20 investigations, plus two workbooks (BASS-II test
  matrix, ACME CFI-G chamber calculator) that have **not been profiled**.
- **No run data** for PSI-60, PSI-62, PSI-115 and PSI-117. These are ground studies that model
  other investigations' data. FLARE shows them as "catalogued, no run data in FLARE".
- **PSI-142's table is an index of 8 figures in 6 publications**, not test data.
- Only 12 of the tables have one row per test (`flare_data = run table`). Six are test-day logs
  (date, fuel, flames ignited) and FLEX-2's is a test matrix of ranges. They describe what was
  tested, not what happened.
- **No documents have been read** (final reports, experimental-detail files, publications). Any
  fact that only those documents hold is missing from the tags. Indexing them is #18.

## The tags are judgements from short texts

- Tags come from the record's own fields (`objective`, `hypothesis`, `approach`, `flightProgram`,
  `experimentHardware`) and the tables. Each one cites its field in `investigation_tags.csv`.
- **Fire-safety role is strict.** It is tagged only when the aim is stated, which leaves 16 of the
  24 investigations `not stated`. Several of them (DAFT, PSI-60, PSI-62, PSI-115) name detection,
  suppression or prevention only as an expected benefit in `researchImpacts`; that wording is
  quoted in `notes`. A looser rule would tag them; say which rule you use when quoting a count.
- **Prevention is FLARE's mapping.** BASS, BASS-II and Saffire I to III compare microgravity
  flammability with NASA's material screening test (NASA-STD-6001). FLARE tags that comparison
  `prevention`; the records do not use the word.
- **SLICE's facility comes from the challenge page.** Its PSI record has no hardware, research
  area or dates.
- **Fuel phase of the ground studies** is the phase of the fuel they model, not of anything
  burned. DAFT burned nothing (`none (no fuel burned)`).
- **"Microgravity" covers orbit, a free-flying Cygnus and drop towers.** PSI-10's record mentions
  drop-tower tests as well as ISS tests; its tables do not say which rows, if any, came from drop
  towers.

## Record and table disagree

| Investigation | Disagreement |
|---|---|
| PSI-39 CFI | Table test dates are in 2017; the record's investigation start date is 10-01-2020. The record's approach gives 0.25 to 0.5 atm; its objective gives 0.25 to 5 atm and the table 0.5 to 5 atm |
| PSI-159 ACME CFI-G | Table fuels are ethane, propane, butane; the objective lists propane, n-butane, n-pentane |
| PSI-100 SAFFIRE-III | `flightProgram` says ISS; the burn ran in Cygnus after it left the ISS |
| PSI-98 vs PSI-100 | Sample length and width are swapped between the two tables (40.6 × 94 cm against 94 × 40.6 cm) |

## Problems inside the tables

**Encoding and characters**
- PSI-69 FLEX is Windows-1252, not UTF-8; an en dash (byte 0x96) marks a missing value. Read it
  with `cp1252`, or the dashes become errors.
- PSI-25, PSI-26 and PSI-142 begin with a byte-order mark. Read with `utf-8-sig`.
- PSI-99 SAFFIRE-II stores µ as `?` (`?-g Burn Length`). FLEX's gas columns lost their subscripts
  (`O`, `N`, `CO` are O2, N2, CO2).

**Values that cannot be right**
- PSI-21 CLD Flame: fuel bottles `C2H5` to `C2H11` and `CH5` to `CH14`. PSI-23 s-Flame:
  atmospheres `N3` to `N6`. Both look like a spreadsheet auto-incrementing `C2H4`, `CH4` and `N2`.
  Read them as the base formula, and say so.
- PSI-20 BRE: oxygen `2100%` and `3400%`, most likely 21% and 34% formatted twice.
- PSI-159 CFI-G: 2 `#VALUE!` cells in the inverse table's peak burner temperature (K) and 4
  `#DIV/0!` cells in the normal table's Tad and Zst (spreadsheet errors).
- PSI-69 FLEX: one ambient pressure of 0 mmHg (the others are 526 to 2,320 mmHg).
- PSI-107 SPICE: 8 negative air rates. PSI-25 BASS-II: 13 negative initial CO readings (ppm).
- PSI-99 SAFFIRE-II: thickness `037 mm`, probably 0.37 mm.

**Inconsistent writing of the same thing**
- Mixed case in PSI-159 (`Inverse` 64 / `inverse` 90; `Yes`/`yes`, `No`/`no`); `flash` also
  appears as a hot-ignition outcome.
- PSI-107 fuels `75 % Propylene` and `75% Propylene`; PSI-20 `100% C2H4` and `100%C2H4`.
- Units written inside cells instead of headers (SAFFIRE-II and III, CFI pressure).
- PSI-25 BASS-II cells hold several settings separated by spaces (`10   15 (brief)   10   8`);
  its fan and air columns are panel readings, not velocities.
- PSI-20 BRE oxygen cells hold lists (`21; 26.5; 34`).

**Duplicates and gaps**
- Repeated identifiers: FLEX `193F001`, SAME-R test `57`, several CFI `Flex Number` values.
- Years missing: SPICE gives day of the year only; SAME-R gives day and month only.
- Large blank shares: CFI-G normal `Cool flame?` (171 of 179), SAME-R aging times (41 to 42 of
  109), FLEX extinction diameter (49 of 274).
- FLEX's `Burning rate; mm`: the unit is doubtful, since burning-rate constants are normally
  mm²/s. Check the FLEX documentation before using it as a number.
- PSI-159 `TFP`, SAME-R `Rt/R0` and FLEX's `Disruption` outcome are not defined in the table or
  the record.

## What this means for FLARE

- Rank and model only the run tables with enough rows (Tier 1 in `docs/DATA_PLAN.md`). Show the
  others in full and say how few rows they have.
- Fix the problems above in the processing step (#12), not in `datasets/`, which stays as PSI
  published it. Record each fix there.
- Licence: 23 investigations are CC0-1.0. **PSI-10 states no licence**; keep the note on it until
  PSI confirms one.
- The NASA web pages in `source_references.csv` marked "not accessed" have not been read. The
  hardware families and roles stated here do not rely on them.

**AI use:** the files in `research/` were drafted with Claude Code (Claude Opus 5.5) from the
PSI records and tables, and every number was computed from the files in this session. The
underlying data is NASA's. A team member should check the tags against the cited fields before
the submission.
