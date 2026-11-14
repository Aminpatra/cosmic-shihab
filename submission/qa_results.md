# QA results

What was tested on the live FLARE site, what broke, and what held up. #37 covers Home and Sources;
the whole-app pass (#29) adds the other pages below, and `test_report.md` (#30) reports from this
file. Each problem is filed as an issue for the page's owner.

## Home and Sources (#37)

**Tested** 14 November 2026 on https://flare-sandy.vercel.app, deployed from `main` at `3549a67` (#43).
Playwright 1.65.1 driving headless Chromium 153.

**How.** Each page was loaded at 320px and 375px (phones), 1440px (laptop), 720px (a 1440px screen
at 200% browser zoom) and 1440px with text at 200% (the browser's font-size setting). The
investigation list was swapped at the API boundary, without changing any page code, for these
datasets:

| Dataset | What it holds |
|---|---|
| Real | The live `/api/investigations` (24 investigations) |
| Worst case | The real list plus realistic extremes spread across rows: a 37-character acronym, a 205-character title with no acronym, a title with `&` and quotes, a long flight programme, a 41-character licence id with no spaces, a 12,845-run table, an investigation with no PSI link or DOI, one with no retrieval date, and a 25th investigation (LUCI) |
| Empty | An empty list |
| One | Only FLEX |
| Huge | 60 investigations |
| Error | The API answers 500 |
| Offline | The request fails |

Each run checked whether the page scrolls sideways and what causes it, clipped text, the text
`undefined`, `NaN` or `null`, links with no target, console errors, and the loading and error
states. "Try again" was clicked after the error. Every link on both pages was followed. Key
screens were looked at, not only measured.

### What broke

Severity: **Broken** (content unreachable or wrong), **Ugly** (readable but visibly wrong),
**Fragile** (fine with today's data, one realistic step from breaking).

| # | Severity | Page | Data | What happens | Issue |
|---|---|---|---|---|---|
| 1 | Broken | Both | Real, text at 200% | Nav labels run off the page, the page scrolls about 900px sideways, catalogue names break mid-word ("ACM") | #46 |
| 2 | Ugly | Home | Real, 320px | Page scrolls 25px sideways: a label in the FLEX example's condition lanes cannot wrap | #46 |
| 3 | Ugly | Sources | Real, 375px | Titles are cut to two lines with no way to read the rest; PSI-60 and PSI-62, which have no acronym, lose their name, and ACME titles lose the part that tells them apart | #46 |
| 4 | Ugly | Sources | Real, 375px | A wrapped detail line starts with a separator bar ("&#124; Show and compare &#124; CC0-1.0") | #46 |
| 5 | Fragile | Both | Empty | No empty state: Home says "PSI lists 0 files (0.0 TB) for these 0 investigations" with nothing below; Sources shows an empty table "retrieved on an unknown date" | #47 |
| 6 | Fragile | Both | Worst case (25) | "24" is written into the copy in four places, so with a 25th investigation the copy contradicts the table | #47 |
| 7 | Fragile | Sources | Worst case | An investigation with no PSI link gets a link with no target; one with no DOI gets an empty link back to the page | #47 |
| 8 | Fragile | Home | Huge, 375px | 60 investigations push the catalogue strip 11px past the edge | #46 |
| 9 | Fragile | Sources | Worst case, 320px | A licence id with no spaces pushes the page 37px sideways | #46 |
| 10 | Fragile | Both | One, Error | "these 1 investigations"; the error box says "The FLARE API did not answer" even when it answered with an error | #47 |

The fix for each, with file and line, is in the issue.

### Decisions for the page owners

- **Long titles on phones (3):** clamp only rows that have an acronym, since the acronym already
  names them, and show the full title on hover or tap. Recommended, because a row without an
  acronym has nothing else to identify it.
- **The number of investigations in the copy (6):** say the count only once it has loaded, or keep
  "24" and treat it as a fact to update with the data. Recommended: the loaded count, because PSI
  plans to add partial-gravity investigations.

### What held up

- All 50 outside links open: 24 PSI records, 24 DOIs (each resolves to its own investigation's PSI
  page), the PSI home page and the Space Apps brand page. All 13 internal links and anchors reach
  real pages, including `/methodology#tables`.
- With real data at 375px and 1440px, neither page scrolls sideways, and at 200% browser zoom the
  navigation collapses to its menu as designed.
- Error and offline: both pages show the error box and nothing else in that section, and "Try
  again" recovers all 24 rows. A loading state shows while the list loads.
- No `undefined`, `NaN` or `null` anywhere, even with a missing retrieval date ("an unknown date")
  or a missing acronym (the accession is shown instead).
- Long acronyms and titles wrap in Home's catalogue lists; `&` and quotes show as text; 12,845 runs
  shows as "12,845 runs".
- On a laptop, a widened Sources table scrolls inside its own frame rather than moving the page.
- No console errors other than the failed request in the error and offline runs.

## Every other page and the deployed site (#29)

**Tested** 15 November 2026 on https://cosmic-shihab.vercel.app, deployed from `main` at `9f86da2`
(#68), and on the local build of the same commit (then again after this branch's fixes, `fe17798`).
playwright-core 1.56.1 driving Google Chrome 157, headless.

**How.** Eleven routes (Explorer, an investigation page `/explorer/PSI-69`, Explorer search,
Scenario, Comparison with no scenario and with a lunar one, Visualization, Assistant, Methodology,
Sources, Home, and an unknown path) were loaded at 320px, 375px, 720px (a 1440px screen at 200%
zoom) and 1440px, and at 1440px with **Chrome's default text size set to 32px**, the reader's
setting. (Raising the page's own `font-size` from CSS does not move `em` media queries, so it is
not a valid stand-in; a first run that did so reported a false navigation overflow on every page.)
Each route was also loaded with the API answering 500 and with the network cut. With the same
checks as #37 (sideways scroll and its cause, `undefined`/`NaN`/`null`, links with no target,
console errors), this made 84 loads per site. Then `break-ui` data was swapped in at the API
boundary, without changing page code, at 320, 375 and 1440px (30 loads): a 39-character acronym
and a 205-character title, a title with `&`, quotes and tags, an investigation with no PSI link or
DOI, 60 investigations, an empty list, an unknown accession, a record with every text field empty,
ranked results with those long names, a ranking with no results, and an assistant answer of 30
blocks citing 40 sources with 112-character file names and unbreakable tokens. Every link on the
investigation, Comparison, Visualization and Methodology pages was followed (75 links).

### What broke

| # | Severity | Page | Data | What happens | Issue |
|---|---|---|---|---|---|
| 11 | Broken | Investigation | Real | Every sampled PSI document link (25 of 25 on `/explorer/PSI-69`) answers 502: PSI now serves legacy files from `psi-curation-prod.s3.amazonaws.com`, which the download endpoint refuses | #73 |
| 12 | Partly | Comparison | Real, lunar | The microgravity notice is shown once above the list, not on every result, though the API gives each result its own note | #70 |
| 13 | Ugly | Investigation | Real, 320px | The publications list pushes the page 11px sideways | #71 |
| 14 | Fragile | Explorer | Empty | The lede still says "The 24 NASA combustion investigations"; the empty message blames filters when none is set | #71 |
| 15 | Fragile | Home, Sources | Worst case | An empty `page_url` still makes a link with no target (`??` does not catch `''`); #47 covered a missing one | #72 |
| 16 | Ugly | Visualization | Real, 320 and 720px, text 200% | Page scrolled 23, 37 and 110px sideways (strip labels, FLEX tables) | fixed here (`fe17798`) |
| 17 | Fragile | Assistant | Worst case, phones | An answer quoting an unbreakable file name pushed the page 136 to 189px sideways; live answers do quote file names | fixed here (`fe17798`) |

Also fixed here: Assistant, Methodology and Visualization breakpoints moved from px to em, as the
team decided (`docs/DECISIONS.md`). After the fixes, the local build passes every check above at
every width and with text at 200%, except the issues still open (11 to 15). At 320px the two FLEX
tables sit 5px into the right margin (inside the screen, nothing hidden).

### Concrete checks (master prompt section 8), on the deployed site

| Check | Result | Evidence |
|---|---|---|
| 129 BASS-II runs and 274 FLEX tests load | Pass | `GET /api/runs`: row_count 129 and 274 |
| 757.7 mmHg stays 757.7 mmHg, conversion marked | Pass | FLEX row: `original {757.7 mmHg}`, `calculated: true`; Comparison shows e.g. "529 mmHg (0.696 atm, converted by FLARE)" |
| Empty scenario gives an explained result | Pass | `GET /api/rank`: no items, "Set at least one condition to rank."; the page says so too |
| Lunar scenario shows the microgravity notice on every result | Partly | API: 18 of 18 results carry `gravity_note`; the page shows it once (#70) |
| Changing one value changes the right scores and the explanation names it | Pass | Oxygen 0.21 to 0.30: BASS-II, SAFFIRE-I and -II, CFI drop (100 to 51-57); FLEX, ACME, CFI-G stay 100 (tests at both values); all 18 name oxygen (7 as match or difference, 11 as unavailable) |
| An unanswerable question gets "not found" with nothing invented | Pass | Nonsense: retrieval only, "No NASA source in FLARE matches this question." Plausible but unanswerable ("the astronaut who ran FLEX test 114"), Claude Opus 5.5: "The documents provided don't name the astronaut…", every claim cited |
| Every page works at 375px and survives `break-ui` | Partly | Yes after this branch's fixes, except 13 to 15 |
| The deployed URL passes the same page checks as the local build | Pass | Same findings on both, before the fixes; the download failure (11) reproduces locally too |

### What held up

- Error and offline: every page shows its error box with "Try again" and no broken layout; the
  investigation page keeps its back link. Empty states explain themselves (Comparison with no
  results lists the six investigations it could not rank, with the reason).
- Long acronyms, 205-character titles, 60 investigations and empty records render without
  `undefined`, `NaN` or `null` on Explorer, the investigation page and Comparison.
- With text at 200%, every page switches to the menu and none scrolls sideways (after fix 16).
- Outside links open, apart from issnationallab.org, which refuses automated requests (403).
- The deployed assistant runs Claude Opus 5.5 (`GET /api/assistant/status`: generated).
