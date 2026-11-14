# Test report

What was checked, how, and what it printed. Every result here was run on 14 November 2026 against
`main` at `812d87c` (after #48) and against the live site https://flare-sandy.vercel.app. Outputs
are copied from those runs, not from PR descriptions. A check that has not been run says so.

This file was started from the merged PRs (#38). The whole-app QA (#29) and the final assembly
(#30) add the pages and checks still missing. Page-by-page QA notes are in `qa_results.md`.

Status words: **Pass** (run, behaved as required), **Partly** (passes where it can be run; the
rest is named), **Fail** (run, did not behave as required), **Not run yet**.

## Test suites

Run on Windows 11, Python 3.15.2 and Node 26.13.1. The deployed backend runs Python 3.12 on
Vercel; the live checks below are what exercise that version.

| Suite | Command | Result | Added by |
|---|---|---|---|
| Backend API | `cd backend && python -m unittest discover -s tests -v` | `Ran 93 tests in 1.883s OK` | #11, #20, #24, #31, #41, #44, #45 |
| Pipeline | `python -m unittest discover -s pipeline/tests -v` (needs `pipeline/requirements.txt`) | `Ran 60 tests in 85.415s OK` | #6, #21, #22, #24, #45 |
| Run analysis | `python -m unittest discover -s research/analysis` | `Ran 5 tests in 0.048s OK` | #32 |
| Coordinator | `cd coordinator && python -m pytest` | `14 passed in 1.10s` | #34 |
| Frontend build | `cd frontend && npm ci && npm run build` | `✓ built in 798ms` | #23, #41, #42 |

The frontend has no automated tests; its pages are checked by hand (`qa_results.md`). The run
analysis tests compare the CSV files and `summary.md`, not the charts, so they ran without
matplotlib.

## Concrete checks (master prompt, section 8)

| # | Check | Status | Evidence | Output |
|---|---|---|---|---|
| 1 | The pipeline loads 129 BASS-II runs and 274 FLEX tests, and a test fails if a count changes | **Pass** | `test_bass2_table_and_test_matrix_are_one_test_each`, `test_row_counts_match_the_data_plan`, `test_committed_files_match_a_fresh_build` (pipeline); `test_concrete_checks_from_the_master_prompt` (backend); live `/api/runs/rows?accession=PSI-25` and `PSI-69` | Each count is written into a test, so a change fails it. Live: `total 129` and `total 274`. All tables: 2,009 rows |
| 2 | A FLEX pressure such as 757.7 mmHg is still shown as 757.7 mmHg, with its conversion marked as calculated | **Partly** | `test_flex_pressure_in_mmhg_is_converted_and_marked` (pipeline); `test_concrete_checks_from_the_master_prompt`, `test_calculated_pressure_keeps_original` (backend); live `/api/runs/rows?accession=PSI-69&limit=1` | Live: `raw 757.7`, `standard {value 0.9969736842, unit atm, calculated True, original {value 757.7, unit mmHg}}`. On screen: not run yet, because no built page shows run rows (Explorer and Visualization, #13 and #35) |
| 3 | A scenario with every field empty returns an explained result, not an error and not a ranking built on invented values | **Partly** | `test_empty_scenario_is_explained_not_ranked`, which also covers a Mars-only scenario and a zero-weight scenario; `test_empty_scenario_is_200_with_message`; live `/api/rank` | Live: `'Set at least one condition to rank.' items 0 not_ranked 24`, HTTP 200. On screen: not run yet (Scenario page, #13) |
| 4 | A lunar scenario shows the microgravity notice on every result | **Partly** | `test_lunar_scenario_notes_microgravity_on_every_result`; live `/api/rank?environment=lunar&oxygen=0.21` | Live: `18 items, 18 with the note`: "This scenario is at 0.17 g. NASA's evidence comes from microgravity and normal-gravity tests, not partial gravity." On screen: not run yet (#13) |
| 5 | Changing one scenario value changes the scores of the runs it should affect, and the explanation names that value | **Pass** (API) | `test_changing_oxygen_changes_only_rows_with_oxygen`: a FLEX row's score changes and a SPICE row without oxygen does not; live `/api/rank?oxygen=…&fuel=methanol` | Live, FLEX (PSI-69): `o2=0.21 score 100 [0.21]`, then `o2=0.40 score 84 [0.4]`; the oxygen entry names the new value |
| 6 | A question the sources cannot answer gets "not found", with no invented result | **Partly** | `test_nothing_found`, `test_scoped_question_with_no_matching_passage_says_so`, `test_refusal_falls_back_to_sources`, `test_api_failure_falls_back_to_sources`; live `POST /api/assistant/ask` | Live: `{"mode":"retrieval_only","reason":"No NASA source in FLARE matches this question.","blocks":[],"sources":[]}`. Not run yet: a live model call (no `ANTHROPIC_API_KEY` yet), so whether Claude answers "not found" when sources exist but don't answer is untested. The tests use a fake model client |
| 7 | Every page works at 375px and survives `break-ui` | **Fail** (so far) | #48 (`qa_results.md`): Home and Sources at 320, 375 and 1440px with worst-case data | Home and Sources break at 200% text and with worst-case data; Sources cuts titles at 375px. Fixes are #46 and #47. Assistant: phone layout reviewed in #41's finish review, but on a test fixture, and no `break-ui` run is recorded. Methodology: not run yet. Explorer, Scenario, Comparison and Visualization are not built yet |
| 8 | The deployed URL passes the same page checks as the local build | **Partly** | The checks in `docs/DEPLOY.md`, plus every route and API above | Pass: all 8 routes `200 text/html`, `/favicon.svg 200 image/svg+xml`, `/api/nope 404 application/json`, `/api/health {"status":"ok","investigations":24,"files":60866,"retrieved":"2026-11-14"}`, ranking, search (`total 2145` for "extinction", so SQLite FTS5 works on Vercel), runs and assistant. Fail: `/api/flex-model 404` (the live site predates #45; needs a redeploy). A route's 200 shows only that the app shell is served; rendering is checked only for Home and Sources (#48) |

## Source links (section 8, "Do source links open?")

**Fail** today, for most files, locally and live alike.

`GET /api/files/{file_id}/download` was tried on 2 files from each of 5 investigations:

| Investigation | Result |
|---|---|
| PSI-25 (BASS-II), PSI-69 (FLEX), PSI-107 (SPICE), PSI-26 | `502 PSI answered with something other than a psi-repo-prod.s3.amazonaws.com link` |
| PSI-159 | `307` to `psi-repo-prod.s3.amazonaws.com` |

PSI does answer. It now gives these files links on its other bucket, `psi-curation-prod`, which
the route refuses (#20). That link works: a one-byte request for
`PSI-25_Engineering Documents_BASS-II_Engineering Requirements.pptx` returned
`206, bytes 0-0/1123356`, matching the catalogue's size. `docs/DEPLOY.md` reads a 502 as "PSI is
not answering", which is not the cause here. When #20 merged, its live run fetched the BASS table
byte for byte, so PSI's answer has changed since.

## Checks each merged PR ran

What each PR says it checked, and whether that was run again for this report.

| PR | Area | Checks in the PR | Run again here |
|---|---|---|---|
| #11 | Catalogue API | 12 tests against counts read from the data files | Yes, in the backend suite (`test_catalogue_api`, 12) |
| #20 | File download link | 5 tests with faked PSI answers; one live run fetched the 4,726-byte BASS table byte for byte | Tests pass (`test_downloads`, 5). The live fetch now fails; see "Source links" |
| #21 | Experimental tables | 17 tests on real rows | Yes (`test_process_tables`, 17) |
| #22 | Investigation tags | `test_tags`; the PR notes backend tests were not run on its author's machine | Yes, both suites pass (`test_tags`, 4) |
| #23 | Design system, Home, Sources | Impeccable finish review ("ship"); `break-ui` not done | The build passes; `break-ui`-style QA was done in #48 |
| #24 | Document search | 17 pipeline and 8 backend tests; FTS5 on Vercel unchecked | Yes; FTS5 now checked live (`total 2145`) |
| #31 | Ranking | 27 new tests (52 backend tests at the time) | Yes (`test_ranking` 18, `test_ranking_api` 6, `test_runs` 3) |
| #32 | Run analysis | 5 tests, one fails if the committed output goes stale | Yes, 5 pass |
| #34 | Coordinator | 14 tests | Yes, 14 pass |
| #41 | AI assistant | 23 tests with a fake model client; live model call untested (no key) | Yes (`test_assistant_api`, 23); live retrieval-only answer checked (check 6) |
| #42 | Methodology page | Numbers traced to repo files by hand; no tests listed | The build passes; the page is not checked at 375px yet |
| #43 | Vercel deploy | The curl checks in `docs/DEPLOY.md` | Yes; see check 8 |
| #44 | Runs API | 10 endpoint checks (85 backend tests at the time) | Yes (`test_runs_api`, 10) |
| #45 | FLEX outcome model | A test reruns training and requires the committed results to match exactly | Yes, it matches (`test_committed_results_are_what_this_code_produces`); 7 FLEX model tests plus 8 API tests |
| #48 | QA of Home and Sources | `qa_results.md` | Not run again; its findings are #46 and #47 |

## Open problems these checks found

- Most file downloads return 502 because the route refuses PSI's `psi-curation-prod` links (#20's
  area). PSI's links themselves work.
- The live site has no `/api/flex-model` yet; it needs a redeploy after #45.
- Home and Sources break at 200% text and with worst-case data (#46, #47).
- The assistant has never made a live model call; the key has not arrived.
- Unflagged suspect values are still scored by the ranking, such as FLEX test 114 at 0 mmHg and
  the negative SPICE air rates (#32, `research/analysis/suspect_values.csv`).

**AI use:** this report was put together with Claude Code (Claude Opus 5.5) and reviewed by the
team. Every output in it comes from a command run on 14 November 2026; none was written by the
model.
