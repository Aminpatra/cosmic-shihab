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
