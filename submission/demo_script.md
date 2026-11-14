# Demo script: FLARE on the live site

A walkthrough of https://cosmic-shihab.vercel.app in about three minutes, for presenting the app
live or for a judge opening it on their own. Every step is a real link, and what it shows is what
the site showed when it was tested (`test_report.md`). The 7-slide deck is prepared separately and
opens with the pitch in `pitch/`.

Before presenting: open each link once so the site is warm, and keep a second tab on the
Assistant, since a live answer takes several seconds.

## 1. The question (20 s)

**Open** https://cosmic-shihab.vercel.app

> A fire in a spacecraft or a Moon base is one the crew can't walk away from. NASA has run 24
> combustion investigations to learn how flames behave without gravity. FLARE answers the
> question a designer actually has: which of NASA's tests looks like my situation?

## 2. A scenario, ranked (45 s)

**Open** https://cosmic-shihab.vercel.app/comparison and click **Moon base or pressurized rover**
(30 % oxygen, 10.2 psi, the values the challenge page states).

> FLARE compared all 2,009 test rows NASA recorded with this scenario. FLEX ranks first with a
> score of 100: 59 of its 274 tests are close. Every result says which conditions match, which
> differ and what NASA never recorded, and every result carries this note: the scenario is at
> 0.17 g, and NASA's evidence comes from microgravity, not partial gravity. And this is a relevance
> score, not a safety assessment.

**Point at** "Reading of this ranking": an AI-written reading, reviewed by a team member, with
every sourced sentence cited.

## 3. Compare on the same axes (30 s)

**Scroll to** "Condition by condition". The top two, FLEX and ACME CFI-G, are already picked; a
third can be ticked in the list.

> Each condition is one lane. The yellow tick is the scenario, the blue band is what NASA tested,
> and hatching means not recorded, never a zero. Below are the closest tests with NASA's own column
> names and units: a pressure NASA recorded in mmHg stays in mmHg, with FLARE's conversion to atm
> marked.

## 4. One investigation, at the source (25 s)

**Open** https://cosmic-shihab.vercel.app/explorer/PSI-69

> The AI summary leads, labelled with the model, the date and the reviewer, and each sourced
> sentence links to the words it came from. Below it is NASA's own record, unchanged, its files with download
> links, and a search inside its documents.

## 5. Ask, and get "not found" when that's the truth (30 s)

**Open** https://cosmic-shihab.vercel.app/assistant and ask:
*What droplet burning rate did FLEX measure at lunar gravity?*

> The answer starts: the documents don't give any FLEX droplet burning rate at lunar gravity.
> Claude Opus 5.5 answers only from NASA's records and documents, cites what it uses, and says
> when the sources don't answer, instead of inventing one.

## 6. The science, honestly (20 s)

**Open** https://cosmic-shihab.vercel.app/visualization and scroll to the FLEX model.

> One model, on FLEX's 274 tests: how did a test end, given only what was set before it? Judged on
> days it never saw, it beats the majority-class baseline, 0.475 macro-F1 against 0.267, and the
> panel says what that is: a pattern in NASA's tests, not a prediction of a real fire.

## 7. Close (10 s)

> FLARE turns NASA's microgravity combustion data into answers a designer can check: ranked,
> explained, sourced, and honest about the gaps.

<!--
For the team (not for the form). The demonstration script the brief asks for (section 9, item 10),
issue #15. Every on-screen claim is from submission/test_report.md (live site, 15 Nov 2026):
- Moon base preset link and the scores: test_report.md "Stored AI summaries and readings";
  59 of 274 close: ranking.rank on the Moon base scenario (submission/ranking.md example).
- Note on every result: check 4. 757.7 mmHg: check 2. The FLEX page's summary: "Stored AI
  summaries". The Assistant's answer: check 6. Model panel and numbers: check 8 and
  backend/data/flex_model/results.json (held_out random_forest 0.475, baseline 0.267).
- "2,009 test rows": GET /api/runs/rows total.
- The deck and pitch/ are the team's separate work; adjust step timings to fit around it.
- "each sourced sentence links to the words it came from": frontend/src/components/AiSummary.jsx.
- Top two picked by default: parsePicks() in frontend/src/pages/ComparisonLanes.js. The mmHg line:
  the Moon base link was not checked for a mmHg value; check 2's link shows
  "757.7 mmHg (0.997 atm, converted by FLARE)", so use that link if a concrete value is wanted.
-->
