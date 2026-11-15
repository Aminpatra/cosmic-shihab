# Research pages: Explorer, Scenario, Comparison (#13)

Design, 14 November 2026. Decided with @gheathwahab: Comparison lays two or three investigations
on shared axes (option B), and Explorer searches inside NASA's documents. Everything else was
handed to the builder ("whatever you see fit") and is marked *(call)*.

## Intent

FLARE's core promise is "pick a fire scenario, see which NASA investigations tested something like
it, and why". These three pages are where a researcher or mission planner does that, and where the
judges will look first in the demo:

- **Explorer** (`/explorer`): browse and filter the 24 PSI investigations, search inside their
  documents, open one to read its record and reach its NASA files.
- **Scenario** (`/scenario`): choose an environment and enter only the conditions you know.
- **Comparison** (`/comparison`): the ranked investigations for that scenario, and two or three of
  them laid against it and against each other, condition by condition.

## Goals

- A scenario becomes a ranked, explained comparison in two clicks, and that result is a link
  anyone can open.
- Every number on screen is NASA's or computed from NASA's, with its source next to it.
- Missing data is drawn as missing (hatched, "Not recorded"), never blank or zero.
- Works at 375px and on a laptop, with real loading, empty and error states.

## Non-goals

- Data Visualization (#35), stored SI summaries on these pages (#39), Methodology (#26).
- Changing the ranking backend (#7): no range or bound inputs, no new environments.
- Fixing the fuel names the pipeline produced (#12); report them instead (see Constraints).
- Export of filtered runs as CSV/JSON (master prompt, section 5); not in this task.

## Anti-goals (failure even if it works)

- A field prefilled with a value no NASA source states, or an empty field silently filled.
- A score shown anywhere without "It is not a safety assessment" in view.
- A lunar or Martian scenario that reads as if partial gravity was tested.
- A dashboard of cards and stat tiles; a second authored entrance animation (`DESIGN.md`).
- A fuel picker full of parsing noise in the demo; horizontal scroll at 375px.

## Constraints

- **Deadline** Sunday 15 November 2026, 11:59 p.m. Build order is Scenario, Comparison, Explorer,
  then search, so the core ships first.
- **Files.** This task may edit `frontend/src/pages/Explorer*`, `Scenario*`, `Comparison*` and
  `frontend/src/components/ConditionLanes*` (coordinator `touches`), plus one-line edits to the
  shared `frontend/src/main.jsx` (routes) and `frontend/src/pages.js` (`ready: true`). Helpers go
  in files under those prefixes, e.g. `frontend/src/pages/ScenarioParams.js`.
- **No new dependencies.** React 19, React Router 8, Lucide, plain CSS, `useApi`/`getJSON` from
  `frontend/src/api.js`, `Loading`/`LoadError` from `components/ApiState.jsx`. Pure helpers are
  tested with Node's built-in runner (`node --test frontend/src/pages/`), so `package.json` is not
  touched. Motion is not needed: the lanes' CSS entrance is the page's one motion.
- **Design.** `DESIGN.md` is the system: lanes vocabulary, one text size in data regions, no cards,
  Neon Yellow only for actions, focus and the scenario, Fira Code only for identifiers, results in
  words plus icon, 720px recomposition into stacked records. `/impeccable` is run before each
  page's look is settled (`CLAUDE.md`).
- **API** (all on main, shapes in `backend/README.md`): `GET /api/investigations`,
  `/api/investigations/{accession}`, `/api/files`, `/api/files/{file_id}/download`, `/api/search`,
  `/api/rank`, `/api/rank/options`. Ranking answers in about 0.4 s locally.
- **Data facts that shape the UI** (checked 14 Nov against the committed data):
  `/api/rank/options` lists 81 fuel names, many of them parsing noise ("pre test flow visulation
  data for sample", "c2h5"); ranked items' `tested` fuel lists carry the same noise; FLEX alone has
  6,453 files and 51 publications; search matches any word (3,136 passages for "extinction
  oxygen"); hardware is free text (19 values for 24 investigations). Tell #12's owner about the
  fuel names.

## Approaches

1. **Plain pages over the existing API helpers, state in the URL** *(chosen)*. Each page reads and
   writes its state with React Router's `useSearchParams`, so Scenario hands Comparison a plain
   link and every view is shareable. Comparison reuses `ConditionLanes` with investigations as the
   rows of one figure per condition. Smallest change, matches how Home already works.
2. **A shared React store between Scenario and Comparison.** Rejected: loses shareable links and
   duplicates what the URL already carries.
3. **Recharts range bars for Comparison.** Rejected: not installed, and it would replace the
   design system's signature lanes with a second visual language.

## Scenario (`/scenario`)

```
Environment  Spacecraft · Space station · Lunar habitat · Pressurized rover · Mars habitat · Custom [g]
Oxygen    [    ] %          NASA tested 12–85 %     Spacesuit 100 % · Moon base ≥ 30 % (expected)
Pressure  [    ] psi ▾      NASA tested 0–5 atm     Spacesuit 4.3 · Moon base ≤ 10.2 · Sea level 14.7 psi
Airflow   [    ] cm/s       NASA tested −5.9–85.3
Fuel phase  gas · liquid · solid      Fuel [type-ahead]
Concern     prevention · detection · suppression               [ Compare investigations → ]
```

- **Environment** *(call)*: the six named in the master prompt. The API's `environment` only sets
  gravity, so Space station sends `spacecraft` (0 g) and Pressurized rover sends `lunar` (0.17 g),
  because the challenge groups rovers with the Moon base. Custom shows a gravity field (0 to 1 g,
  `gravity_g`). The UI choice travels separately as `place=` so the page can show it back.
- **Every field starts empty.** Nothing is sent for an empty field.
- **Reference values** *(call)*: small buttons beside a field, each naming its source, the
  [challenge page](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=details):
  Spacesuit 100 % oxygen at 4.3 psi; Moon base and pressurized rovers oxygen "30% or greater" and
  pressure "10.2 psi or less" (expected, not final); Earth at sea level 14.7 psi. Clicking fills the
  field; the bound ones say beside the field that the stated value is a limit and the ranking treats
  it as a single value. No preset fills a spacecraft, station or Mars value (none is sourced).
- **Tested ranges** beside each numeric field come from `/api/rank/options` (min, max, rows).
- **Units** *(call)*: oxygen entered in % (sent as mole fraction, ÷100). Pressure in psi (default,
  as the challenge states psi), kPa or atm, sent in atm (psi ÷ 14.6959, kPa ÷ 101.325), with the
  converted value shown under the field; `p_unit=` keeps the choice. Airflow in cm/s. Values the
  API rejects (oxygen outside 0 to 100 %, negative pressure or airflow) are caught in the form
  before sending, and a 422 from the API is still shown in words.
- **Fuel** *(call)*: free text with suggestions from `/api/rank/options` limited to fuels with at
  least 10 rows (22 names), so noise never appears in the list; any typed text is still sent.
- **Concern**: the three from `/api/rank/options`.
- **Compare investigations** (the one primary button) goes to `/comparison?` with the API's own
  parameter names (`environment`, `gravity_g`, `oxygen`, `pressure`, `flow_velocity`, `fuel`,
  `fuel_phase`, `concern`) plus `place` and `p_unit`. Arriving with those parameters refills the
  form, so "Edit scenario" from Comparison is a link back.

## Comparison (`/comparison`)

```
YOUR SCENARIO  Lunar habitat · oxygen 30 % · pressure 10.2 psi (0.694 atm) · solid   [Edit scenario]
At 0.17 g. NASA's evidence comes from microgravity and normal-gravity tests, not partial gravity.
A relevance score shows how closely NASA's tests match this scenario. It is not a safety assessment.
Weights  oxygen ─●─ 1   pressure ─●─ 1   fuel phase ─●─ 1   Equal weights: FLARE claims…  [Reset]

RANKED (18)                      score  close tests   match  differs  not recorded
[x] FLEX        PSI-69             67   0 of 274         2       1          0
[x] SAFFIRE-II  PSI-101            52   …
[ ] BASS        PSI-25             41   …                pick up to 3
Not ranked (6): DAFT / DAFT-2 PSI-47, no test conditions recorded · …

OXYGEN, %                 (one figure per condition the scenario set; one row per picked investigation)
FLEX        ▕░░▓▓▓▓▓▓│░░░░░▏  Match    tested 12–34 %, closest 30 %
SAFFIRE-II  ▕░░░░▓▓│░░░░░░▏  Differs  tested 21.5–22.1 %, closest 22.1 %
PRESSURE, atm …   AIRFLOW, cm/s …   FUEL PHASE …   CONCERN …   FUEL …

CLOSEST TESTS  FLEX: run 41, PSI-69_Experimental table_FLEX.csv line 42, score 67
               O initial ambient composition; mole fraction 0.3 · Ambient pressure; mmHg 534.3 (0.703 atm, converted)
```

- **Scenario bar** shows what was entered (with the entered unit and the converted value), the
  API's `gravity_note` when set, and the API's `notice` verbatim beside the scores.
- **Weights** *(call)*: one slider per variable the scenario set, 0 to 10, step 1, default 1,
  written to the URL as `weight_<variable>` and re-ranked after a short pause; the API's
  `method.weights_reason` beside them; Reset returns to equal.
- **Ranked table**: rank, acronym and accession, title, score, close tests (`close_tests` of
  `rows_scored` `row_unit`), and the counts of `matches`, `differences`, `unavailable`. A checkbox
  picks up to 3 (a fourth says why it can't be picked); the top 2 are picked on arrival *(call)*;
  picks live in the URL as `pick=PSI-69,PSI-101`. `not_ranked` follows with each `reason`. Each
  name links to its Explorer page.
- **Figures**: one `ConditionLanes` figure per variable in `method.variables`, rows = picked
  investigations in rank order. Row status: in `matches` → Match, in `differences` → Differs, in
  `unavailable` → Not recorded (hatched). Lane kinds:
  - oxygen (shown in %, ×100), pressure (atm), airflow (cm/s): `range`, band = `tested_min` to
    `tested_max`, tick = scenario value. **Shared axis** across rows from `/api/rank/options` min
    and max, widened to include the scenario value (a 100 % spacesuit must stay on the axis).
  - fuel phase (gas, liquid, solid) and concern (prevention, detection, suppression): `stops`.
    `ConditionLanes` is extended so `band` may be a list, because an investigation can test more
    than one phase.
  - fuel: `pair`, theirs = the tested names (the matching ones first, then "+N more"), yours =
    the scenario's fuel.
  - Readout: "tested 12–34 %, closest 30 %" or the tested values in words.
  - The figure's footnote names the source: the investigation's experimental table and DOI.
  - Each row's label is the acronym, with the accession in the unit slot *(call)*. The
    `ConditionLanes` changes stay backwards compatible, so Home's example figure is unchanged.
  - A `pick=` accession missing from `items` is ignored; with one ranked item, one is picked.
- **Closest tests**: each picked investigation's `best_tests` (up to 3): run id, file name, line,
  score, and every value with PSI's original column name and unit, marking converted values with
  the original.
- **States**: no scenario in the URL → a short line and a link to Scenario; the API's `message`
  when no condition was set; `Loading`/`LoadError` for the request; zero items → say so.

## Explorer (`/explorer`)

```
[ Search inside NASA's documents…                    ]
Platform   ISS · Cygnus · computation          Fuel phase  gas · liquid · solid
Role       prevention · detection · suppression · not stated
Gravity    micro · normal                      Data  run table · test-day log · catalogue only …
Showing 9 of 24
FLEX   PSI-69   Flame Extinguishment Experiment   ISS   liquid   micro   run table   6,453 files
```

- **Filters** *(call)*: from `derived.tags.values`, split on `"; "`: platform, fuel phase,
  fire-safety role, gravity level, FLARE data (`flare_data`). OR within a group, AND across groups,
  a count beside each option, state in the URL. Hardware is not a filter (free text).
- **Table**: acronym and accession, title, platform, fuel phase, gravity, FLARE data, file count;
  sorted by accession number (`byAccession` in `catalogue.js`); stacked records below 720px.
- **Document search** (decided): a query box (`q=` in the URL) calling
  `/api/search?q=&limit=10&offset=`; results in their own section above the table: the passage's
  `snippet` with `[[`…`]]` rendered as highlighted text by splitting the string (never as HTML),
  investigation, file name, page, and "Open file" linking to `/api/files/{file_id}/download`
  (about 2 s). "Show more" loads the next 10. A 503 says the search index is not built.

## One investigation (`/explorer/:accession`)

A new route in `main.jsx`, component `frontend/src/pages/ExplorerInvestigation.jsx` *(call)*:

- Title, acronym, accession, DOI link, PSI page link (`derived.page_url`), dates, licence,
  hardware, platform.
- PSI's own objective, hypothesis, approach and research impacts, labelled as the PSI record's text.
- Tags with the field each one cites; what FLARE holds (`derived.experimental_tables`, rows).
- Files: `/api/files?accession=&kind=&limit=100&offset=`, a kind filter with counts from
  `derived.files_by_kind`, 100 at a time, each linking to its download.
- Publications (title, authors, DOI when present), contacts (name, role, affiliation).
- A search box scoped to this investigation (`accession=`), and "Compare against a scenario".
- An unknown accession shows the not-found state.

## Shell edits

`pages.js`: `ready: true` for explorer, scenario and comparison, and the Visualization slot's
`issue` changed from 13 to 35 (the scope change). `main.jsx`: the three routes plus
`explorer/:accession`.

## Done means

- `node --test frontend/src/pages/` passes: unit conversion, scenario ↔ URL, lane building from a
  rank item (match, differs, not recorded, multi-phase stops, axis widening), snippet splitting.
- `npm run build` in `frontend/` passes.
- Each page rendered against the real backend at 375px and 1440px, with no horizontal scroll, and
  the lunar, spacesuit and empty-scenario cases checked by hand.
- `break-ui` on Comparison with worst-case data (three picks, long fuel lists, "DAFT / DAFT-2",
  every lane hatched) before the demo.

## Left to the builder

Exact copy, spacing and visual details within `DESIGN.md` (after `/impeccable`); debounce length;
how the ranked table and figures sit side by side on wide screens; how many tested fuel names fit
before "+N more"; reference-button styling.
