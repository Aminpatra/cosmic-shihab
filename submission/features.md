# Implemented and planned

Everything under "Implemented" runs on https://cosmic-shihab.vercel.app today and was checked there
(`test_report.md`). Everything under "Planned" was asked for in our plan or found in testing, and is
not built.

## Implemented

**Data**
- All 24 NASA PSI combustion investigations: records, file lists (60,866 files) and DOIs, read from
  PSI's public web service.
- 22 experimental tables from 20 investigations, 2,009 test rows, each value kept as NASA published
  it, with every conversion marked as calculated (FLEX's 757.7 mmHg stays 757.7 mmHg, shown as
  0.997 atm, converted by FLARE).
- Data profiling: missing values shown as "not recorded", 117 suspect values listed with file and
  line.
- Full-text search over the text of NASA's documents for 19 investigations.
- Download links to NASA's files, fetched fresh from PSI when clicked.

**Ranking and comparison**
- Scenario form with six environments, oxygen, pressure in three units, airflow, fuel, fuel phase
  and fire-safety role; presets only for the values the challenge page states, with the source.
- Ranking of every test row against the scenario, with score, close tests, matches, differences,
  unavailable variables, variables used and the three closest tests; adjustable weights.
- The partial-gravity note on every result of a lunar or Martian scenario.
- Side-by-side comparison of up to three investigations on shared axes, one lane per condition,
  with "not recorded" hatched.
- Every ranking and comparison is a link that can be shared.

**Exploring**
- Explorer with filters (platform, fuel phase, fire-safety role, gravity, data in FLARE), a page per
  investigation with NASA's record unchanged, its files, publications and document search.
- Visualization: the experimental tables as charts, a coverage matrix of which conditions each
  table recorded, the tests near a chosen scenario, and the FLEX model's results.
- Methodology and Sources pages: how data is read, ranked and answered, its limits, and every
  reference.

**SI**
- Research assistant (Claude Opus 5.5) that answers only from PSI records and documents, cites every
  sourced sentence, marks its own explanation, says when no source answers, and still returns the
  matching sources without an SI key.
- 24 stored investigation summaries and 3 readings of the challenge scenarios' rankings, reviewed
  against their sources and labelled SI-generated with model, date and reviewer.
- One model: FLEX test outcomes, judged against a majority-class baseline on held-out test days,
  with a chance check and SHAP.

**Quality**
- Automated tests: 105 for the API, 60 for the pipeline, 5 for the run analysis, 27 for the website's
  logic (all passing on 15 November 2026).
- Every page checked at 320, 375 and 1440px, with text at 200 %, with the API failing, and with
  worst-case data (`qa_results.md`).

## Planned, not built

- **Export** of the filtered test rows as CSV or JSON with NASA's column names, units and source
  links.
- **Within one investigation,** which conditions were varied across its tests and which were held
  constant.
- **A richer ranking:** similarity of research objectives, the relevance of the outcomes measured,
  and scenario values given as ranges ("30 % or greater") rather than single numbers.
- **Partial-gravity evidence** once PSI publishes results from LUCI and FM2.
- **Fixes found in testing:** the assistant's citation numbers should scroll to their source, and
  the error messages on most pages should say when the API answered with an error rather than not
  at all.

<!--
For the team (not for the form). Draft for "features fully implemented versus planned", issue #15.
Sources:
- 24 investigations, 60,866 files: GET /api/health (15 Nov 2026). 22 tables, 20 accessions, 2,009
  rows: GET /api/runs and /api/runs/rows. 117 suspect values, 19 investigations with indexed
  documents: submission/datasets.md.
- Conversions marked: test_report.md check 2; pipeline/process_tables.py.
- Six environments: frontend/src/pages/ScenarioParams.js PLACES. Shareable links: docs/DECISIONS.md (#13).
- Ranking outputs: backend/app/ranking.py _rank_one(); weights: weight_<variable>.
- Explorer filters: frontend/src/pages/ExplorerFilters.js. Visualization: frontend/src/pages/Visualization.jsx
  (CoverageMatrix), components/ScenarioProbe.jsx (#69), components/FlexModel.jsx (#53).
- Assistant: backend/app/assistant.py; live status generated, claude-opus-5-5.
- Test counts: submission/test_report.md (run on 25b8889, 15 Nov 2026). QA: submission/qa_results.md (#29).
- Planned items: master prompt section 5 "Investigation matching and ranking" and "Additions"
  (export, varied/held constant, ranges); checked absent in frontend/src and backend/app on
  25b8889 (no CSV/JSON download, no varied/held-constant view; ranking.py scores no objectives or
  outcomes). Fixes: test_report.md "Open problems".
-->
