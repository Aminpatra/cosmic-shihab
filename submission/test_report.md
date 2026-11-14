# Test report

What was checked, how, and what it printed. Every result here was run on 15 November 2026 (UTC+4)
against `main` at `25b8889` (after #78) and against the live site, https://cosmic-shihab.vercel.app
(the team's site since #66), which serves that version's pages and download fix. Outputs are copied
from those runs, not from PR descriptions. A check that has not been run says so.

The report was started from the merged PRs in #38 (runs of 14 November against `299dba6`). #30
reran every check for this version, added the PRs merged since, and folds in the whole-app QA
(#29), whose page-by-page notes are in `qa_results.md`.

Status words: **Pass** (run, behaved as required), **Partly** (passes where it can be run; the
rest is named), **Fail** (run, did not behave as required), **Not run yet**.

"On screen" means the page was rendered in headless Microsoft Edge, driven through its DevTools
protocol, at 1440px unless a width is given, and the rendered text was read. The page checks below
ran on the live site. #29's QA used Google Chrome through playwright-core; its results are marked
as #29's.

## Test suites

Run on Windows 11, Python 3.15.2 and Node 26.13.1, on `25b8889`. The deployed backend runs Python
3.12 on Vercel; the live checks below are what exercise that version.

| Suite | Command | Result | Added by |
|---|---|---|---|
| Backend API | `cd backend && python -m unittest discover -s tests -v` | `Ran 105 tests in 2.366s OK` | #11, #20, #24, #31, #41, #44, #45, #55, #78 |
| Pipeline | `python -m unittest discover -s pipeline/tests -v` (needs `pipeline/requirements.txt`) | `Ran 60 tests in 84.550s OK` | #6, #21, #22, #24, #45 |
| Run analysis | `python -m unittest discover -s research/analysis` | `Ran 5 tests in 0.037s OK` | #32 |
| Coordinator | `cd coordinator && python -m pytest` | `14 passed in 0.84s` | #34 |
| Frontend helpers | `node --test "frontend/src/pages/*.test.js"` | `tests 27, pass 27, fail 0` | #49, #67 |
| Frontend build | `cd frontend && npm ci && npm run build` | `✓ built in 868ms` | #23, #41, #42, #49 to #54, #60, #64, #67, #69, #74 to #77 |

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
  tests against the conditions you set, and only those.", a "Set a scenario" link and links to the
  three scenarios the challenge page gives values for ("Moon base or pressurized rover 30 % oxygen,
  10.2 psi", "Earth sea-level air 21 % oxygen, 14.7 psi", "Spacesuit atmosphere 100 % oxygen, 4.3
  psi"). No error and no ranking.

### 4. A lunar scenario shows the microgravity notice on every result: **Pass**

- Test: `test_lunar_scenario_notes_microgravity_on_every_result`.
- Live API `/api/rank?environment=lunar&oxygen=0.21`: 18 items, and each of the 18 carries its own
  `gravity_note` (two wordings, such as "This scenario is at 0.17 g. The evidence comes from
  microgravity tests, not partial gravity.").
- On screen: `/comparison?environment=lunar&place=lunar&oxygen=0.21` shows "This scenario is at
  0.17 g. NASA's evidence comes from microgravity and normal-gravity tests, not partial gravity."
  above the list, and with "Show all 18 ranked" pressed, **18 of 18 results** carry their own note
  (#75). #38 and #29 had found it shown once only.
- A link with `place=lunar` but no `environment` says "Environment: Lunar habitat" but ranks at
  0 g with no notice (found in #38, not rerun). The Scenario page always writes both, so only a
  link made by hand or by another page hits this.

### 5. Changing one scenario value changes the scores of the runs it should affect, and the explanation names that value: **Pass**

- Test: `test_changing_oxygen_changes_only_rows_with_oxygen`: a FLEX row's score changes, a SPICE
  row without oxygen does not, and FLEX's explanation names the new value.
- Live API `/api/rank?oxygen=…&fuel=methanol`, FLEX (PSI-69): score `100` at oxygen 0.21, `84` at 0.40.
- On screen, the same two scenarios: oxygen 21 % gives FLEX "2 match 0 differs 0 not recorded 130
  of 274 tests close to your scenario Relevance score 100"; oxygen 40 % gives "1 match 1 differs 0
  not recorded 5 of 274 tests close to your scenario Relevance score 84".
- #29 ran oxygen 0.21 against 0.30: BASS-II, SAFFIRE-I and -II and CFI drop from 100
  to between 51 and 57; FLEX, ACME and CFI-G, which tested both values, stay at 100; all 18 results
  name oxygen.

### 6. A question the sources cannot answer gets "not found", with no invented result: **Pass** (on the questions tried)

- Tests: `test_nothing_found`, `test_scoped_question_with_no_matching_passage_says_so`,
  `test_refusal_falls_back_to_sources` and `test_api_failure_falls_back_to_sources`. These use a
  fake model client.
- On screen, the live Assistant page (`/api/assistant/status`: `{"mode": "generated", "model":
  "claude-opus-5-5"}`), run on `9f86da2`'s deploy; the Assistant's code has changed since only in
  its CSS (#74):
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
- #29 asked a plausible but unanswerable question, "the astronaut who ran FLEX test 114": "The
  documents provided don't name the astronaut…", with every claim cited.
- Three questions are a small sample.
- The citation numbers in an answer don't move the page; see "Open problems".

### 7. Every page works at 375px, and survives `break-ui`: **Pass**

- #29 loaded eleven routes at 320, 375, 720 and 1440px and with the browser's text size at 200%,
  with the API answering 500 and with the network cut, then swapped `break-ui` data in at the API
  boundary at 320, 375 and 1440px (see "Whole-app QA" below). Its findings 13 to 17 are fixed.
- Rerun here on the live site: at 320px and at 375px, all eleven routes are exactly as wide as the
  screen (`document.documentElement.scrollWidth` equals the viewport, so no sideways scrolling):
  `/`, `/explorer`, `/explorer/PSI-69`, `/explorer?q=extinction`, `/scenario`, `/comparison` with
  no scenario and with a lunar one, `/visualization`, `/assistant`, `/methodology` and `/sources`.
  `/visualization` also fits at 720px.
- What was not rerun here: the 200% text size, and the Assistant answer quoting unbreakable file
  names (#29's finding 17, fixed in #74 and passed in #29's own run). #29 notes that at 320px the
  two FLEX tables sit 5px into the right margin, inside the screen.

### 8. The deployed URL passes the same page checks as the local build: **Pass** on https://cosmic-shihab.vercel.app

- `docs/DEPLOY.md` and `docs/DECISIONS.md` name cosmic-shihab.vercel.app (#68). #38 found that the
  site they named before, flare-sandy.vercel.app, served an older build.
- On cosmic-shihab.vercel.app:
  - All 8 routes return `200 text/html`; `/favicon.svg` returns `200 image/svg+xml`; `/api/nope`
    returns `404 application/json`; `/api/health` returns `{"status": "ok", "investigations": 24,
    "files": 60866, "retrieved": "2026-11-14"}`.
  - Checks 1 to 7 give the outputs above. Its JavaScript bundle holds the code of #75, #76 and #77,
    and its download route behaves as #78's code does. The site does not say which commit it serves.
  - `/api/flex-model` returns 200, and the Visualization page shows its notice ("not a prediction
    of a real fire") and the held-out macro-F1 chart.
  - Search returns `total 2145` for "extinction", so SQLite FTS5 works on Vercel.
- #29 found the same results on the deployed site as on a local build of the same commit.
- flare-sandy.vercel.app still answers with the older build: `/api/assistant/summaries/PSI-69`,
  `/api/assistant/readings` and `/api/flex-model` return 404.

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

## Source links (section 8, "Do source links open?"): **Pass**

`GET /api/files/{file_id}/download` on the live site, for the first file of 5 investigations, then
a one-byte request to the address it redirects to:

| Investigation | Download route | Redirects to | File |
|---|---|---|---|
| PSI-25 (BASS-II) | `307` | `psi-curation-prod.s3.amazonaws.com` | `206, bytes 0-0/1123356` |
| PSI-69 (FLEX) | `307` | `psi-curation-prod.s3.amazonaws.com` | `206, bytes 0-0/26750` |
| PSI-107 (SPICE), PSI-26 | `307` | Not read | Not tried |
| PSI-159 | `307` | `psi-repo-prod.s3.amazonaws.com` | `206, bytes 0-0/7496324` |

- Before #78 the route refused PSI's second bucket, `psi-curation-prod`: in this report's earlier
  run (on `9f86da2`) the same files of PSI-25, PSI-69, PSI-107 and PSI-26 answered 502, and #29 found 25 of 25 sampled document links on `/explorer/PSI-69` failing that way (its
  finding 11). #78 accepts exactly the two PSI hosts.
- Only one file per investigation was tried here.

## Whole-app QA (#29)

#29 tested on 15 November with playwright-core 1.56.1 and Google Chrome 157, headless, on the live
site deployed from `9f86da2` and on a local build of the same commit. Eleven routes at 320, 375,
720 and 1440px and with the browser's text size at 32px (200%), each also with the API answering
500 and with the network cut (84 loads per site); then `break-ui` data swapped in at the API
boundary at 320, 375 and 1440px (30 loads: long acronyms and titles, markup in titles, missing
links, 60 investigations, an empty list, an unknown accession, empty records, long ranked names, a
ranking with no results, and an assistant answer of 30 blocks citing 40 sources with 112-character
file names); and every link on four pages followed (75 links). Details are in `qa_results.md`.

What it found, and where each stands on `25b8889`:

| # | What #29 found | Fixed by | Rerun here |
|---|---|---|---|
| 11 | Every sampled PSI document link on `/explorer/PSI-69` answered 502 | #78 | Yes: 5 of 5 investigations' links redirect, and the 3 files tried open; see "Source links" |
| 12 | The lunar notice was shown once, not on every result | #75 | Yes: 18 of 18 results; see check 4 |
| 13 | `/explorer/PSI-69` scrolled sideways at 320px | #77 (which found it was every record with a DOI, by 60px at 320px) | Yes: fits at 320 and 375px. #77 checked all 24 investigation pages |
| 14 | With an empty catalogue, Explorer still said "The 24 NASA combustion investigations" and blamed filters | #77 | Yes, with `/api/investigations` answering `[]`: the intro says "The NASA combustion investigations in PSI." and the box says "The PSI catalogue came back empty…", with no filter message |
| 15 | An empty `page_url` made a link with no target on Home and Sources | #76 | In #76, with the catalogue answer rewritten: 2 blank links per page before, none after |
| 16 | Visualization scrolled sideways at 320 and 720px and with text at 200% | #74 | Yes at 320, 375 and 720px; 200% text not rerun |
| 17 | An Assistant answer quoting an unbreakable file name pushed the page sideways on phones | #74 | Not rerun |

What held up in #29's run: every page shows its error box with "Try again" when the API fails or
the network is cut; long names, 60 investigations and empty records render without `undefined`,
`NaN` or `null`; with text at 200% every page switches to the menu; outside links open, apart from
issnationallab.org, which refuses automated requests (403).

## Checks each merged PR ran

What each PR says it checked, and whether that was run again for this report.

| PR | Area | Checks in the PR | Run again here |
|---|---|---|---|
| #11 | Catalogue API | 12 tests against counts read from the data files | Yes, in the backend suite (`test_catalogue_api`, 12) |
| #20 | File download link | 5 tests with faked PSI answers; one live run fetched the 4,726-byte BASS table byte for byte | Tests pass (`test_downloads`, now extended by #78); live downloads work; see "Source links" |
| #21 | Experimental tables | 17 tests on real rows | Yes (`test_process_tables`, 17) |
| #22 | Investigation tags | `test_tags`; the PR notes backend tests were not run on its author's machine | Yes, both suites pass (`test_tags`, 4) |
| #23 | Design system, Home, Sources | Impeccable finish review ("ship"); `break-ui` not done | The build passes; worst-case QA was done in #48 and #29 |
| #24 | Document search | 17 pipeline and 8 backend tests; FTS5 on Vercel unchecked | Yes; FTS5 checked live (`total 2145`) |
| #31 | Ranking | 27 new tests (52 backend tests at the time) | Yes (`test_ranking` 18, `test_ranking_api` 6, `test_runs` 3) |
| #32 | Run analysis | 5 tests, one fails if the committed output goes stale | Yes, 5 pass |
| #34 | Coordinator | 14 tests | Yes, 14 pass |
| #41 | AI assistant | 23 tests with a fake model client; live model call untested (no key) | Yes (`test_assistant_api`); the live page was asked three questions (check 6) |
| #42 | Methodology page | Numbers traced to repo files by hand; no tests listed | The build passes; fits at 320 and 375px |
| #43 | Vercel deploy | The curl checks in `docs/DEPLOY.md` | Yes, on cosmic-shihab.vercel.app; see check 8 |
| #44 | Runs API | 10 endpoint checks (85 backend tests at the time) | Yes (`test_runs_api`, 10) |
| #45 | FLEX outcome model | A test reruns training and requires the committed results to match exactly | Yes (`test_committed_results_are_what_this_code_produces`), plus 6 FLEX data tests and 8 API tests |
| #48 | QA of Home and Sources | `qa_results.md` | Not run again; its findings #46 and #47 were fixed by #54 and #50 |
| #49 | Explorer, Scenario, Comparison | 22 helper tests | Yes, they pass; checks 2 to 5 were rendered on its Comparison page |
| #50 | Empty and changing data on Home and Sources | Edge at 375 and 1440px with the API's answer swapped (real, empty, one, no link or DOI, 500, offline); build and 22 tests | The build and tests pass; #29 ran the same kinds of data on every page |
| #51 | Visualization page | Every drawn count matches `summary.md`; colours checked with the dataviz validator; Impeccable finish review | The build passes; fits at 320, 375 and 720px; not looked at by eye here |
| #52 | Submission drafts | Numbers recounted from committed files; 24 DOIs and 20 row counts matched | Not run again |
| #53 | FLEX model panel | Every number read from `results.json`; Impeccable finish review | Rendered live: the notice and the held-out macro-F1 chart appear |
| #54 | Layout fixes on Home and Sources | 200% text, 1440, 375 and 320px; tests and build | The build and tests pass; fits at 320 and 375px; #29 reran 200% text |
| #55 | Summary and reading generator, `/api/assistant/readings` | 103 backend tests | Yes, in the backend suite (`test_readings` included) |
| #57 | Pitch opening | 46 browser checks on the HTML file, plus an offline run | Not run again |
| #58 | Stored summaries and readings | Every citation quoted word for word, every number in a cited sentence found in its source, no Markdown, 211 to 279 words | Not run again; #63 reviewed all 27 files |
| #60 | Flame and gravity visuals on Methodology and Scenario | 1440, 1000 and 375px with live data; build and 22 tests | Their text ("Illustration made with AI", "Gravity tested") is in the live bundle; both pages fit at 320 and 375px; not looked at by eye here |
| #61 | This report's start (#38) and the FLEX test fix | Every suite and check, run on `299dba6` | Yes, all of it, on `25b8889` |
| #63 | Summaries and readings signed as reviewed (#28) | The README's five checks on all 27 files; 103 backend tests | Yes: live, all 24 summaries and 3 readings are `reviewed: true` |
| #64 | The team's own logos | Sources at 1440 and 375px | The live bundle uses `cosmic-shihab-logo-white`; `Logo.jpg` is no longer in the repo; Sources fits at 320 and 375px |
| #67 | AI summaries on Explorer and Comparison (#39) | 27 frontend tests; Edge at 1440 and 375px (citation clicks, unreviewed and missing files, a weight hiding the reading) | Yes, live; see "Stored AI summaries and readings" |
| #68 | Docs name cosmic-shihab.vercel.app; QR code | `docs/DEPLOY.md`'s checks against the new URL | Yes; see check 8. The QR code was not decoded again |
| #69 | Visualization follows a scenario; Home astronaut (#65) | 1440 and 375px in a headless browser; build and 27 tests | Visualization and Home fit at 320 and 375px (Visualization also at 720px); the new figures were not checked by eye here |
| #74 | Whole-app QA (#29) and its Visualization and Assistant fixes | `qa_results.md`: findings 11 to 17, the eight concrete checks, what held up | Fixes for 13 to 16 rerun; see "Whole-app QA" |
| #75 | Microgravity notice on every result (#70) | 18 of 18 API items carry a note; 1440 and 375px, 6 of 6 shown rows | Yes: 18 of 18 with every result shown (check 4) |
| #76 | No dead PSI link from an empty `page_url` (#72) | Edge with the catalogue answer rewritten: 2 blank links per page before, none after | That check is this PR's own; not run again |
| #77 | Investigation pages on phones; Explorer's empty list (#71) | All 24 investigation pages at 320 and 375px; `/explorer` with real data and with `[]` | Yes: `/explorer/PSI-69` at 320 and 375px, and `/explorer` with `[]` |
| #78 | Downloads from PSI's second host (#73) | Extended `test_downloads`; three FLEX documents redirect live and return the PDF (206) | Yes: 105 backend tests pass; live, 5 of 5 investigations redirect, and the 3 files tried answer 206 |

## Open problems these checks found

- **The Assistant's citation numbers don't move the page.** On the live site, clicking citation 1
  sets the address to `#src-1` but leaves the page at the top, with the source 1,757px below.
  React Router's `<ScrollRestoration>` gives a `#hash` link the same history key as the page and
  puts the scroll back. #67 avoids this in the summary block by scrolling to the source itself; the
  Assistant (#41's area) needs the same.
- **Most error boxes say the API "did not answer" even when it answered with an error.** Checked
  in the code on `25b8889`: 9 `<LoadError>` calls don't pass `error={…}` as #47's decision asks, in
  Assistant, Comparison, Explorer, the investigation page (2 calls), document search, Scenario,
  Visualization and the FLEX model panel. The Assistant still says "Loading the 24
  investigations…" with a fixed number.
- **flare-sandy.vercel.app still serves an older build.** The docs no longer name it (#68), but
  anyone with the old link gets a build from before #45 (its `/api/flex-model` returns 404).
  `docs/DEPLOY.md`'s redeploy command still deploys to that project (#68's note).
- **Unflagged suspect values are still scored by the ranking,** such as FLEX test 114 at 0 mmHg and
  the negative SPICE air rates (#32, `research/analysis/suspect_values.csv`). Not rerun here.
- **Not rerun here, from #29:** text at 200% after #74's fixes, and the worst-case Assistant answer
  (finding 17). `pipeline/psi_client.py` still accepts only `psi-repo-prod` (#78's note), which is
  fine for the tables it downloads today.

**AI use:** this report was put together with Claude Code (Claude Opus 5.5) and reviewed by the
team. Every output in it comes from a command or page run on 14 or 15 November 2026; none was
written by the model. #29's results are from its own run, recorded in `qa_results.md`.
