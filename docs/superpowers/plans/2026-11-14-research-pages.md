# Research Pages (Explorer, Scenario, Comparison) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the Scenario, Comparison and Explorer pages (plus one page per investigation) for issue #13.

**Architecture:** Each page is a React component over the existing FastAPI endpoints, with its state
in the URL through React Router's `useSearchParams`. Everything that can be computed without React
(unit conversion, URL ↔ form, lanes from a rank item, filters, snippet splitting) lives in plain
`.js` helper modules tested with Node's built-in runner. Comparison reuses `ConditionLanes` with
investigations as rows.

**Tech Stack:** React 19, React Router 8, Lucide, plain CSS, Vite 8; `node:test` for helpers; FastAPI
backend already on main.

**Spec:** `docs/superpowers/specs/2026-11-14-research-pages-design.md`

## Global Constraints

- Edit only `frontend/src/pages/Explorer*`, `frontend/src/pages/Scenario*`, `frontend/src/pages/Comparison*`, `frontend/src/components/ConditionLanes*`, plus route lines in `frontend/src/main.jsx` and entries in `frontend/src/pages.js`; append-only `docs/DECISIONS.md` and `docs/ai-use/gheathwahab.md`.
- No new dependencies; `frontend/package.json` is not touched. Helpers must import nothing but other plain `.js` files (no JSX, no CSS), so Node can run their tests.
- `DESIGN.md` governs every visual choice: lanes vocabulary, one 0.9375rem text size in data regions, no cards or stat tiles, Neon Yellow only for actions, focus and the scenario, Fira Code only for identifiers, results as word + icon, stacked records below 720px, no second entrance animation.
- The API's `notice` ("A relevance score shows how closely NASA's tests match this scenario. It is not a safety assessment.") is shown verbatim wherever a score is visible; `gravity_note` is shown whenever the API returns one.
- No field is ever filled without the user's click; reference values name the challenge page as source: `https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=details`.
- Every backend call goes through relative `/api/...` paths (`getJSON`/`useApi` in `frontend/src/api.js`, which this task does not edit).
- Commit after each task with a message that says why, ending `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; call the coordinator `heartbeat("gheathwahab", 13)` after every commit.

## Review Focus

- A mole fraction typed into the % field (`0.3`) gets a visible hint ("did you mean 30 %?"), not a silent 0.3 % scenario. → Task 1 test `validate … hints`.
- A decimal comma (`10,2`) or stray spaces are read as 10.2, not rejected. → Task 1 test `parseNumber`.
- A hand-edited or stale link (`oxygen=abc`, `p_unit=bar`, `place=moon`, unknown `pick=`) falls back to empty or default values and never crashes. → Task 1 `hand-edited URL`, Task 3 `parsePicks`.
- A tested range that is one value (20–20 cm/s) still draws a visible band and reads "tested 20 cm/s". → Task 3 `single-value band`, and the minimum band width in Task 3's `ConditionLanes.css`.
- A scenario outside everything NASA tested (100 % oxygen, the spacesuit reference) stays on the axis. → Task 3 `axis widens`.

## File Structure

| File | Responsibility |
|---|---|
| `frontend/src/pages/ScenarioParams.js` (+ `.test.js`) | Places, reference values, unit conversion, validation, form ↔ URL, the `/rank` path |
| `frontend/src/pages/Scenario.jsx`, `Scenario.css` | The Scenario form |
| `frontend/src/pages/ComparisonLanes.js` (+ `.test.js`) | Axes, statuses, lanes and figures from `/api/rank`, picks |
| `frontend/src/pages/Comparison.jsx`, `Comparison.css` | Scenario bar, weights, ranked table, figures, closest tests |
| `frontend/src/components/ConditionLanes.jsx`, `.css` | Stops lanes accept a list of tested stops and a hatched "none" state; single-value bands stay visible |
| `frontend/src/pages/ExplorerFilters.js` (+ `.test.js`) | Tag filters and snippet splitting |
| `frontend/src/pages/Explorer.jsx`, `Explorer.css` | Investigation list with filters, hosts the search |
| `frontend/src/pages/ExplorerSearch.jsx` | Document search box and results (used by both Explorer pages) |
| `frontend/src/pages/ExplorerInvestigation.jsx` | `/explorer/:accession` |

Run all helper tests with: `node --test "frontend/src/pages/*.test.js"` (from the repo root).

Run the app for visual checks (two background shells):
`cd backend && .venv/Scripts/python -m uvicorn main:app --port 8000` and `cd frontend && npm run dev -- --port 5173`.
Screenshot command (Chrome is installed):
`"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --hide-scrollbars --window-size=375,2400 --virtual-time-budget=8000 --screenshot="<scratchpad>/<page>-375.png" "http://localhost:5173/<path>"`, and again with `--window-size=1440,2400`.

---

### Task 1: Scenario model helpers

**Files:**
- Create: `frontend/src/pages/ScenarioParams.js`
- Test: `frontend/src/pages/ScenarioParams.test.js`

**Interfaces:**
- Produces:
  - `PLACES: {id, label, environment}[]`, in order `spacecraft` Spacecraft → `spacecraft`, `station` Space station → `spacecraft`, `lunar` Lunar habitat → `lunar`, `rover` Pressurized rover → `lunar`, `mars` Mars habitat → `mars`, `custom` Custom → `custom`.
  - `PRESSURE_UNITS = ['psi', 'kPa', 'atm']`; `ATM_IN = {psi: 14.6959, kPa: 101.325, atm: 1}`.
  - `REFERENCE_SOURCE = {label: 'Flame in Freefall challenge page, NASA Space Apps 2026', url}` (URL in Global Constraints).
  - `REFERENCES = {oxygen: [{label: 'Spacesuit', value: 100}, {label: 'Moon base and rovers', value: 30, bound: 'at least', note: 'expected, not final'}], pressure: [{label: 'Spacesuit', value: 4.3}, {label: 'Moon base and rovers', value: 10.2, bound: 'at most', note: 'expected, not final'}, {label: 'Earth at sea level', value: 14.7}]}` (pressure values in psi).
  - `EMPTY_FORM = {place: '', gravity: '', oxygen: '', pressure: '', pUnit: 'psi', flow: '', fuel: '', fuelPhase: '', concern: ''}`; every value is the string the user typed (oxygen in %, pressure in `pUnit`).
  - `parseNumber(text: string) -> number | null`; `toAtm(value: number, unit) -> number`; `fromAtm(atm: number, unit) -> number`.
  - `validate(form) -> {errors: {[field|'form']: string}, hints: {[field]: string}}`.
  - `formToParams(form) -> URLSearchParams`; `paramsToForm(params: URLSearchParams) -> form`.
  - `hasScenario(params) -> boolean` (true when any of `oxygen`, `pressure`, `flow_velocity`, `fuel`, `fuel_phase`, `concern` is set).
  - `rankPath(params) -> string`: `/rank?` plus only `environment`, `gravity_g`, `oxygen`, `pressure`, `flow_velocity`, `fuel`, `fuel_phase`, `concern` and `weight_*`, in the order they appear.

- [ ] **Step 1: Write the failing tests**

```js
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { EMPTY_FORM, parseNumber, toAtm, formToParams, paramsToForm, validate, hasScenario, rankPath } from './ScenarioParams.js'

test('parseNumber reads trimmed numbers and a decimal comma', () => {
  assert.equal(parseNumber(' 10,2 '), 10.2)
  assert.equal(parseNumber('4.3'), 4.3)
  assert.equal(parseNumber(''), null)
  assert.equal(parseNumber('abc'), null)
})

test('pressure converts to atm', () => {
  assert.ok(Math.abs(toAtm(14.6959, 'psi') - 1) < 1e-9)
  assert.ok(Math.abs(toAtm(101.325, 'kPa') - 1) < 1e-9)
  assert.equal(toAtm(0.7, 'atm'), 0.7)
})

test('a rover scenario becomes API parameters, leaving empty fields out', () => {
  const p = formToParams({ ...EMPTY_FORM, place: 'rover', oxygen: '30', pressure: '10.2', fuelPhase: 'solid' })
  assert.equal(p.get('environment'), 'lunar')
  assert.equal(p.get('place'), 'rover')
  assert.equal(p.get('oxygen'), '0.3')
  assert.equal(p.get('pressure'), '0.694071')
  assert.equal(p.get('p_unit'), 'psi')
  assert.equal(p.get('fuel_phase'), 'solid')
  assert.equal(p.has('flow_velocity'), false)
  assert.equal(p.has('gravity_g'), false)
})

test('the form survives a round trip through the URL', () => {
  const form = { ...EMPTY_FORM, place: 'custom', gravity: '0.38', oxygen: '21', pressure: '101.325', pUnit: 'kPa', flow: '5', fuel: 'PMMA', concern: 'suppression' }
  assert.deepEqual(paramsToForm(formToParams(form)), form)
  assert.equal(paramsToForm(formToParams({ ...EMPTY_FORM, pressure: '10.2' })).pressure, '10.2')
})

test('a hand-edited URL falls back instead of breaking', () => {
  const form = paramsToForm(new URLSearchParams('oxygen=abc&p_unit=bar&pressure=1&place=moon'))
  assert.equal(form.oxygen, '')
  assert.equal(form.pUnit, 'psi')
  assert.equal(form.pressure, '14.6959')
  assert.equal(form.place, '')
})

test('validate catches what the API would reject, and hints at a fraction typed as percent', () => {
  assert.equal(validate({ ...EMPTY_FORM, oxygen: '120' }).errors.oxygen, 'Oxygen must be between 0 and 100 %.')
  assert.equal(validate({ ...EMPTY_FORM, oxygen: 'abc' }).errors.oxygen, 'Enter a number.')
  assert.equal(validate({ ...EMPTY_FORM, pressure: '-1' }).errors.pressure, 'Pressure cannot be negative.')
  assert.equal(validate({ ...EMPTY_FORM, flow: '-2' }).errors.flow, 'Airflow cannot be negative.')
  assert.equal(validate({ ...EMPTY_FORM, place: 'custom', gravity: '2', oxygen: '21' }).errors.gravity, 'Gravity must be between 0 and 1 g.')
  assert.match(validate({ ...EMPTY_FORM, oxygen: '0.3' }).hints.oxygen, /30 %/)
  assert.equal(validate({ ...EMPTY_FORM, place: 'lunar' }).errors.form, 'Enter at least one condition. FLARE ranks only on what you set.')
  assert.deepEqual(validate({ ...EMPTY_FORM, fuelPhase: 'gas' }).errors, {})
})

test('hasScenario and rankPath', () => {
  assert.equal(hasScenario(new URLSearchParams('place=rover&environment=lunar')), false)
  assert.equal(hasScenario(new URLSearchParams('oxygen=0.3')), true)
  const p = new URLSearchParams('environment=lunar&oxygen=0.3&place=rover&p_unit=psi&pick=PSI-69&weight_oxygen=3')
  assert.equal(rankPath(p), '/rank?environment=lunar&oxygen=0.3&weight_oxygen=3')
})
```

- [ ] **Step 2: Run and see them fail.** `node --test "frontend/src/pages/*.test.js"`. Expected: FAIL, cannot find `./ScenarioParams.js`.
- [ ] **Step 3: Implement `ScenarioParams.js`** with the interfaces above. Numbers written to the URL and read back are rounded with `Number(x.toPrecision(6))`, which is what makes `10.2 psi → 0.694071 atm → 10.2` round-trip. `gravity_g` is written only for `custom`. Unknown `place` or `p_unit`, and non-numeric numbers, read back as `''` or `'psi'`.
- [ ] **Step 4: Run the tests.** Expected: all pass.
- [ ] **Step 5: Commit** (`ScenarioParams.js`, its test) and heartbeat.

### Task 2: Scenario page

**Files:**
- Create: `frontend/src/pages/Scenario.jsx`, `frontend/src/pages/Scenario.css`
- Modify: `frontend/src/main.jsx` (route `scenario`), `frontend/src/pages.js` (scenario `ready: true`; Visualization `issue: 35`)

**Interfaces:**
- Consumes: Task 1 exports; `useApi('/rank/options')` → `{variables: {oxygen, pressure, flow_velocity: {unit, min, max, rows}}, fuels: [{name, rows}], fuel_phases, concerns, environments}`.
- Produces: navigation to `/comparison?${formToParams(form)}`; arriving at `/scenario?…` prefills via `paramsToForm`.

- [ ] **Step 1: Set the look.** Run `/impeccable` (shape) once for all three pages with the spec and `DESIGN.md`; its answers govern the CSS of Tasks 2, 4, 6 and 8. Note any decision it makes that changes the spec in the spec's "Left to the builder" section.
- [ ] **Step 2: Build the form** as the spec's Scenario sketch: place choice (radio group, Custom reveals the gravity field), oxygen %, pressure with a `psi | kPa | atm` select and the converted atm value beneath, airflow cm/s, fuel phase and concern as radio groups with a "none" choice, fuel as `<input list>` over fuels with `rows >= 10`. Beside each numeric field: "NASA tested {min}–{max} {unit}" from the options (oxygen shown in %), and the reference buttons from `REFERENCES` whose click fills that field (pressure references convert into the selected unit); bound references show "{bound} {value} ({note})" beside the field after the click, and one line names `REFERENCE_SOURCE` as a link. Errors and hints from `validate` sit under their fields; the "Compare investigations" primary button is disabled while `errors` is non-empty and `errors.form` is shown beside it. Loading/error states for the options use `Loading`/`LoadError`.
- [ ] **Step 3: Wire the route and slot**: `{ path: 'scenario', element: <Scenario /> }` in `main.jsx`; `ready: true` on `/scenario` and `issue: 35` on `/visualization` in `pages.js`.
- [ ] **Step 4: Verify.** `cd frontend && npm run build` passes; with both servers running, screenshot `/scenario` and `/scenario?place=rover&environment=lunar&oxygen=0.3&pressure=0.694071&p_unit=psi` at 375 and 1440: the second shows Pressurized rover, 30 %, 10.2 psi prefilled; no horizontal overflow at 375.
- [ ] **Step 5: Commit** and heartbeat.

### Task 3: Comparison lanes helpers and the `ConditionLanes` extension

**Files:**
- Create: `frontend/src/pages/ComparisonLanes.js`
- Test: `frontend/src/pages/ComparisonLanes.test.js`
- Modify: `frontend/src/components/ConditionLanes.jsx` (`StopsTrack`), `frontend/src/components/ConditionLanes.css`

**Interfaces:**
- Consumes: `nameOf(inv)` from `frontend/src/catalogue.js`.
- Produces:
  - `LANE_VARIABLES = {oxygen: {label: 'Oxygen', unit: '%', scale: 100, kind: 'range'}, pressure: {label: 'Pressure', unit: 'atm', scale: 1, kind: 'range'}, flow_velocity: {label: 'Airflow', unit: 'cm/s', scale: 1, kind: 'range'}, fuel_phase: {label: 'Fuel phase', kind: 'stops', stops: ['gas', 'liquid', 'solid']}, concern: {label: 'Concern', kind: 'stops', stops: ['prevention', 'detection', 'suppression']}, fuel: {label: 'Fuel', kind: 'pair'}}`.
  - `formatValue(n: number) -> string` (at most 3 significant digits, `en-US`).
  - `axisFor(variable, options, scenarioValue) -> {min, max, ticks: number[]}` in display units, covering the data range and the scenario value, with 3 to 6 round ticks.
  - `statusOf(item, variable) -> 'match' | 'differs' | 'missing'`; `countsOf(item) -> {match, differs, missing}`.
  - `laneFor(item, variable, scenario, axis) -> lane` in `ConditionLanes`' shape: `label = nameOf(item)`, `unit = item.accession`, plus `status`, `readout`, `source`, and per kind `band`/`value`/`axis`, `stops`/`band: number[]`/`value`, or `theirs`/`yours`.
  - `figuresFor(result, picks: string[], options) -> {variable, caption, summary, lanes}[]`, one per `result.method.variables`, lanes in rank order.
  - `parsePicks(param: string | null, items) -> string[]`: valid accessions from `param`, at most 3; when `param` is null, the first two items.
- `ConditionLanes` stops lanes accept `band` as a number (Home, unchanged) or a list; an empty list draws the stops over the 135° hatch; a range band whose ends are equal keeps a visible minimum width.

- [ ] **Step 1: Write the failing tests** with a fixture shaped like `/api/rank` output:

```js
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { axisFor, statusOf, countsOf, laneFor, figuresFor, parsePicks } from './ComparisonLanes.js'

const OPTIONS = { variables: { oxygen: { unit: 'mole fraction', min: 0.12, max: 0.85 }, pressure: { unit: 'atm', min: 0, max: 5 }, flow_velocity: { unit: 'cm/s', min: -5.92, max: 85.28 } } }
const SCENARIO = { oxygen: 0.3, pressure: 0.7, flow_velocity: 10, fuel: 'pmma', fuel_phase: 'solid' }
const FLEX = {
  accession: 'PSI-69', investigationAcronym: 'FLEX', score: 50,
  matches: [{ variable: 'oxygen', scenario: 0.3, tested_min: 0.12, tested_max: 0.34, closest: 0.3, unit: 'mole fraction' },
            { variable: 'pressure', scenario: 0.7, tested_min: 0, tested_max: 3.0525, closest: 0.7, unit: 'atm' }],
  differences: [{ variable: 'fuel_phase', scenario: 'solid', tested: ['liquid'] }, { variable: 'fuel', scenario: 'pmma', tested: ['Heptane', 'Methanol'] }],
  unavailable: ['flow_velocity'],
  best_tests: [{ file: 'PSI-69_Experimental table_FLEX.csv', line: 42, run_id: '41', score: 67,
    values: { oxygen: { column: 'O initial ambient composition; mole fraction', value: 0.3, unit: 'mole fraction' } } }],
}
const TWIN = {   // synthetic, not a PSI investigation
  accession: 'TEST-1', investigationAcronym: '', score: 40,
  matches: [{ variable: 'fuel_phase', scenario: 'solid', tested: ['gas', 'solid'] },
            { variable: 'fuel', scenario: 'pmma', tested: ['Cotton-Fiberglass (SIBAL)', 'PMMA', 'PMMA & Nomex', 'Silicone'] }],
  differences: [{ variable: 'flow_velocity', scenario: 10, tested_min: 20, tested_max: 20, closest: 20, unit: 'cm/s' }],
  unavailable: ['oxygen', 'pressure'], best_tests: [],
}
const RESULT = { scenario: SCENARIO, method: { variables: ['oxygen', 'pressure', 'flow_velocity', 'fuel', 'fuel_phase'] }, items: [FLEX, TWIN] }

test('statuses and counts come from matches, differences and unavailable', () => {
  assert.equal(statusOf(FLEX, 'oxygen'), 'match')
  assert.equal(statusOf(FLEX, 'fuel_phase'), 'differs')
  assert.equal(statusOf(FLEX, 'flow_velocity'), 'missing')
  assert.deepEqual(countsOf(FLEX), { match: 2, differs: 2, missing: 1 })
})

test('axis widens to keep the scenario on it', () => {
  const a = axisFor('oxygen', OPTIONS, 30)
  assert.ok(a.min <= 12 && a.max >= 85)
  assert.ok(axisFor('oxygen', OPTIONS, 100).max >= 100)
  assert.ok(axisFor('flow_velocity', OPTIONS, 200).max >= 200)
})

test('a range lane shows the tested band in display units', () => {
  const lane = laneFor(FLEX, 'oxygen', SCENARIO, axisFor('oxygen', OPTIONS, 30))
  assert.equal(lane.kind, 'range')
  assert.deepEqual(lane.band, [12, 34])
  assert.equal(lane.value, 30)
  assert.equal(lane.status, 'match')
  assert.equal(lane.readout, 'tested 12–34 %, closest 30 %')
  assert.equal(lane.label, 'FLEX')
  assert.equal(lane.unit, 'PSI-69')
  assert.equal(lane.source, '"O initial ambient composition; mole fraction" in PSI-69_Experimental table_FLEX.csv')
  assert.equal(laneFor(FLEX, 'pressure', SCENARIO, axisFor('pressure', OPTIONS, 0.7)).readout, 'tested 0–3.05 atm, closest 0.7 atm')
})

test('a single-value band stays a band and reads as one value', () => {
  const lane = laneFor(TWIN, 'flow_velocity', SCENARIO, axisFor('flow_velocity', OPTIONS, 10))
  assert.deepEqual(lane.band, [20, 20])
  assert.equal(lane.readout, 'tested 20 cm/s, closest 20 cm/s')
  assert.equal(lane.label, 'TEST-1')
})

test('a missing variable is hatched and says so', () => {
  const lane = laneFor(FLEX, 'flow_velocity', SCENARIO, axisFor('flow_velocity', OPTIONS, 10))
  assert.equal(lane.band, null)
  assert.equal(lane.status, 'missing')
  assert.equal(lane.readout, 'Not recorded')
})

test('stops lanes list every tested stop', () => {
  const lane = laneFor(TWIN, 'fuel_phase', SCENARIO)
  assert.equal(lane.kind, 'stops')
  assert.deepEqual(lane.stops, ['gas', 'liquid', 'solid'])
  assert.deepEqual(lane.band, [0, 2])
  assert.equal(lane.value, 2)
})

test('fuel pair lists matching names first, then a count', () => {
  const lane = laneFor(TWIN, 'fuel', SCENARIO)
  assert.equal(lane.kind, 'pair')
  assert.equal(lane.theirs, 'PMMA, PMMA & Nomex, Cotton-Fiberglass (SIBAL) +1 more')
  assert.equal(lane.yours, 'pmma')
})

test('figures follow the method order, rows follow the rank order', () => {
  const figures = figuresFor(RESULT, ['TEST-1', 'PSI-69'], OPTIONS)
  assert.deepEqual(figures.map((f) => f.variable), ['oxygen', 'pressure', 'flow_velocity', 'fuel', 'fuel_phase'])
  assert.equal(figures[0].caption, 'Oxygen, %')
  assert.deepEqual(figures[0].lanes.map((l) => l.unit), ['PSI-69', 'TEST-1'])
})

test('picks ignore unknown accessions and default to the top two', () => {
  assert.deepEqual(parsePicks('PSI-999,TEST-1', RESULT.items), ['TEST-1'])
  assert.deepEqual(parsePicks(null, RESULT.items), ['PSI-69', 'TEST-1'])
  assert.equal(parsePicks('PSI-69,TEST-1,PSI-69', RESULT.items).length, 2)
})
```

- [ ] **Step 2: Run and see them fail.** Expected: FAIL, cannot find `./ComparisonLanes.js`.
- [ ] **Step 3: Implement `ComparisonLanes.js`.** Scale display values with `Number((x * scale).toPrecision(6))` so `0.34 × 100` is `34`. Fuel names matching the scenario fuel (case-insensitive substring) come first; show at most 3 names, then "+N more". `source` uses the first `best_tests` entry that has the variable (`"<column>" in <file>`), else `<accession> experimental table`. Readout for a missing range is `Not recorded`; for stops and pairs, the tested values joined by ", ".
- [ ] **Step 4: Extend `ConditionLanes`** as in Interfaces; Home (`/`) must render exactly as before.
- [ ] **Step 5: Run the tests and the build.** `node --test "frontend/src/pages/*.test.js"` all pass; `npm run build` passes; screenshot `/` at 1440 and compare with the Home figure before the change.
- [ ] **Step 6: Commit** and heartbeat.

### Task 4: Comparison page

**Files:**
- Create: `frontend/src/pages/Comparison.jsx`, `frontend/src/pages/Comparison.css`
- Modify: `frontend/src/main.jsx` (route `comparison`), `frontend/src/pages.js` (comparison `ready: true`)

**Interfaces:**
- Consumes: `hasScenario`, `rankPath`, `paramsToForm`, `PLACES`, `fromAtm` (Task 1); `figuresFor`, `countsOf`, `parsePicks`, `formatValue` (Task 3); `GET /api/rank` and `/api/rank/options` shapes in `backend/README.md`.
- Produces: links `/scenario?<same params>` ("Edit scenario") and `/explorer/<accession>` for each ranked name.

- [ ] **Step 1: Build the page** as the spec's Comparison sketch, in this order: scenario bar (place label, each set value in the entered unit with the converted value, `gravity_note`, `notice` verbatim, "Edit scenario"); weights (a 0–10 step-1 slider per `method.variables`, written to the URL as `weight_<variable>` with `replace` after about 300 ms, `method.weights_reason`, Reset); ranked table (rank, name + accession linking to Explorer, title, score, `close_tests` of `rows_scored` `row_unit`, the three counts with Match/Differs/Not recorded words, a pick checkbox capped at 3 with a reason shown on the disabled fourth, picks in `pick=`); `not_ranked` with each `reason`; one `ConditionLanes` per figure (`theirsLabel` "Tested range", footnote naming each picked investigation's experimental table and DOI link); closest tests per pick (run id, file, line, score, each value with PSI's column name and unit, and "converted from {original.value} {original.unit}" when `calculated`). Keep the previous result on screen while a re-rank loads (a small local hook in this file; `api.js` is not this task's).
- [ ] **Step 2: States.** No scenario (`!hasScenario`) → one line and a link to `/scenario`; the API's `message` when present; `Loading`/`LoadError`; `items: []` → say no investigation could be ranked and list `not_ranked`.
- [ ] **Step 3: Wire the route and slot** (`comparison` in `main.jsx`, `ready: true` in `pages.js`).
- [ ] **Step 4: Verify** with both servers: screenshot at 375 and 1440 `/comparison?place=lunar&environment=lunar&oxygen=0.3&pressure=0.7&p_unit=atm&fuel_phase=solid` (gravity note visible, two picks, figures for oxygen, pressure, fuel phase), `/comparison?oxygen=1&pressure=0.292599&p_unit=psi&place=spacecraft&environment=spacecraft` (spacesuit: ticks stay on the axis), `/comparison` (empty state). Change a weight and confirm the URL and order update without the table blanking.
- [ ] **Step 5: Commit** and heartbeat.

### Task 5: Explorer helpers

**Files:**
- Create: `frontend/src/pages/ExplorerFilters.js`
- Test: `frontend/src/pages/ExplorerFilters.test.js`

**Interfaces:**
- Produces:
  - `FILTERS = [{key: 'platform', label: 'Platform'}, {key: 'fuel_phase', label: 'Fuel phase'}, {key: 'fire_safety_role', label: 'Fire-safety role'}, {key: 'gravity_level', label: 'Gravity'}, {key: 'flare_data', label: 'Data in FLARE'}]`.
  - `tagValues(inv, key) -> string[]` (split on `;`, trimmed, empty dropped; `[]` when the record has no tags).
  - `readFilters(params) -> {[key]: Set<string>}` from repeated keys (`fuel_phase=gas&fuel_phase=solid`).
  - `matchesFilters(inv, selected) -> boolean` (OR within a key, AND across keys).
  - `optionsFor(investigations, key) -> {value, count}[]`, count descending then value.
  - `splitSnippet(snippet: string) -> {text: string, match: boolean}[]`.

- [ ] **Step 1: Write the failing tests**

```js
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { tagValues, readFilters, matchesFilters, optionsFor, splitSnippet } from './ExplorerFilters.js'

const tags = (values) => ({ derived: { tags: { values } } })
const A = { accession: 'A', ...tags({ platform: 'ISS', fuel_phase: 'liquid', gravity_level: 'microgravity' }) }
const B = { accession: 'B', ...tags({ platform: 'computation', fuel_phase: 'gas; liquid', gravity_level: 'microgravity; normal gravity' }) }
const C = { accession: 'C', derived: {} }

test('tag values split on semicolons', () => {
  assert.deepEqual(tagValues(B, 'fuel_phase'), ['gas', 'liquid'])
  assert.deepEqual(tagValues(C, 'fuel_phase'), [])
})

test('filters are OR within a group and AND across groups', () => {
  const sel = readFilters(new URLSearchParams('fuel_phase=gas&fuel_phase=liquid&platform=ISS'))
  assert.deepEqual([...sel.fuel_phase], ['gas', 'liquid'])
  assert.equal(matchesFilters(A, sel), true)
  assert.equal(matchesFilters(B, sel), false)
  assert.equal(matchesFilters(C, sel), false)
  assert.equal(matchesFilters(C, readFilters(new URLSearchParams(''))), true)
})

test('options are counted', () => {
  assert.deepEqual(optionsFor([A, B, C], 'fuel_phase'), [{ value: 'liquid', count: 2 }, { value: 'gas', count: 1 }])
})

test('snippets split into plain and matched text, and broken markers stay text', () => {
  assert.deepEqual(splitSnippet('droplet [[extinction]] (high [[Oxygen]])'), [
    { text: 'droplet ', match: false }, { text: 'extinction', match: true },
    { text: ' (high ', match: false }, { text: 'Oxygen', match: true }, { text: ')', match: false },
  ])
  assert.deepEqual(splitSnippet('open [[ only'), [{ text: 'open [[ only', match: false }])
  assert.deepEqual(splitSnippet('<b>x</b>'), [{ text: '<b>x</b>', match: false }])
})
```

- [ ] **Step 2: Run and see them fail.** Expected: FAIL, cannot find `./ExplorerFilters.js`.
- [ ] **Step 3: Implement `ExplorerFilters.js`.**
- [ ] **Step 4: Run the tests.** Expected: all pass.
- [ ] **Step 5: Commit** and heartbeat.

### Task 6: Explorer list page

**Files:**
- Create: `frontend/src/pages/Explorer.jsx`, `frontend/src/pages/Explorer.css`
- Modify: `frontend/src/main.jsx` (route `explorer`), `frontend/src/pages.js` (explorer `ready: true`)

**Interfaces:**
- Consumes: Task 5 exports; `byAccession`, `nameOf`, `formatNumber` from `catalogue.js`; `useApi('/investigations')`.
- Produces: links `/explorer/<accession>`; renders `<ExplorerSearch />` (Task 7) above the list once Task 7 lands (leave its place marked by the section heading until then).

- [ ] **Step 1: Build the page:** filter groups from `FILTERS` with `optionsFor` counts (toggle buttons with `aria-pressed`, state in repeated URL keys, a Clear control), "Showing N of 24", and the table from the spec (acronym + accession in Fira Code, title, platform, fuel phase, gravity, data in FLARE, `derived.file_count` files), sorted by `byAccession`, stacked records below 720px. Zero matches → say so with Clear.
- [ ] **Step 2: Wire the route and slot.**
- [ ] **Step 3: Verify:** build passes; screenshots at 375 and 1440 of `/explorer` and `/explorer?fuel_phase=solid&platform=ISS`; the count matches a manual count from `/api/investigations`.
- [ ] **Step 4: Commit** and heartbeat.

### Task 7: Document search

**Files:**
- Create: `frontend/src/pages/ExplorerSearch.jsx` (styles in `Explorer.css`)
- Modify: `frontend/src/pages/Explorer.jsx` (render it)

**Interfaces:**
- Consumes: `splitSnippet` (Task 5); `GET /api/search?q=&accession=&limit=10&offset=` → `{query, total, limit, offset, items}`.
- Produces: `export default function ExplorerSearch({ accession })`; the query lives in the URL as `q`.

- [ ] **Step 1: Build it:** a labelled search form (submit on Enter or button); results with `splitSnippet` parts rendered as text and `<mark>` (no `dangerouslySetInnerHTML`), the investigation name linking to `/explorer/<accession>`, file name in Fira Code, page ("page 3"; nothing for Word), and "Open file" linking to `/api/files/<file_id>/download` with a note that it takes a moment; "{total} passages" and "Show more" appending the next 10. A 503 says "Document search is not available: the search index has not been built."; a 422 is ignored (empty query); other errors use `LoadError`.
- [ ] **Step 2: Verify:** build passes; `/explorer?q=extinction%20oxygen` at 375 and 1440 shows highlighted passages; "Show more" grows the list; an "Open file" link answers 307 (`curl -sI http://127.0.0.1:8000/api/files/<file_id>/download`).
- [ ] **Step 3: Commit** and heartbeat.

### Task 8: One investigation's page

**Files:**
- Create: `frontend/src/pages/ExplorerInvestigation.jsx` (styles in `Explorer.css`)
- Modify: `frontend/src/main.jsx` (route `explorer/:accession`)

**Interfaces:**
- Consumes: `GET /api/investigations/{accession}` (fetched directly with `fetch` so a 404 can be told apart), `GET /api/files?accession=&kind=&limit=100&offset=`, `ExplorerSearch` (Task 7) with `accession`, `tagValues`/`FILTERS` (Task 5).

- [ ] **Step 1: Build it** per the spec's "One investigation": header (title, acronym, accession, DOI and PSI page links, dates, licence, hardware, platform); PSI's objective, hypothesis, approach and research impacts under "From the PSI record"; tags with the field each cites (`derived.tags.sources`); experimental tables from `derived.experimental_tables`; files with a kind filter (counts from `derived.files_by_kind`, a JSON object of `{kind: {files, bytes}}`), 100 per page with Previous/Next, each linking to its download; publications (title, `authorList`, DOI link when non-empty, status); contacts (name, roles, affiliation); `ExplorerSearch accession`; "Compare against a scenario" to `/scenario`. Unknown accession → a not-found message linking back to `/explorer`.
- [ ] **Step 2: Verify:** build passes; screenshots at 375 and 1440 of `/explorer/PSI-69` (6,453 files across kinds; publications listed) and `/explorer/PSI-60` (empty acronym, catalogue only), and `/explorer/PSI-0` shows not found.
- [ ] **Step 3: Commit** and heartbeat.

### Task 9: Whole-task check and records

**Files:**
- Modify: `docs/DECISIONS.md` (one line), `docs/ai-use/gheathwahab.md` (one row)

- [ ] **Step 1: Run everything:** `node --test "frontend/src/pages/*.test.js"` all pass; `npm run build` passes; screenshots of every changed page at 375 and 1440 reviewed together for `DESIGN.md` consistency.
- [ ] **Step 2: Run `break-ui`** on Comparison with three picks, long fuel lists, the "DAFT / DAFT-2" acronym and every lane hatched; fix what breaks, re-run the tests and build.
- [ ] **Step 3: Record:** in `docs/DECISIONS.md`, `- 2026-11-14 @gheathwahab: /comparison reads its scenario from the URL with /api/rank's own parameter names plus place, p_unit (psi, kPa, atm) and pick (up to 3 accessions), and each investigation's page is /explorer/{accession}, so any page can link to a ranking or a record (#13)`; a row in `docs/ai-use/gheathwahab.md` following its README. Ask the human to tell #12's owner that `/api/rank/options` and the ranked `tested` fuel lists carry parsing noise ("pre test flow visulation data for sample", "c2h5").
- [ ] **Step 4: Commit**, heartbeat, run the `usage-aware` checkpoint, and suggest `/team-sync` then `/team-pr`.
