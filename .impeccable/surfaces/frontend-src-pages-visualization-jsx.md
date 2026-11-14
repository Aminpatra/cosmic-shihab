---
version: 1
slug: "frontend-src-pages-visualization-jsx"
primary_target: "frontend/src/pages/Visualization.jsx"
related_targets: []
---

# Data Visualization surface (/visualization)

Mode: Read. Researchers and judges learn what PSI's experimental tables actually recorded and
where the tests sit, from real rows only (GET /api/runs, /api/runs/rows). Charts and captions
follow research/analysis/README.md (#32): suspect values left out (pipeline flags, pressure <= 0,
negative flow), only tables whose rows are tests, inverse-flame oxygen marked as the burner
stream's, correlation never presented as cause, units as PSI wrote them.

States: loading, API error, a coverage cell with values, a cell with no column (hatched, not
clickable as data), phone width.

## Direction contract

THESIS: The coverage matrix is the page's index: the visitor first sees what each test table
recorded, then opens any cell to see those values. It refuses a dashboard of unrelated chart tiles.

OWN-WORLD: DESIGN.md unchanged: Deep Blue ground, hairline ramp-3 rules, one data text size,
Blue Yonder band-fill for recorded data (shaded by share recorded), 135-degree hatch for a field a
table has no column for, a Neon Yellow frame on the chosen cell, provenance footnote under every
figure naming the PSI column, Fira Code for file names only.

STORY: The visitor sees which fields each of the 14 test tables gives, opens a cell to see its
spread, then reads three fixed figures (oxygen by pressure, FLEX burning rate by oxygen, and the
FLEX test-outcome model panel with its notice, held-out scores against the baseline and limits,
added by #40) with their caveats, and leaves knowing what can and cannot be compared.

FIRST VIEWPORT: H1 and lede at left; below, the full-width coverage matrix (tables as rows, six
fields as columns, cells shaded by share recorded, hatched where absent) with one cell preselected
and framed in Neon Yellow; its value strip begins directly beneath with caption and source.

FORM: Coverage matrix as the index, position 3 of 7 on my list. seed:6dcf35d2f255d928
SIGNATURE MOVE: choosing a matrix cell draws that table's values for that field on a scale shared
by every table, so the strip shows where this table sits among all tests.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
