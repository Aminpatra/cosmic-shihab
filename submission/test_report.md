# Test report

What was checked, how, and what it printed. Every result here was run on 14 November 2026
against `main` at `cd9dbcc` (after #51) and against the live site https://flare-sandy.vercel.app.
Outputs are copied from those runs, not from PR descriptions. A check that has not been run says
so.

This file was started from the merged PRs (#38). The whole-app QA (#29) and the final assembly
(#30) add the pages and checks still missing. Page-by-page QA notes are in `qa_results.md`.

Status words: **Pass** (run, behaved as required), **Partly** (passes where it can be run; the
rest is named), **Fail** (run, did not behave as required), **Not run yet**.

"On screen" means the page was rendered from a local build (Vite dev server plus the backend on
port 8000) in headless Microsoft Edge at 1440px, and the rendered text was read.

## Test suites

Run on Windows 11, Python 3.15.2 and Node 26.13.1. The deployed backend runs Python 3.12 on
Vercel; the live checks below are what exercise that version.

| Suite | Command | Result | Added by |
|---|---|---|---|
| Backend API | `cd backend && python -m unittest discover -s tests -v` | `Ran 93 tests in 8.625s OK` | #11, #20, #24, #31, #41, #44, #45 |
| Pipeline | `python -m unittest discover -s pipeline/tests -v` (needs `pipeline/requirements.txt`) | `Ran 60 tests in 342.750s OK` | #6, #21, #22, #24, #45 |
| Run analysis | `python -m unittest discover -s research/analysis` | `Ran 5 tests in 0.046s OK` | #32 |
| Coordinator | `cd coordinator && python -m pytest` | `14 passed in 0.86s` | #34 |
| Frontend helpers | `node --test "frontend/src/pages/*.test.js"` | `tests 22, pass 22, fail 0` | #49 |
| Frontend build | `cd frontend && npm ci && npm run build` | `✓ built in 966ms` | #23, #41, #42, #49, #50, #51 |

- The pages themselves have no automated tests; they are checked by hand (`qa_results.md`).
- The run-analysis tests compare the CSV files and `summary.md`, not the charts, so they ran
  without matplotlib.
- The FLEX model's reproducibility test only passes on Python 3.15.2. The stored results record the
  Python version and the test compares that too, so it fails on any other version even though the
  model's numbers match (found by #51). A fix follows #38.

## Concrete checks (master prompt, section 8)

### 1. The pipeline loads 129 BASS-II runs and 274 FLEX tests, and a test fails if a count changes: **Pass**

- Tests: `test_bass2_table_and_test_matrix_are_one_test_each`, `test_row_counts_match_the_data_plan`
  and `test_committed_files_match_a_fresh_build` (pipeline); `test_concrete_checks_from_the_master_prompt`
  (backend). Each count is written into a test, so a change fails it.
- Live: `/api/runs/rows?accession=PSI-25` gives `total 129`, `PSI-69` gives `total 274`. All
  tables together hold 2,009 rows.

### 2. A FLEX pressure such as 757.7 mmHg is still shown as 757.7 mmHg, with its conversion marked as calculated: **Pass**

- Tests: `test_flex_pressure_in_mmhg_is_converted_and_marked` (pipeline);
  `test_concrete_checks_from_the_master_prompt` and `test_calculated_pressure_keeps_original` (backend).
- Live API: `raw 757.7`, `standard {value 0.9969736842, unit atm, calculated True, original {value 757.7, unit mmHg}}`.
- On screen: `/comparison?oxygen=0.21&pressure=0.9969736842&pick=PSI-69`, under "Closest tests",
  shows FLEX run 1 as `Ambient pressure; mmHg 757.7 mmHg (0.997 atm, converted by FLARE)`.

### 3. A scenario with every field empty returns an explained result, not an error and not a ranking built on invented values: **Pass**

- Tests: `test_empty_scenario_is_explained_not_ranked` (also a Mars-only and a zero-weight
  scenario) and `test_empty_scenario_is_200_with_message`.
- Live API `/api/rank`: HTTP 200, `'Set at least one condition to rank.' items 0 not_ranked 24`.
- On screen: `/comparison` with no scenario shows "No scenario yet. The comparison ranks NASA's
  tests against the conditions you set, and only those." and a "Set a scenario" link. No error
  and no ranking.

### 4. A lunar scenario shows the microgravity notice on every result: **Partly**

- Test: `test_lunar_scenario_notes_microgravity_on_every_result`.
- Live API `/api/rank?environment=lunar&oxygen=0.21`: `18 items, 18 with the note`.
- On screen: `/comparison?environment=lunar&place=lunar&oxygen=0.21` shows "This scenario is at
  0.17 g. NASA's evidence comes from microgravity and normal-gravity tests, not partial gravity."
  **once, above the 18 ranked results**, not on each result. The team should decide whether
  that meets "on every result".
- A link with `place=lunar` but no `environment` says "Environment: Lunar habitat" but ranks at
  0 g with no notice. The Scenario page always writes both, so only a link made by hand or by
  another page hits this.

### 5. Changing one scenario value changes the scores of the runs it should affect, and the explanation names that value: **Pass**

- Test: `test_changing_oxygen_changes_only_rows_with_oxygen`: a FLEX row's score changes, a SPICE
  row without oxygen does not, and FLEX's explanation names the new value.
- Live API `/api/rank?oxygen=…&fuel=methanol`, FLEX (PSI-69): `o2=0.21 score 100 [0.21]`, then
  `o2=0.40 score 84 [0.4]`.
- On screen, the same two scenarios: "Oxygen 21 %" gives FLEX "2 match 0 differs … 130 of 274
  tests close to your scenario, Relevance score 100"; "Oxygen 40 %" gives "1 match 1 differs … 5
  of 274 tests close to your scenario, Relevance score 84".

### 6. A question the sources cannot answer gets "not found", with no invented result: **Partly**

- Tests: `test_nothing_found`, `test_scoped_question_with_no_matching_passage_says_so`,
  `test_refusal_falls_back_to_sources` and `test_api_failure_falls_back_to_sources`.
- Live API `POST /api/assistant/ask`:
  `{"mode":"retrieval_only","reason":"No NASA source in FLARE matches this question.","blocks":[],"sources":[]}`.
- Not run yet:
  - a live model call (no `ANTHROPIC_API_KEY` yet), so whether Claude says "not found" when
    sources exist but don't answer is untested; the tests use a fake model client;
  - the Assistant page's own rendering of this answer.

### 7. Every page works at 375px, and survives `break-ui`: **Fail** (so far)

- Home and Sources: #48 checked them at 320, 375 and 1440px with worst-case data (`qa_results.md`).
  - The empty and changing data it found (#47) was fixed by #50, which says it was checked in
    Edge at 375 and 1440px; that check was not run again here.
  - The layout breaks (#46) are still open: 200% text breaks the nav, and Sources cuts titles at
    375px.
- Assistant: #41's finish review looked at a phone layout, on a test fixture; no `break-ui` run
  is recorded.
- Explorer, Scenario, Comparison, Visualization and Methodology: not run yet at 375px or with
  worst-case data (#29).

### 8. The deployed URL passes the same page checks as the local build: **Fail** (today)

- The live site runs a build from before #45 and #49:
  - Scenario, Comparison and Visualization still show "in progress";
  - `/api/flex-model` answers `404`.
  - It needs a redeploy (`docs/DEPLOY.md`).
- What the live site has passes the checks in `docs/DEPLOY.md`:
  - all 8 routes return `200 text/html`;
  - `/favicon.svg` returns `200 image/svg+xml`;
  - `/api/nope` returns `404 application/json`;
  - `/api/health` returns `{"status":"ok","investigations":24,"files":60866,"retrieved":"2026-11-14"}`;
  - ranking, runs and the assistant answer;
  - search returns `total 2145` for "extinction", so SQLite FTS5 works on Vercel.
- A route's 200 shows only that the app shell is served; rendering is checked live only for Home
  and Sources (#48).

## Source links (section 8, "Do source links open?"): **Fail** today, for most files

`GET /api/files/{file_id}/download` was tried on 2 files from each of 5 investigations, locally
and live:

| Investigation | Result |
|---|---|
| PSI-25 (BASS-II), PSI-69 (FLEX), PSI-107 (SPICE), PSI-26 | `502 PSI answered with something other than a psi-repo-prod.s3.amazonaws.com link` |
| PSI-159 | `307` to `psi-repo-prod.s3.amazonaws.com` |

- PSI does answer. It now gives these files links on its other bucket, `psi-curation-prod`, which
  the route refuses (#20).
- That link works: a one-byte request for
  `PSI-25_Engineering Documents_BASS-II_Engineering Requirements.pptx` returned
  `206, bytes 0-0/1123356`, matching the catalogue's size.
- `docs/DEPLOY.md` reads a 502 as "PSI is not answering", which is not the cause here, and #49's
  guess ("PSI unreachable?") has the same cause.
- When #20 merged, its live run fetched the BASS table byte for byte, so PSI's answer has changed
  since.

## Checks each merged PR ran

What each PR says it checked, and whether that was run again for this report.

| PR | Area | Checks in the PR | Run again here |
|---|---|---|---|
| #11 | Catalogue API | 12 tests against counts read from the data files | Yes, in the backend suite (`test_catalogue_api`, 12) |
| #20 | File download link | 5 tests with faked PSI answers; one live run fetched the 4,726-byte BASS table byte for byte | Tests pass (`test_downloads`, 5). The live fetch now fails; see "Source links" |
| #21 | Experimental tables | 17 tests on real rows | Yes (`test_process_tables`, 17) |
| #22 | Investigation tags | `test_tags`; the PR notes backend tests were not run on its author's machine | Yes, both suites pass (`test_tags`, 4) |
| #23 | Design system, Home, Sources | Impeccable finish review ("ship"); `break-ui` not done | The build passes; worst-case QA was done in #48 |
| #24 | Document search | 17 pipeline and 8 backend tests; FTS5 on Vercel unchecked | Yes; FTS5 now checked live (`total 2145`) |
| #31 | Ranking | 27 new tests (52 backend tests at the time) | Yes (`test_ranking` 18, `test_ranking_api` 6, `test_runs` 3) |
| #32 | Run analysis | 5 tests, one fails if the committed output goes stale | Yes, 5 pass |
| #34 | Coordinator | 14 tests | Yes, 14 pass |
| #41 | AI assistant | 23 tests with a fake model client; live model call untested (no key) | Yes (`test_assistant_api`, 23); the live retrieval-only answer was checked (check 6) |
| #42 | Methodology page | Numbers traced to repo files by hand; no tests listed | The build passes; not checked at 375px yet |
| #43 | Vercel deploy | The curl checks in `docs/DEPLOY.md` | Yes; see check 8 |
| #44 | Runs API | 10 endpoint checks (85 backend tests at the time) | Yes (`test_runs_api`, 10) |
| #45 | FLEX outcome model | A test reruns training and requires the committed results to match exactly | Yes on Python 3.15.2 (`test_committed_results_are_what_this_code_produces`), plus 6 FLEX data tests and 8 API tests. It fails on other Python versions; see "Test suites" |
| #48 | QA of Home and Sources | `qa_results.md` | Not run again; its findings are #46 (open) and #47 (fixed by #50) |
| #49 | Explorer, Scenario, Comparison | 22 helper tests | Yes, 22 pass; checks 2 to 5 were rendered on its Comparison page |
| #50 | Empty and changing data on Home and Sources | Edge at 375 and 1440px with the API's answer swapped (real, empty, one, no link or DOI, 500, offline); build and 22 tests | The build and tests pass; the Edge check was not run again |
| #51 | Visualization page | Every drawn count matches `summary.md`; colours checked with the dataviz validator; Impeccable finish review | The build passes; the page was not checked by hand here |

## Open problems these checks found

- Most file downloads return 502 because the route refuses PSI's `psi-curation-prod` links (#20's
  area). PSI's links themselves work.
- The live site needs a redeploy: it lacks #45's `/api/flex-model` and the pages from #49, #50 and #51.
- Home and Sources still break at 200% text and in places at 375px (#46).
- The lunar notice is shown once above the ranked list rather than on each result (check 4). That
  needs a team decision.
- The FLEX reproducibility test fails on any Python other than 3.15.2.
- The assistant has never made a live model call; the key has not arrived.
- #50 reports, not rerun here, that the Assistant, Scenario, Comparison and Explorer pages don't
  yet tell an API error apart from no answer, and that the Assistant still says "Loading the 24
  investigations…".
- Unflagged suspect values are still scored by the ranking, such as FLEX test 114 at 0 mmHg and
  the negative SPICE air rates (#32, `research/analysis/suspect_values.csv`).

**AI use:** this report was put together with Claude Code (Claude Opus 5.5) and reviewed by the
team. Every output in it comes from a command run on 14 November 2026; none was written by the
model.
