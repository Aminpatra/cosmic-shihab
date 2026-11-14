# How FLARE ranks investigations

The ranking answers one question: **how closely did NASA's actual tests match this scenario?** It
compares the scenario with every test row NASA recorded, not with a summary of the investigation,
and it shows its working for every result. It is not a safety assessment, and every ranking says
so: "A relevance score shows how closely NASA's tests match this scenario. It is not a safety
assessment."

## What the visitor sets

Any of these, and only these. A field left empty takes no part in the score.

| Variable | Compared with | Unit |
|---|---|---|
| Oxygen | the test's oxygen | mole fraction (entered as %) |
| Pressure | the test's pressure | atm (entered in psi, kPa or atm and converted) |
| Airflow | the test's flow velocity | cm/s |
| Fuel | the fuel or material the test burned | words, with formulas read as names (C7H16 = heptane) |
| Fuel phase | the investigation's tag (gas, liquid, solid) | |
| Fire-safety role | the investigation's tag (prevention, detection, suppression) | |
| Environment | sets the gravity only (0 g spacecraft and station, 0.17 g lunar habitat and rover, 0.38 g Mars, or a custom value) | g |

## Scoring one test

Each variable the visitor set gets a part between 0 and 1:

- **A number** (oxygen, pressure, airflow): `1 − |test value − scenario value| ÷ tolerance`, never
  below 0. The tolerance is a quarter of the range that variable spans across all of NASA's
  scorable tests: 0.1825 for oxygen (mole fraction), 1.25 atm for pressure and 22.8 cm/s for
  airflow. It comes from the data, not from fire science, and FLARE says so.
- **Fuel:** 1 if every word of the typed fuel appears in the test's fuel, otherwise 0.
- **Fuel phase and fire-safety role:** 1 if the investigation's tag includes the visitor's value,
  otherwise 0.
- **Not recorded:** if the test, or the investigation's record, does not state the variable, the
  part is 0. Measuring less never ranks higher.
- **Suspect values:** a value FLARE's profiling flagged as looking wrong is treated as not
  recorded.

The test's score is the weighted mean of its parts. All weights start equal, because FLARE claims
no variable matters more for fire safety; the visitor can change any weight, and a weight of 0
leaves that variable out.

## From tests to a ranked investigation

- **Score:** the investigation's best test, as a number from 0 to 100.
- **Close tests:** how many of its tests score 0.8 or more.
- **Order:** by score, then by the number of close tests, then by PSI accession number.
- **Why it ranked here:** for each variable used, the result says whether it **matches** (the best
  test's part is 0.8 or more), **differs** (with the tested range and the closest value, in the
  scenario's unit), or is **unavailable** (no test recorded it). It also lists the variables and
  weights used and its three closest tests, with NASA's own column names and units, so each can be
  found in the PSI table.
- **Not ranked:** an investigation with no test table, or whose table records no test
  conditions, is listed apart with the reason (for the Moon base scenario: "No experimental table: catalogue only" for
  four, "No test conditions recorded" and "An index of published figures, not tests" for one each).
- **No scenario:** with nothing set, FLARE ranks nothing and says "Set at least one condition to
  rank."

## Gravity

Gravity is never scored, because NASA's PSI holds no combustion tests in partial gravity: its
tests ran in microgravity or in normal gravity. When the scenario is above 0 g, every result says
so, for example "This scenario is at 0.17 g. The evidence comes from microgravity tests, not
partial gravity." FLARE never interpolates between microgravity and Earth.

## An example

The Moon base scenario the challenge page states (lunar habitat, 30 % oxygen, 10.2 psi):

| Rank | Investigation | Score | Tests close to the scenario |
|---|---|---|---|
| 1 | FLEX (PSI-69) | 100 | 59 of 274 |
| 2 | ACME CFI-G (PSI-159) | 94 | 12 of 333 |
| 3 | ACME/Flame Design (PSI-10) | 87 | 15 of 327 |
| 4 | CFI (PSI-39) | 73 | 0 of 87 |
| 5 | BASS-II (PSI-25) | 29 | 0 of 129 |

18 investigations are ranked and 6 are listed as not ranked. Each of the 18 carries the gravity
note, because none tested at 0.17 g.

## What the ranking does not do

It does not compare research objectives or score which outcomes an investigation measured (it
lists them), and it takes one number per condition, not a range such as "30 % or greater". It
does not say whether an environment is safe. These limits are listed in `limitations.md` and
`features.md`.

<!--
For the team (not for the form). Draft for the ranking-method part of the package, issue #15.
Everything is from backend/app/ranking.py (method version "1") on main at 25b8889:
- Variables, units, gravity values: NUMERIC, UNITS, VARIABLES, GRAVITY; frontend PLACES
  (frontend/src/pages/ScenarioParams.js) for which places map to which environment.
- Closeness, tolerance: closeness(), tolerances() (a quarter of the span of every scorable row);
  values printed by ranking.tolerances() on 15 Nov 2026: oxygen 0.1825, pressure 1.25,
  flow_velocity 22.8.
- Fuel: fuel_matches(), FORMULAS. Tags: _part() with tag_values() (fuel_phase, fire_safety_role).
- Flagged values skipped: scorable_value() (a cell with `flags` is not scored).
- Weighted mean, unavailable as 0: score_row(). Weights: DEFAULT_WEIGHTS, WEIGHTS_REASON.
- Score, close tests (CLOSE = 0.8), match/differ/unavailable, best_tests[:3]: _rank_one().
- Order: rank() sort key (-score, -close_tests, accession number).
- Not ranked and EMPTY: rank(), _structural_reason().
- Gravity note: _gravity_note(); PSI has no partial-gravity combustion data per the challenge page
  (master prompt section 5, "Partial gravity, stated exactly").
- Example: ranking.rank(Scenario(environment="lunar", oxygen=0.3, pressure=0.69407113)) on
  15 Nov 2026 (the Moon base preset link), and live on screen (submission/test_report.md).
-->
