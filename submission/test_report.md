# Test report

What was checked, how, and what it printed. Every result here was run on 15 November 2026 (UTC+4)
against `main` at `9f86da2` (after #68) and against the live site, https://cosmic-shihab.vercel.app
(the team's site since #66). Outputs are copied from those runs, not from PR descriptions. A check
that has not been run says so.

The report was started from the merged PRs in #38 (runs of 14 November against `299dba6`). #30
reran every check for this version and added the PRs merged since. The whole-app QA (#29) is still
running; its page-by-page notes go in `qa_results.md`, and its summary is added here when it merges.

Status words: **Pass** (run, behaved as required), **Partly** (passes where it can be run; the
rest is named), **Fail** (run, did not behave as required), **Not run yet**.

"On screen" means the page was rendered in headless Microsoft Edge, driven through its DevTools
protocol, at 1440px unless a width is given, and the rendered text was read. The page checks below
ran on the live site. The #39 pages were also rendered from a local build while #39 was made (#67).

## Test suites

Run on Windows 11, Python 3.15.2 and Node 26.13.1, on `9f86da2`. The deployed backend runs Python
3.12 on Vercel; the live checks below are what exercise that version.

| Suite | Command | Result | Added by |
|---|---|---|---|
| Backend API | `cd backend && python -m unittest discover -s tests -v` | `Ran 103 tests in 1.509s OK` | #11, #20, #24, #31, #41, #44, #45, #55 |
| Pipeline | `python -m unittest discover -s pipeline/tests -v` (needs `pipeline/requirements.txt`) | `Ran 60 tests in 57.544s OK` | #6, #21, #22, #24, #45 |
| Run analysis | `python -m unittest discover -s research/analysis` | `Ran 5 tests in 0.031s OK` | #32 |
| Coordinator | `cd coordinator && python -m pytest` | `14 passed in 0.45s` | #34 |
| Frontend helpers | `node --test "frontend/src/pages/*.test.js"` | `tests 27, pass 27, fail 0` | #49, #67 |
| Frontend build | `cd frontend && npm ci && npm run build` | `✓ built in 486ms` | #23, #41, #42, #49 to #54, #60, #64, #67 |

- The pages themselves have no automated tests apart from their helpers; they are checked in the
  browser (here and in `qa_results.md`).
- The run-analysis tests compare the CSV files and `summary.md`, not the charts, so they ran
  without matplotlib.
- The FLEX model's reproducibility test used to fail on any Python but 3.15.2: the stored results
  record the Python version and the test compared that too, although the model's numbers matched
  (found by #51). #61 fixed it: the test now leaves the recorded Python version out. Run as if on
  Python 3.12.9 (`platform.python_version` replaced), the fixed test printed `Ran 1 test in
  246.907s OK` (14 November). It still skips when the scikit-learn version differs.

## Concrete checks (master prompt, section 8)

### 1. The pipeline loads 129 BASS-II runs and 274 FLEX tests, and a test fails if a count changes: **Pass**

- Tests: `test_bass2_table_and_test_matrix_are_one_test_each`, `test_row_counts_match_the_data_plan`
  and `test_committed_files_match_a_fresh_build` (pipeline); `test_concrete_checks_from_the_master_prompt`
  (backend). Each count is written into a test, so a change fails it.
- Live: `/api/runs/rows?accession=PSI-25` gives `total 129`, `PSI-69` gives `total 274`, and all
  tables together give `total 2009`.

### 2. A FLEX pressure such as 757.7 mmHg is still shown as 757.7 mmHg, with its conversion marked as calculated: **Pass**

- Tests: `test_flex_pressure_in_mmhg_is_converted_and_marked` (pipeline);
  `test_concrete_checks_from_the_master_prompt` and `test_calculated_pressure_keeps_original` (backend).
- On screen: `/comparison?oxygen=0.21&pressure=0.9969736842&pick=PSI-69`, under "Closest tests",
  shows FLEX run 1 as `757.7 mmHg (0.997 atm, converted by FLARE)`.

### 3. A scenario with every field empty returns an explained result, not an error and not a ranking built on invented values: **Pass**

- Tests: `test_empty_scenario_is_explained_not_ranked` (also a Mars-only and a zero-weight
  scenario) and `test_empty_scenario_is_200_with_message`.
- Live API `/api/rank`: HTTP 200, `'Set at least one condition to rank.' items 0 not_ranked 24`.
- On screen: `/comparison` with no scenario shows "No scenario yet. The comparison ranks NASA's
  tests against the conditions you set, and only those.", a "Set a scenario" link and, since #67,
  links to the three scenarios the challenge page gives values for ("Moon base or pressurized rover
  30 % oxygen, 10.2 psi", "Earth sea-level air 21 % oxygen, 14.7 psi", "Spacesuit atmosphere 100 %
  oxygen, 4.3 psi"). No error and no ranking.

### 4. A lunar scenario shows the microgravity notice on every result: **Partly**

- Test: `test_lunar_scenario_notes_microgravity_on_every_result`.
- Live API `/api/rank?environment=lunar&oxygen=0.21`: 18 items, and each of the 18 carries its own
  `gravity_note` (two wordings, such as "This scenario is at 0.17 g. The evidence comes from
  microgravity tests, not partial gravity.").
- On screen: `/comparison?environment=lunar&place=lunar&oxygen=0.21` shows "This scenario is at
  0.17 g. NASA's evidence comes from microgravity and normal-gravity tests, not partial gravity."
  **once, above the 18 ranked results**, not on each result. The team should decide whether that
  meets "on every result".
- A link with `place=lunar` but no `environment` says "Environment: Lunar habitat" but ranks at
  0 g with no notice (found in #38). The Scenario page always writes both, so only a link made by
  hand or by another page hits this.

### 5. Changing one scenario value changes the scores of the runs it should affect, and the explanation names that value: **Pass**

- Test: `test_changing_oxygen_changes_only_rows_with_oxygen`: a FLEX row's score changes, a SPICE
  row without oxygen does not, and FLEX's explanation names the new value.
- Live API `/api/rank?oxygen=…&fuel=methanol`, FLEX (PSI-69): score `100` at oxygen 0.21, `84` at 0.40.
- On screen, the same two scenarios: oxygen 21 % gives FLEX "2 match 0 differs 0 not recorded 130
  of 274 tests close to your scenario Relevance score 100"; oxygen 40 % gives "1 match 1 differs 0
  not recorded 5 of 274 tests close to your scenario Relevance score 84".

### 6. A question the sources cannot answer gets "not found", with no invented result: **Pass** (on the questions tried)

- Tests: `test_nothing_found`, `test_scoped_question_with_no_matching_passage_says_so`,
  `test_refusal_falls_back_to_sources` and `test_api_failure_falls_back_to_sources`. These use a
  fake model client.
- On screen, the live Assistant page (`/api/assistant/status`: `{"mode": "generated", "model":
  "claude-opus-5-5"}`):
  - "zzzqx vbnmw" shows "No NASA source in FLARE matches this question." with no answer text and
    no sources.
  - "What droplet burning rate did FLEX measure at lunar gravity?" (not scoped) shows an answer
    "AI-generated by claude-opus-5-5 from the 9 sources below" that begins "The documents don't
    give any FLEX droplet burning rate at lunar gravity, and nothing in them indicates that FLEX
    tested at lunar gravity at all.", with 9 citations to 9 sources. Only its first 400
    characters were read in this run; #38's run of the same question (scoped to PSI-69, through
    the API) read the whole answer and found no number in it.
  - For comparison, the example "Which gases did FLEX test as fire suppressants?" gets a cited
    answer ("carbon dioxide, helium and sulfur hexafluoride", 10 citations, 9 sources).
- Two questions are a small sample.
- The citation numbers in an answer don't move the page; see "Open problems".

### 7. Every page works at 375px, and survives `break-ui`: **Partly**

- At 375px, on the live site, every page is exactly as wide as the screen
  (`document.documentElement.scrollWidth` 375 on a 375px viewport, so no sideways scrolling): `/`,
  `/explorer`, `/explorer/PSI-69`, `/scenario`, `/comparison` with and without the Moon base
  scenario, `/visualization`, `/assistant`, `/methodology` and `/sources`. This measures overflow
  only; nobody looked at these pages by eye for this report.
- `break-ui` with worst-case data:
  - Home and Sources: #48 found breaks at 320, 375 and 1440px (`qa_results.md`). #50 fixed the
    data problems (#47) and #54 the layout problems (#46); neither check was run again here.
  - Every other page: not run yet. It is part of #29.

### 8. The deployed URL passes the same page checks as the local build: **Pass** on https://cosmic-shihab.vercel.app

- `docs/DEPLOY.md` and `docs/DECISIONS.md` now name cosmic-shihab.vercel.app (#68). #38 found that
  the site they named before, flare-sandy.vercel.app, served an older build.
- On cosmic-shihab.vercel.app:
  - All 8 routes return `200 text/html`; `/favicon.svg` returns `200 image/svg+xml`; `/api/nope`
    returns `404 application/json`; `/api/health` returns `{"status": "ok", "investigations": 24,
    "files": 60866, "retrieved": "2026-11-14"}`.
  - Checks 1 to 6 give the outputs above. The test suites ran on `9f86da2`; the site serves a build
    that includes #60, #64 and #67 (their text is in its JavaScript bundle). The site does not say
    which commit it serves.
  - `/api/flex-model` returns 200, and the Visualization page shows its notice ("not a prediction
    of a real fire") and the held-out macro-F1 chart.
  - Search returns `total 2145` for "extinction", so SQLite FTS5 works on Vercel.
- flare-sandy.vercel.app still answers with the older build: `/api/assistant/summaries/PSI-69`,
  `/api/assistant/readings` and `/api/flex-model` return 404, and its pages lack #67.

## Stored AI summaries and readings (#28, #39): **Pass**

- Live API: all 24 summaries (`/api/assistant/summaries/{accession}`) and the 3 readings
  (`/api/assistant/readings`) are `reviewed: true`, `reviewed_by: "Aminpatra"` (#63). Each reading
  is `current: true`, so the live ranking still has the order it explains.
- On screen, `/explorer/PSI-69` leads its text column with the summary: "AI-generated by
  claude-opus-5-5 on 14 November 2026, from the 9 sources listed under it." and "Reviewed by
  @Aminpatra, who checked it against those sources.", with 10 citation links.
- On screen, the Moon base scenario link (`/comparison?environment=lunar&oxygen=0.3&pressure=0.69407114&place=lunar&p_unit=psi`)
  shows "Reading of this ranking" above a ranking whose top five score 100, 94, 87, 73 and 29, the
  scores the reading states. With `&weight_oxygen=2` added, the reading is not shown.
- Locally on #67's build: an unreviewed file shows "Not reviewed yet", an investigation with no
  file shows nothing in its place, and a citation click opens its source.

## Source links (section 8, "Do source links open?"): **Fail**, for most files

`GET /api/files/{file_id}/download` on the live site, for the first file of 5 investigations:

| Investigation | Result |
|---|---|
| PSI-25 (BASS-II), PSI-69 (FLEX), PSI-107 (SPICE), PSI-26 | `502 PSI answered with something other than a psi-repo-prod.s3.amazonaws.com link: 'https://psi-curation-prod.s3.amazonaws.com/…'` |
| PSI-159 | `307` to `psi-repo-prod.s3.amazonaws.com` |

- PSI does answer. It now gives these files links on its other bucket, `psi-curation-prod`, which
  the route refuses (#20).
- That link works: in #38's run, a one-byte request for
  `PSI-25_Engineering Documents_BASS-II_Engineering Requirements.pptx` returned
  `206, bytes 0-0/1123356`, matching the catalogue's size.
- `docs/DEPLOY.md` reads a 502 as "PSI is not answering", which is not the cause here.
- When #20 merged, its live run fetched the BASS table byte for byte, so PSI's answer has changed
  since.

## Whole-app QA (#29): **Not run yet**

#29 is in progress (@saminre). Its page-by-page results go in `qa_results.md`, and their summary
is added here when it merges.

## Checks each merged PR ran

What each PR says it checked, and whether that was run again for this report.

| PR | Area | Checks in the PR | Run again here |
|---|---|---|---|
| #11 | Catalogue API | 12 tests against counts read from the data files | Yes, in the backend suite (`test_catalogue_api`, 12) |
| #20 | File download link | 5 tests with faked PSI answers; one live run fetched the 4,726-byte BASS table byte for byte | Tests pass (`test_downloads`, 5). The live fetch now fails; see "Source links" |
| #21 | Experimental tables | 17 tests on real rows | Yes (`test_process_tables`, 17) |
| #22 | Investigation tags | `test_tags`; the PR notes backend tests were not run on its author's machine | Yes, both suites pass (`test_tags`, 4) |
| #23 | Design system, Home, Sources | Impeccable finish review ("ship"); `break-ui` not done | The build passes; worst-case QA was done in #48 |
| #24 | Document search | 17 pipeline and 8 backend tests; FTS5 on Vercel unchecked | Yes; FTS5 checked live (`total 2145`) |
| #31 | Ranking | 27 new tests (52 backend tests at the time) | Yes (`test_ranking` 18, `test_ranking_api` 6, `test_runs` 3) |
| #32 | Run analysis | 5 tests, one fails if the committed output goes stale | Yes, 5 pass |
| #34 | Coordinator | 14 tests | Yes, 14 pass |
| #41 | AI assistant | 23 tests with a fake model client; live model call untested (no key) | Yes (`test_assistant_api`); the live page was asked three questions (check 6) |
| #42 | Methodology page | Numbers traced to repo files by hand; no tests listed | The build passes; no sideways scroll at 375px |
| #43 | Vercel deploy | The curl checks in `docs/DEPLOY.md` | Yes, on cosmic-shihab.vercel.app; see check 8 |
| #44 | Runs API | 10 endpoint checks (85 backend tests at the time) | Yes (`test_runs_api`, 10) |
| #45 | FLEX outcome model | A test reruns training and requires the committed results to match exactly | Yes (`test_committed_results_are_what_this_code_produces`), plus 6 FLEX data tests and 8 API tests |
| #48 | QA of Home and Sources | `qa_results.md` | Not run again; its findings #46 and #47 were fixed by #54 and #50 |
| #49 | Explorer, Scenario, Comparison | 22 helper tests | Yes, they pass; checks 2 to 5 were rendered on its Comparison page |
| #50 | Empty and changing data on Home and Sources | Edge at 375 and 1440px with the API's answer swapped (real, empty, one, no link or DOI, 500, offline); build and 22 tests | The build and tests pass; the Edge check was not run again |
| #51 | Visualization page | Every drawn count matches `summary.md`; colours checked with the dataviz validator; Impeccable finish review | The build passes; no sideways scroll at 375px; not looked at by eye here |
| #52 | Submission drafts | Numbers recounted from committed files; 24 DOIs and 20 row counts matched | Not run again |
| #53 | FLEX model panel | Every number read from `results.json`; Impeccable finish review | Rendered live: the notice and the held-out macro-F1 chart appear |
| #54 | Layout fixes on Home and Sources | 200% text, 1440, 375 and 320px; tests and build | The build and tests pass; no sideways scroll at 375px; the rest was not run again |
| #55 | Summary and reading generator, `/api/assistant/readings` | 103 backend tests | Yes, 103 pass (`test_readings` included) |
| #57 | Pitch opening | 46 browser checks on the HTML file, plus an offline run | Not run again |
| #58 | Stored summaries and readings | Every citation quoted word for word, every number in a cited sentence found in its source, no Markdown, 211 to 279 words | Not run again; #63 reviewed all 27 files |
| #60 | Flame and gravity visuals on Methodology and Scenario | 1440, 1000 and 375px with live data; build and 22 tests | Their text ("Illustration made with AI", "Gravity tested") is in the live bundle; both pages have no sideways scroll at 375px; not looked at by eye here |
| #61 | This report's start (#38) and the FLEX test fix | Every suite and check, run on `299dba6` | Yes, all of it, on `9f86da2` |
| #63 | Summaries and readings signed as reviewed (#28) | The README's five checks on all 27 files; 103 backend tests | Yes: live, all 24 summaries and 3 readings are `reviewed: true` |
| #64 | The team's own logos | Sources at 1440 and 375px | The live bundle uses `cosmic-shihab-logo-white`; `Logo.jpg` is no longer in the repo; Sources has no sideways scroll at 375px |
| #67 | AI summaries on Explorer and Comparison (#39) | 27 frontend tests; Edge at 1440 and 375px (citation clicks, unreviewed and missing files, a weight hiding the reading) | Yes, live; see "Stored AI summaries and readings" |
| #68 | Docs name cosmic-shihab.vercel.app; QR code | `docs/DEPLOY.md`'s checks against the new URL | Yes; see check 8. The QR code was not decoded again |

## Open problems these checks found

- **Most file downloads return 502**, because the route refuses PSI's `psi-curation-prod` links
  (#20's area). PSI's links themselves work.
- **The Assistant's citation numbers don't move the page.** On the live site, clicking citation 1
  sets the address to `#src-1` but leaves the page at the top, with the source 1,697px below.
  React Router's `<ScrollRestoration>` gives a `#hash` link the same history key as the page and
  puts the scroll back. #67 avoids this in the summary block by scrolling to the source itself; the
  Assistant (#41's area) needs the same.
- **flare-sandy.vercel.app still serves the older build.** The docs no longer name it (#68), but
  anyone with the old link gets a build from before #45 (its `/api/flex-model` returns 404).
  `docs/DEPLOY.md`'s redeploy command still deploys to that project (#68's note).
- **The lunar notice is shown once above the ranked list,** not on each result (check 4). That
  needs a team decision.
- **Most pages say the API "did not answer" even when it answered with an error.** Checked in the
  code on `9f86da2`: 8 `<LoadError>` calls don't pass `error={…}` as #47's decision asks, in
  Assistant, Comparison, Explorer, the investigation page (2 calls), document search, Scenario and
  Visualization. The Assistant still says "Loading the 24 investigations…" with a fixed number.
- **Unflagged suspect values are still scored by the ranking,** such as FLEX test 114 at 0 mmHg and
  the negative SPICE air rates (#32, `research/analysis/suspect_values.csv`). Not rerun here.

**AI use:** this report was put together with Claude Code (Claude Opus 5.5) and reviewed by the
team. Every output in it comes from a command or page run on 14 or 15 November 2026; none was
written by the model.
