# Ranking Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rank NASA PSI investigations against a user's fire scenario by scoring each test row, with an explanation for every result, served at `GET /api/rank`.

**Architecture:** A read-only loader for `backend/data/runs/`, a pure scoring module (closeness per variable, weighted row score, roll-up to investigations, explanation), and one FastAPI router with two endpoints. Investigation tags come from `derived.tags.values` in the catalogue records (DECISIONS.md, @saminre).

**Tech Stack:** Python 3.12–3.14, FastAPI 0.162.7, standard library only; tests with `unittest` and FastAPI's `TestClient`.

**Spec:** `docs/superpowers/specs/2026-11-14-ranking-engine-design.md`

## Global Constraints

- Backend code runs on Python 3.12 to 3.14; no new runtime dependency (`backend/pyproject.toml` stays FastAPI only).
- Everything read at run time lives in `backend/` and is opened read-only.
- Every route starts with `/api`; the router lives in `backend/app/routes/ranking.py` and is included in `backend/main.py`.
- Nothing is filled in by FLARE: an unset scenario field stays unset; `environment` sets gravity only (`spacecraft` 0, `lunar` 0.17 g, `mars` 0.38 g).
- Every response carries `notice` = `"A relevance score shows how closely NASA's tests match this scenario. It is not a safety assessment."`
- A set variable that a row lacks scores 0 and is never skipped.
- Run tests from `backend/`: `.venv/Scripts/python -m unittest discover -s tests -v` (macOS/Linux: `.venv/bin/python`).

## Review Focus

1. Fuel typed as a formula, in another case or with punctuation (`c2h4`, ` Ethylene`, `n-heptane`, `PMMA film`) should still match the rows PSI wrote as `C2H4`, `Heptane`, material `PMMA`. Test in Task 2.
2. All weights of the set variables at 0 should give the empty-scenario message, not a division by zero. Test in Task 3.
3. Scenario values outside every tested range (oxygen 1.0, pressure 0, flow 500) should score 0, never below, and appear under `differences`. Test in Task 3.
4. A fuel no test used (`kerosene`) should score 0 for fuel and still rank on the other variables, without an error. Test in Task 3.
5. `gravity_g` with an environment other than `custom` should be refused (422) rather than silently ignored; `custom` without `gravity_g` gives no gravity note. Test in Task 4.

---

### Task 1: Load the runs files

**Files:**
- Create: `backend/app/runs.py`
- Test: `backend/tests/test_runs.py`

**Interfaces:**
- Produces: `runs() -> dict[str, dict]`, accession to the parsed `runs/<ACCESSION>.json` (`{"accession", "tables": [...]}`), cached with `functools.cache`, in accession-number order like `catalogue.investigations()`. `DATA_DIR` reused from `app.catalogue`.

- [ ] **Step 1: Write the failing tests** in `backend/tests/test_runs.py`, counting from the files directly (as `test_catalogue_api.py` does):

```python
def test_loads_every_table_and_row(self):
    data = runs.runs()
    self.assertEqual(len(data), 20)
    self.assertEqual(sum(len(t["tables"]) for t in data.values()), 22)
    self.assertEqual(sum(len(tb["rows"]) for t in data.values() for tb in t["tables"]), 2009)

def test_known_counts(self):  # brief, section "Concrete checks"
    self.assertEqual(len(runs.runs()["PSI-69"]["tables"][0]["rows"]), 274)
    self.assertEqual(len(runs.runs()["PSI-25"]["tables"][0]["rows"]), 129)

def test_flex_pressure_keeps_psi_value(self):
    p = runs.runs()["PSI-69"]["tables"][0]["rows"][0]["standard"]["pressure"]
    self.assertTrue(p["calculated"])
    self.assertEqual(p["original"], {"value": 757.7, "unit": "mmHg"})
```

- [ ] **Step 2: Run** `.venv/Scripts/python -m unittest tests.test_runs -v`. Expected: ImportError for `app.runs`.
- [ ] **Step 3: Implement `runs()`** in `backend/app/runs.py`; raise `ValueError` if a file's `accession` differs from its name.
- [ ] **Step 4: Run** the same command. Expected: 3 tests OK.
- [ ] **Step 5: Commit** `backend/app/runs.py backend/tests/test_runs.py`: "Load PSI's processed test tables for the ranking (#7)".

### Task 2: Score one test row

**Files:**
- Create: `backend/app/ranking.py`
- Test: `backend/tests/test_ranking.py` (class `RowScoring`)

**Interfaces:**
- Consumes: `runs.runs()`; `catalogue.investigations()[acc]["derived"]["tags"]["values"]` with keys `fuel_phase`, `fire_safety_role`, `gravity_level` (several values joined by `"; "`; `"not stated"` means none).
- Produces:
  - `NUMERIC = ("oxygen", "pressure", "flow_velocity")`, `UNITS = {"oxygen": "mole fraction", "pressure": "atm", "flow_velocity": "cm/s"}`, `VARIABLES = NUMERIC + ("fuel", "fuel_phase", "concern")`
  - `DEFAULT_WEIGHTS: dict[str, float]` (every variable 1.0) and `WEIGHTS_REASON: str` ("Equal weights: FLARE claims no variable matters more for fire safety. Override per request.")
  - `CLOSE = 0.8`, `GRAVITY = {"spacecraft": 0.0, "lunar": 0.17, "mars": 0.38}`
  - `@dataclass(frozen=True) class Scenario`: `environment: str | None = None`, `gravity_g: float | None = None`, `oxygen`, `pressure`, `flow_velocity: float | None = None`, `fuel`, `fuel_phase`, `concern: str | None = None`, `weights: dict[str, float] = field(default_factory=dict)`; methods `set_variables() -> list[str]` (in `VARIABLES` order, unset and zero-weight excluded), `weight(variable) -> float`, `gravity() -> float | None`.
  - `scorable_value(row: dict, variable: str) -> float | None`: the standard field's `value` when it is a single number and the cell `row["cells"][standard["column"]]` has no `flags`; else `None`.
  - `tolerances() -> dict[str, float]`: per numeric variable, (max − min) / 4 over all scorable values, cached.
  - `normalize_fuel(text: str) -> str`: lowercase, every non-alphanumeric run becomes one space, formula tokens become names (`c2h4` ethylene, `ch4` methane, `c2h6` ethane, `c3h8` propane, `c3h6` propylene, `c4h10` butane, `c7h16` heptane, `c12h26` dodecane, `ch3oh` methanol, `c2h5oh` ethanol).
  - `closeness(scenario_value: float, row_value: float, tolerance: float) -> float`: `max(0.0, 1 - abs(row_value - scenario_value) / tolerance)`.
  - `fuel_matches(scenario_fuel: str, row_fuel: dict) -> bool`: every word longer than one character of `normalize_fuel(scenario_fuel)` is among the words of `normalize_fuel` of the row fuel's `material` list and `text` joined by spaces. (`set_variables()` treats a fuel with no such word as unset.)
  - `score_row(scenario: Scenario, row: dict, tags: dict) -> tuple[float, dict[str, float | None]]`: weighted mean over `set_variables()`, with `None` (unavailable) counted as 0; returns the score and the per-variable values. Fuel: 1.0 / 0.0 from `fuel_matches`, `None` when the row has no fuel. `fuel_phase` and `concern`: 1.0 / 0.0 from the tag, `None` when the tag is `"not stated"`.

- [ ] **Step 1: Write the failing tests** (class `RowScoring`), using real rows: `flex1 = runs.runs()["PSI-69"]["tables"][0]["rows"][0]` (O2 0.21, methanol, no flow).

```python
def test_tolerances_come_from_the_data(self):
    t = ranking.tolerances()
    self.assertAlmostEqual(t["oxygen"], 0.1825, places=4)
    self.assertAlmostEqual(t["pressure"], 1.25, places=4)
    self.assertAlmostEqual(t["flow_velocity"], 22.8, places=4)

def test_closeness_falls_linearly_to_zero(self):
    self.assertEqual(ranking.closeness(0.21, 0.21, 0.2), 1.0)
    self.assertAlmostEqual(ranking.closeness(0.21, 0.31, 0.2), 0.5)
    self.assertEqual(ranking.closeness(0.21, 0.90, 0.2), 0.0)

def test_fuel_names_match_formulas_case_and_punctuation(self):  # Review Focus 1
    for typed in ["c2h4", " Ethylene", "ETHYLENE"]:
        self.assertEqual(ranking.normalize_fuel(typed), "ethylene")
        self.assertTrue(ranking.fuel_matches(typed, c2h4_row["standard"]["fuel"]))
    self.assertTrue(ranking.fuel_matches("n-heptane", heptane_row["standard"]["fuel"]))
    self.assertTrue(ranking.fuel_matches("PMMA film", pmma_row["standard"]["fuel"]))

def test_missing_variable_counts_as_zero_not_skipped(self):
    score, parts = ranking.score_row(ranking.Scenario(oxygen=0.21, flow_velocity=20), flex1, flex_tags)
    self.assertEqual(parts, {"oxygen": 1.0, "flow_velocity": None})
    self.assertAlmostEqual(score, 0.5)

def test_fuel_scores_from_material_list_and_formula_text(self):
    self.assertEqual(ranking.score_row(ranking.Scenario(fuel="PMMA"), pmma_row, bass2_tags)[1]["fuel"], 1.0)
    self.assertEqual(ranking.score_row(ranking.Scenario(fuel="Kapton"), pmma_row, bass2_tags)[1]["fuel"], 0.0)
    self.assertEqual(ranking.score_row(ranking.Scenario(fuel="ethylene"), c2h4_row, psi10_tags)[1]["fuel"], 1.0)

def test_phase_and_concern_come_from_tags(self):  # FLEX: liquid, suppression; PSI-10: role "not stated"
    parts = ranking.score_row(ranking.Scenario(fuel_phase="liquid", concern="suppression"), flex1, flex_tags)[1]
    self.assertEqual(parts, {"fuel_phase": 1.0, "concern": 1.0})
    parts = ranking.score_row(ranking.Scenario(fuel_phase="liquid", concern="suppression"), c2h4_row, psi10_tags)[1]
    self.assertEqual(parts, {"fuel_phase": 0.0, "concern": None})

def test_flagged_value_is_unavailable(self):  # PSI-20 oxygen "3400%", flag percent_over_100
    self.assertIsNone(ranking.scorable_value(psi20_flagged_row, "oxygen"))

def test_zero_weight_drops_the_variable(self):
    s = ranking.Scenario(oxygen=0.21, flow_velocity=20, weights={"flow_velocity": 0})
    self.assertEqual(s.set_variables(), ["oxygen"])
```

In `setUpClass`, take each `*_tags` as `catalogue.investigations()[acc]["derived"]["tags"]["values"]` (`flex_tags` PSI-69, `bass2_tags` PSI-25, `psi10_tags` PSI-10, `spice_tags` PSI-107), and find rows by searching the loaded data: `pmma_row`, the first PSI-25 row whose fuel text contains "PMMA film"; `c2h4_row`, the first PSI-10 row with fuel text "C2H4"; `heptane_row`, the first row anywhere with fuel text "Heptane"; `psi20_flagged_row`, the PSI-20 row whose oxygen cell has `percent_over_100`. Fail the test class loudly if any is not found.

- [ ] **Step 2: Run** `.venv/Scripts/python -m unittest tests.test_ranking -v`. Expected: ImportError for `app.ranking`.
- [ ] **Step 3: Implement** the names above in `backend/app/ranking.py`.
- [ ] **Step 4: Run** the same command. Expected: 8 tests OK.
- [ ] **Step 5: Commit** `backend/app/ranking.py backend/tests/test_ranking.py`: "Score one PSI test against a scenario, counting gaps as no evidence (#7)".

### Task 3: Rank investigations and explain each result

**Files:**
- Modify: `backend/app/ranking.py`
- Test: `backend/tests/test_ranking.py` (class `Ranking`)

**Interfaces:**
- Consumes: Task 2's names.
- Produces: `rank(scenario: Scenario) -> dict` with keys `items`, `not_ranked`, `message` (`None`, or `"Set at least one condition to rank."` when `set_variables()` is empty), `gravity_note` (scenario level), `method` (`{"variables": [...], "weights": {...}, "weights_reason", "tolerances": {...}, "close": 0.8, "version": "1"}`), `notice`.
  - Item: `accession`, `title`, `investigationAcronym`, `doi`, `score` (best row × 100, rounded to int), `close_tests` (rows ≥ `CLOSE`), `rows_scored`, `row_unit` (the table's `row_is`), `used_variables` ({variable: weight}), `matches`, `differences` (each `{"variable", "scenario", "tested_min", "tested_max", "closest", "unit"}`; numbers only carry min/max/closest), `unavailable` (set variables with no scorable value in any row of the investigation, or a `"not stated"` tag), `best_tests` (up to 3: `{"file", "line", "run_id", "score", "values"}` where `values` copies each set variable's standard entry), `measured_outcomes` (standard fields with role `outcome` present in any row), `gravity_note`.
  - A set variable available in the investigation is a match when the best test's part is ≥ `CLOSE`, else a difference.
  - `not_ranked` item: `accession`, `title`, `investigationAcronym`, `doi`, `reason`. Data-driven: no runs file, "No experimental table: catalogue only"; every row `row_is == "published_figure"`, "An index of published figures, not tests"; no row with any scorable condition or fuel, "No test conditions recorded". On an empty scenario every other investigation is added with reason `message`.
  - Order: score descending, then `close_tests` descending, then accession number.
  - `gravity_note` (scenario and every item) when `scenario.gravity()` > 0: `f"This scenario is at {g} g. The evidence comes from {gravity_level} tests, not partial gravity."`, using the investigation's tag (scenario level: "NASA's evidence comes from microgravity and normal-gravity tests, not partial gravity."). `None` otherwise.

- [ ] **Step 1: Write the failing tests** (class `Ranking`):

```python
def test_flex_ranks_first_for_its_own_conditions(self):
    out = ranking.rank(ranking.Scenario(oxygen=0.21, pressure=1.0, fuel="methanol"))
    top = out["items"][0]
    self.assertEqual(top["accession"], "PSI-69")
    self.assertGreaterEqual(top["score"], 99)
    self.assertEqual({m["variable"] for m in top["matches"]}, {"oxygen", "pressure", "fuel"})
    self.assertEqual(top["best_tests"][0]["file"], "PSI-69_Experimental table_FLEX.csv")

def test_changing_oxygen_changes_only_rows_with_oxygen(self):
    a, b = ranking.Scenario(oxygen=0.21, fuel="methanol"), ranking.Scenario(oxygen=0.40, fuel="methanol")
    self.assertNotEqual(ranking.score_row(a, flex1, flex_tags), ranking.score_row(b, flex1, flex_tags))
    self.assertEqual(ranking.score_row(a, spice_row, spice_tags), ranking.score_row(b, spice_row, spice_tags))
    flex = next(i for i in ranking.rank(b)["items"] if i["accession"] == "PSI-69")
    self.assertIn(0.40, [d["scenario"] for d in flex["matches"] + flex["differences"] if d["variable"] == "oxygen"])

def test_missing_information_is_named(self):
    items = {i["accession"]: i for i in ranking.rank(ranking.Scenario(oxygen=0.21, flow_velocity=20))["items"]}
    self.assertIn("flow_velocity", items["PSI-69"]["unavailable"])
    self.assertIn("oxygen", items["PSI-107"]["unavailable"])

def test_lunar_scenario_notes_microgravity_on_every_result(self):
    out = ranking.rank(ranking.Scenario(environment="lunar", oxygen=0.21))
    self.assertTrue(out["items"])
    self.assertTrue(all("not partial gravity" in i["gravity_note"] for i in out["items"]))
    self.assertTrue(all(i["gravity_note"] is None for i in ranking.rank(ranking.Scenario(environment="spacecraft", oxygen=0.21))["items"]))

def test_empty_scenario_is_explained_not_ranked(self):
    for s in [ranking.Scenario(), ranking.Scenario(environment="mars"),
              ranking.Scenario(oxygen=0.21, weights={"oxygen": 0})]:   # Review Focus 2
        out = ranking.rank(s)
        self.assertEqual((out["items"], out["message"]), ([], "Set at least one condition to rank."))
        self.assertEqual(len(out["not_ranked"]), 24)
    self.assertIsNotNone(ranking.rank(ranking.Scenario(environment="mars"))["gravity_note"])

def test_structural_not_ranked_set(self):
    out = ranking.rank(ranking.Scenario(oxygen=0.21))
    self.assertEqual({n["accession"] for n in out["not_ranked"]},
                     {"PSI-47", "PSI-60", "PSI-62", "PSI-115", "PSI-117", "PSI-142"})
    self.assertEqual(len(out["items"]) + len(out["not_ranked"]), 24)

def test_out_of_range_values_score_zero_as_differences(self):  # Review Focus 3
    for s in [ranking.Scenario(oxygen=1.0), ranking.Scenario(pressure=0.0, flow_velocity=500)]:
        for i in ranking.rank(s)["items"]:
            self.assertGreaterEqual(i["score"], 0)
    flex = next(i for i in ranking.rank(ranking.Scenario(oxygen=1.0))["items"] if i["accession"] == "PSI-69")
    self.assertEqual([d["variable"] for d in flex["differences"]], ["oxygen"])

def test_unknown_fuel_scores_zero_and_still_ranks(self):  # Review Focus 4
    out = ranking.rank(ranking.Scenario(oxygen=0.21, fuel="kerosene"))
    self.assertTrue(out["items"])
    self.assertTrue(all(i["score"] <= 50 for i in out["items"]))

def test_zero_weight_equals_leaving_the_variable_out(self):
    with_zero = ranking.rank(ranking.Scenario(oxygen=0.21, flow_velocity=20, weights={"flow_velocity": 0}))
    without = ranking.rank(ranking.Scenario(oxygen=0.21))
    self.assertEqual([(i["accession"], i["score"]) for i in with_zero["items"]],
                     [(i["accession"], i["score"]) for i in without["items"]])

def test_calculated_pressure_keeps_original(self):
    flex = next(i for i in ranking.rank(ranking.Scenario(pressure=1.0))["items"] if i["accession"] == "PSI-69")
    p = flex["best_tests"][0]["values"]["pressure"]
    self.assertTrue(p["calculated"])
    self.assertEqual(p["original"]["unit"], "mmHg")
```

`spice_row` is the first PSI-107 row (flow, no oxygen).

- [ ] **Step 2: Run** `.venv/Scripts/python -m unittest tests.test_ranking -v`. Expected: the 10 new tests fail with `AttributeError: ... has no attribute 'rank'`; Task 2's 8 still pass.
- [ ] **Step 3: Implement `rank()`** and its helpers in `backend/app/ranking.py`. Score every row of every table once per call (2,009 rows; no caching across scenarios).
- [ ] **Step 4: Run** the same command. Expected: 18 tests OK. Then time `ranking.rank(Scenario(oxygen=0.21, pressure=1, fuel="methanol"))`; expected well under 1 s.
- [ ] **Step 5: Commit** `backend/app/ranking.py backend/tests/test_ranking.py`: "Rank investigations by their closest tests and explain every result (#7)".

### Task 4: Serve the ranking

**Files:**
- Create: `backend/app/routes/ranking.py`
- Modify: `backend/main.py` (import and `app.include_router(ranking.router)`), `backend/README.md` (two endpoint rows, one layout row each for `app/runs.py` and `app/ranking.py`), `docs/DECISIONS.md` (one line, below), `docs/ai-use/Aminpatra.md` (one row)
- Test: `backend/tests/test_ranking_api.py`

**Interfaces:**
- Consumes: `ranking.Scenario`, `ranking.rank`, `ranking.tolerances`, `ranking.UNITS`, `ranking.GRAVITY`, `runs.runs()`.
- Produces:
  - `GET /api/rank`: query `environment: Literal["spacecraft","lunar","mars","custom"] | None`, `gravity_g` (0 to 1; 422 unless `environment == "custom"`), `oxygen` (0 to 1), `pressure` (0 to 10), `flow_velocity` (0 to 1000), `fuel` (max 100 chars), `fuel_phase: Literal["gas","liquid","solid"]`, `concern: Literal["prevention","detection","suppression"]`, `weight_<variable>` for each of `VARIABLES` (0 to 10). Returns `rank()`'s dict plus `scenario` (only the parameters given).
  - `GET /api/rank/options`: `{"variables": {var: {"unit", "min", "max", "rows"}}, "fuels": [{"name", "rows"}], "fuel_phases", "concerns", "environments": {name: gravity}}`; fuels are `normalize_fuel` of each row's materials and, when there are none, its text, counted by row, most rows first.
  - DECISIONS line: `- 2026-11-14 @Aminpatra: the ranking is GET /api/rank (scenario as query parameters, weights as weight_<variable>) returning {scenario, method, notice, message, gravity_note, items, not_ranked}, and GET /api/rank/options gives the Scenario page its real ranges and fuels; shapes in backend/README.md (#7)`

- [ ] **Step 1: Write the failing tests** in `backend/tests/test_ranking_api.py`:

```python
def test_rank_answers_with_notice_method_and_echo(self):
    body = client.get("/api/rank", params={"oxygen": 0.21, "fuel": "methanol"}).json()
    self.assertEqual(body["notice"], "A relevance score shows how closely NASA's tests match this scenario. It is not a safety assessment.")
    self.assertEqual(body["scenario"], {"oxygen": 0.21, "fuel": "methanol"})
    self.assertEqual(body["items"][0]["accession"], "PSI-69")
    self.assertIn("tolerances", body["method"])

def test_empty_scenario_is_200_with_message(self):
    body = client.get("/api/rank").json()
    self.assertEqual((body["items"], body["message"]), ([], "Set at least one condition to rank."))

def test_weights_come_from_query(self):
    a = client.get("/api/rank", params={"oxygen": 0.21, "flow_velocity": 20, "weight_flow_velocity": 0}).json()
    b = client.get("/api/rank", params={"oxygen": 0.21}).json()
    self.assertEqual([i["score"] for i in a["items"]], [i["score"] for i in b["items"]])

def test_out_of_range_inputs_are_422(self):
    for params in [{"oxygen": 1.5}, {"pressure": -1}, {"flow_velocity": -3}, {"weight_oxygen": -1},
                   {"environment": "venus"}, {"environment": "lunar", "gravity_g": 0.5}]:  # Review Focus 5
        self.assertEqual(client.get("/api/rank", params=params).status_code, 422, params)

def test_custom_gravity(self):
    self.assertIsNone(client.get("/api/rank", params={"environment": "custom", "oxygen": 0.21}).json()["gravity_note"])
    self.assertIn("0.5 g", client.get("/api/rank", params={"environment": "custom", "gravity_g": 0.5, "oxygen": 0.21}).json()["gravity_note"])

def test_options_come_from_the_data(self):
    body = client.get("/api/rank/options").json()
    self.assertEqual(body["variables"]["oxygen"], {"unit": "mole fraction", "min": 0.12, "max": 0.85, "rows": 1147})
    names = [f["name"] for f in body["fuels"]]
    self.assertIn("pmma", names); self.assertIn("ethylene", names)
    self.assertEqual(body["environments"], {"spacecraft": 0.0, "lunar": 0.17, "mars": 0.38})
```

- [ ] **Step 2: Run** `.venv/Scripts/python -m unittest tests.test_ranking_api -v`. Expected: 404s / failures (no route).
- [ ] **Step 3: Implement** the router, register it, and write the README rows, DECISIONS line and AI-use row.
- [ ] **Step 4: Run the whole suite** `.venv/Scripts/python -m unittest discover -s tests -v`. Expected: all tests OK (25 existing + 3 + 18 + 6 = 52).
- [ ] **Step 5: Commit** all files above: "Serve the ranking at /api/rank with its options for the Scenario page (#7)".
