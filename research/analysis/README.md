# Exploratory analysis of the PSI runs

Master prompt section 4, "Analysis requirements" (#27). What the processed experimental tables
measure, what they miss, where their tests sit, and which patterns between conditions and outcomes
the data can show. Every number below comes from `explore_runs.py`; the full tables are in
`summary.md` and the CSV files.

```
python3 -m pip install -r research/analysis/requirements.txt    # once: matplotlib, for the charts
python3 research/analysis/explore_runs.py                         # rewrites everything in this folder
python3 -m unittest discover -s research/analysis -v              # checks the committed output is current
```

**Data:** `backend/data/runs/` (22 PSI tables, 2,009 rows, retrieved 14 November 2026), written by
`pipeline/process_tables.py`. Only 14 tables in 12 investigations have one row per test; the rest
are test-day logs, sessions, a fuel summary and a figure index, and are left out of anything
counted per test.

| File | What it holds |
|---|---|
| `summary.md` | The tables below in short; regenerated, never edited |
| `column_profile.csv` | Every PSI column: kinds of cells, each kind of missing, distinct values, min and max |
| `standard_coverage.csv` | Per table and comparable field: rows with one value, a list or range, text only, missing, suspect |
| `condition_ranges.csv` | Tested range of oxygen, pressure, flow and burn time per table, suspect values left out |
| `suspect_values.csv` | 117 values that look wrong, each with file, line, column, original text and the rule |
| `flex_relationships.csv` | FLEX: Spearman rank correlation of each condition with each outcome, per fuel |
| `flex_test_end.csv` | FLEX: how tests ended, per fuel and band of initial oxygen |
| `figures/` | The three charts below (PNG, 200 dpi, dark brand surface) |

## Charts

**`figures/coverage.png`: which comparable fields each test table gives.** One row per test table,
one column per comparable field, shaded by the share of rows with one usable value; hatched where
the table has no such column. Read it to see which investigations can be compared on which field.

**`figures/condition_space.png`: where the tests sit in oxygen and pressure.** One panel per table
that records both; that table's tests in blue over every table's tests in grey. Empty areas were
not tested in these tables. In the two inverse-flame tables the oxygen is the burner stream's, not
the surrounding gas's, so they do not describe a cabin atmosphere.

**`figures/flex_burning_rate.png`: FLEX droplet burning rate by oxygen.** One dot per FLEX test,
one panel per fuel, orange where the gas contained helium. Pressure, droplet size and the inert gas
also vary across these dots, so the chart shows a pattern in these tests, not a cause.

## Findings

1. **Few fields can be compared across investigations.** Of the 14 test tables, fuel is recorded
   in 13, oxygen in 9, pressure in 6, flow velocity in 6, burn time in 5 and how the test ended in
   3. Only FLEX and the two ACME CFI-G tables give oxygen, pressure and an outcome together.
2. **The tests cluster near one atmosphere and below 40% oxygen.** Of the 726 tests that record
   oxygen and pressure around the flame (inverse flames left out), 61% ran between 0.9 and 1.1 atm,
   none above 0.40 oxygen (mole fraction), and none below 0.5 atm.
3. **The challenge's reference points are mostly outside the tested range.** The spacesuit
   (100% oxygen at 4.3 psi, 0.29 atm) is outside every table. For the Moon base and pressurized
   rover (oxygen 30% or more, 10.2 psi or less, not final), 20 tests match, all ACME CFI-G normal
   flames; 17 FLEX tests ran at 0.30 to 0.34 oxygen and 10.3 to 10.5 psi, just above the bound.
4. **117 values look wrong; the pipeline flags 41 of them.** Besides the pipeline's own flags
   (negative CO readings, "3400%" oxygen, impossible formulas, a leading zero), the analysis finds: FLEX test 114 at 0 mmHg although it burned for 18.9 s; 8 SPICE air rates below
   zero; 50 rows that repeat an earlier row exactly (SPICE 34, CFI 8, ACME E-FIELD 8). It also finds
   ACME BRE's "3400%" and "2100%" converted to oxygen 34 and 21 in `standard`: the cell is flagged
   but the converted value is not. 15 category spellings differ only in case or spaces
   ("75 % Propylene" and "75% Propylene").
5. **In FLEX, burning rate rises with oxygen in both fuels**, ρ 0.43 for heptane (107 tests) and
   0.69 for methanol (151), and the rise is visible in `flex_burning_rate.png`.
6. **How a FLEX test ended shifts with oxygen.** Below 0.18 oxygen all 54 methanol tests ended in
   extinction; above 0.22, 22 of 33 heptane tests ended in disruption. Burn time therefore measures
   different things in different tests, and its correlation with oxygen (ρ 0.77 heptane, 0.41
   methanol) mixes those endings. It is not a burn-time effect of oxygen.

## Caveats

- **Correlation is not cause.** In FLEX, oxygen also moves with droplet size (ρ 0.30 heptane, 0.25
  methanol), and helium with pressure (ρ -0.33 and -0.34). No correlation here controls for the
  others.
- **Outcomes are not all comparable.** In CFI-G, a burn time of 0 means no ignition, and a test
  ended by "FT" (flow termination) has a burn time set by the operator, not by the flame. FLEX
  burn times end in extinction, completion or disruption (finding 6).
- **Units as PSI wrote them.** FLEX's burning-rate column is headed "mm"; a burning-rate constant
  is usually mm²/s, but PSI does not say so and FLARE does not change it.
- **Suspect values are left out of ranges, charts and correlations, never corrected.** They stay in
  `backend/data/runs/` exactly as PSI wrote them.
- Values written with `~`, `<` or `>` are left out of the correlations.

**Validation** (`validate-data`, 14 November 2026): share with the caveats above. Recounted from the
raw PSI files in `datasets/`, not from the processed data: 274 FLEX tests, one at 0 mmHg, 8
negative SPICE air rates, 50 duplicate rows, and the heptane oxygen and burn-time ρ of 0.77. In
`standard_coverage.csv` and `column_profile.csv` every row's parts add up to its total.

## For other tasks

- **#16 (FLEX model):** how a test ended depends strongly on oxygen and fuel (finding 6), which makes
  it a better target than burn time. Leave out test 114 and the approximate burn times.
- **#13 (Visualization page):** the three charts read the same rows that `/api/runs/rows` serves
  (#25), so they can be redrawn there with the same captions; hatch what was not recorded, as
  `DESIGN.md` does.
- **#7 (ranking):** the zero pressure and negative air rates are not flagged, so ranking scores them
  and they widen its tolerances (pressure from 0 atm instead of 0.43).
- **`pipeline/process_tables.py`:** flagging those values, and not converting flagged cells into
  `standard`, would fix both of the above at the source.

**AI use:** this analysis and its code were written with Claude Code (Claude Opus 5.5) and reviewed
by the team. The data is NASA's; the charts are drawn from it and contain no generated content.
