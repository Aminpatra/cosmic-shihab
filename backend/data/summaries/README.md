# backend/data/summaries

AI-generated text that FLARE stores so the demo never depends on a live model call. Written by
`pipeline/write_summaries.py` with Claude Opus 5.5 through the assistant (`backend/app/assistant.py`),
from the cited NASA sources. Every file starts as `"reviewed": false`.

| Files | What | Served by |
|---|---|---|
| `<ACCESSION>.json` | A 150 to 250 word summary of one investigation | `GET /api/assistant/summaries/{accession}` |
| `readings/<preset>.json` | A plain-language reading of the ranking for one preset scenario: `lunar-base`, `spacesuit`, `sea-level-air` | `GET /api/assistant/readings` |

Each file holds `blocks` (sentences; `kind: "source"` with `citations`, or `kind: "explanation"`
for the assistant's own words) and the `sources` they cite. A reading's first source is the FLARE
ranking itself (`kind: "ranking"`), so the reading explains the ranking and cannot change it; the
endpoint adds `current: false` when the live ranking no longer has the same order.

## Reviewing

Read each file against its sources before setting `reviewed`. It passes only if all of these hold:

1. Every `source` sentence says only what its `cited_text` says. Each number, material and condition
   appears in the cited text, with the same unit.
2. No `explanation` sentence states a fact about an investigation, its results or its conditions.
3. It says what the sources don't state (results, conditions) instead of filling the gap.
4. It gives no safety advice and never calls a relevance score a safety assessment.
5. A reading keeps the ranking's order and scores, includes the gravity note when the ranking has
   one (`lunar-base`), and calls the evidence microgravity, not partial gravity.

Then set `"reviewed": true` and `"reviewed_by": "<your GitHub login>"` and commit. If a check fails,
fix nothing by hand: regenerate with `--force --only <name>`, or leave it unreviewed and note why in
the pull request. Pages show an unreviewed file as unreviewed.
