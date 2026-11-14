# Ranking engine design (#7)

Status: draft for approval, 2026-11-14. Approach chosen by @Aminpatra: score each test, then roll up.

## Intent

A researcher or mission planner describes a fire scenario and FLARE lists the NASA investigations
whose tests come closest, best first, with the reasons. It answers "which evidence should I read
first for this situation?", not "is this situation safe?". The brief (master prompt section 5)
requires every result to show its score, why it was selected, what matches, what differs, what is
unavailable and which variables were used; weights configurable and documented; and a notice
whenever lunar or Martian scenarios rest on microgravity evidence.

## Goals, non-goals, anti-goals

- **Goals:** a ranking that changes when the scenario changes and says why; every number traceable
  to a PSI row (file and line); honest about gaps; one API endpoint the Scenario and Comparison
  pages (#13) and the assistant (#10) can call.
- **Non-goals (this version):** scoring by outcome of interest (only FLEX and CFI-G record outcomes
  in common fields); merging tests across investigations; any physical model of fire behaviour.
- **Anti-goals:** a score that reads as a safety rating; a value FLARE filled in that the user did
  not give; an investigation ranked high because it measured only one of the things asked about.

## What the data allows (measured 2026-11-14 on `backend/data/runs/`)

- 2,009 rows from 22 tables in 20 investigations. Standard fields: oxygen (mole fraction) in 1,149
  rows, pressure (atm) in 1,001, flow velocity (cm/s) in 570, fuel text in 1,862.
- Oxygen and pressure come from gas-flame and droplet tests (ACME, CFI, FLEX, CFI-G); flow comes
  from solid-material tests (SAFFIRE, SAME, SPICE). No investigation has all three.
- Solids name a `material` (PMMA, SIBAL, Kapton, ...); gases and liquids only have `text`
  ("C2H4", "Methanol", "75 % Propylene").
- `research/investigation_tags.csv`: fuel phase for all 24; fire-safety role for 8 (16 "not
  stated"); gravity: 20 microgravity, 3 microgravity and normal gravity, 1 normal gravity, none
  partial gravity.

## Approaches considered

1. **Score each test row, roll up to the investigation (chosen).** Explanations can name the
   closest tests; uses all 2,009 rows; follows the brief's recommendation in section 14.
2. Score each investigation's tested ranges. Simpler, but cannot point to tests and treats a range
   tested twice like one tested 200 times.
3. Learned similarity or embeddings. Dropped: nothing records which investigations are relevant
   to a scenario, so there is nothing to train on, and the brief requires an explainable ranking.

## The scenario

All fields optional. Nothing is filled in by FLARE.

| Field | Unit / values |
|---|---|
| `environment` | `spacecraft`, `lunar`, `mars`, `custom`. Sets gravity only: microgravity, 0.17 g, 0.38 g, or `gravity_g` given by the user. Never fills a condition *(my call)* |
| `oxygen` | mole fraction, 0 to 1 |
| `pressure` | atm |
| `flow_velocity` | cm/s |
| `fuel` | free text, matched as below |
| `fuel_phase` | `gas`, `liquid`, `solid` |
| `concern` | `prevention`, `detection`, `suppression` (the challenge's fire-safety roles) |

## Scoring

**Per variable, per row** (0 to 1):

- *Numbers* (oxygen, pressure, flow): `1 - |row - scenario| / tolerance`, floored at 0. The
  tolerance per variable is one quarter of the span of that variable across all rows, computed from
  the data at start-up and shown in the response *(my call: it is derived from the data, not from
  fire science, and says so)*.
- *Fuel:* 1 if the scenario's fuel names the row's material or fuel (case-insensitive, whole words,
  with a small table of formula names: C2H4 = ethylene, CH4 = methane, ...); else 0. *Fuel phase:*
  1 if the investigation's phase tag includes it, else 0.
- *Concern:* 1 if the investigation's fire-safety role includes it; "not stated" counts as
  unavailable.
- A variable the user set but the row does not have scores 0 and is listed as unavailable. It is
  never skipped: skipping would let an investigation that measured one variable outrank one that
  measured three.
- Only a standard field's single `value` is scored. A value whose cell carries a flag from #12
  (`negative_concentration`, `percent_over_100`, ...), or a cell read as a range, list or text,
  counts as unavailable for that row and is shown as PSI wrote it *(my call)*.

**Row score** = weighted mean over the variables the user set. Default weights are all 1
*(my call: equal weights claim no scientific significance)*; the request may override any weight.

**Investigation score** = its best row's score, shown 0 to 100. Alongside, not mixed in:
`close_tests`, the number of rows scoring at least 0.8, so depth of evidence is visible.

**Not ranked** (listed separately, with the reason): the four catalogue-only investigations
(PSI-60, 62, 115, 117), PSI-142 (an index of figures, not tests) and PSI-47 (two sessions with no
conditions) *(my call)*.

**Empty scenario:** no ranking; every investigation listed unranked with "Set at least one
condition to rank" (the brief's concrete check). Choosing only an environment counts as empty,
but the gravity note is still shown.

**Gravity:** for `lunar`, `mars` or a custom gravity above 0, every result carries
`gravity_note`: the evidence is from microgravity (or normal gravity, per the tag), not partial
gravity. Gravity is not in the score, because no investigation could match it.

## Explanation per investigation

`score`, `close_tests`, `rows_scored` and the row unit (`test`, `test_day`, ...);
`matches` and `differences` per variable, each with the scenario value, the investigation's tested
range and the closest test's value; `unavailable` variables; `used_variables` and their weights;
`best_tests` (up to 3: table file, line, PSI run ID, values, row score); `measured_outcomes`
(standard outcome fields present); `gravity_note`; title, acronym and DOI.

Every response carries `notice: "A relevance score shows how closely NASA's tests match this
scenario. It is not a safety assessment."` and `method` (variables, weights, tolerances, version).

## API

- `GET /api/rank?oxygen=0.21&pressure=1&fuel=PMMA&...` returns `{scenario, method, notice,
  items, not_ranked}`. GET, so a scenario is a shareable URL. `weight_<variable>=` overrides a
  weight. 422 for out-of-range values (oxygen outside 0 to 1, negative pressure or flow).
- `GET /api/rank/options` returns, per variable, unit, min, max and row count, plus the fuels and
  materials present with counts, so the Scenario page can build its inputs from real data.

## Code

- `backend/app/runs.py`: loads `backend/data/runs/*.json` once, read-only (like `catalogue.py`).
- `backend/app/ranking.py`: pure functions (closeness, row score, roll-up, explanation) and the
  default weights with their reasons.
- `backend/app/routes/ranking.py`: the two endpoints. Shapes in `backend/README.md` and one line in
  `docs/DECISIONS.md`.
- `backend/tests/test_ranking.py`: the brief's checks on the real data. Changing one value changes
  the scores of the rows it touches and the explanation names it; an empty scenario is explained,
  not an error; a lunar scenario shows the gravity note on every result; a variable an
  investigation lacks is listed as unavailable; FLEX's 757.7 mmHg still shows as calculated from
  757.7 mmHg; weights change the order.

## Left to the builder

Formula-name table contents, response field order, rounding (scores to whole numbers, values to
PSI's precision), and how ties are broken (more close tests first, then accession).
