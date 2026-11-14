# Limitations and assumptions

FLARE helps people find and compare NASA's combustion research. It does not predict fires, it does
not certify that any environment is safe, and it never fills a gap in NASA's data with a guess.
These are the limits a researcher should know before relying on it.

## The evidence

- **No partial gravity.** NASA's PSI holds no combustion tests in lunar or Martian gravity; its
  tests ran in microgravity or in normal gravity. FLARE says so on every result of a lunar or
  Martian scenario and never interpolates between the two. Partial-gravity data is expected later
  from the Lunar-g Combustion Investigation (LUCI) and the Flammability of Materials on the Moon
  (FM2) experiment.
- **Uneven coverage.** 20 of the 24 investigations publish a test table; the other four analyse
  other investigations' data. The tables hold 2,009 rows, but conditions are often missing: 1,147
  rows record oxygen, 1,001 pressure and 570 airflow. The three Saffire experiments, which burned
  large samples inside an uncrewed spacecraft, have 21 rows between them.
- **Values that look wrong.** FLARE's profiling found 117 suspect values (for example a FLEX test
  at 0 mmHg). Flagged values are left out of the score, but not every suspect value is flagged, so
  a few still take part (`research/analysis/suspect_values.csv` lists them all with file and line).
- **Documents.** The assistant and the search read the NASA documents FLARE could extract text
  from: 256 documents from 19 investigations. Scanned pages without text, and formats it could not
  read, are not searched.
- **An apparatus, not a cabin.** Each experiment ran in its own chamber or apparatus. None of
  them is a crewed cabin, so a close match says the conditions were similar, not that a fire in a
  cabin would behave the same way.

## The ranking

- **A relevance score, not a safety assessment.** It measures how close NASA's test conditions are
  to the scenario. A score of 100 means a test matched every condition set; it says nothing about
  how dangerous that condition is.
- **The scale comes from the data.** "Close" is measured against a quarter of the range NASA
  tested (0.1825 oxygen mole fraction, 1.25 atm, 22.8 cm/s), not against a fire-science threshold.
  A different choice would change the scores and, when several conditions are set, how much each
  one counts, so it could change the order.
- **Equal weights by default.** FLARE does not claim any variable matters more for fire safety.
  The visitor can change the weights; the default is a statement of neutrality, not of physics.
- **The best test decides.** An investigation scores as its closest test. One close test is enough
  to rank high; the number of close tests is shown beside it.
- **Simple matching for words.** Fuel matches when every typed word appears in the test's fuel;
  fuel phase and fire-safety role come from FLARE's tags for each investigation, which cite the
  record field they were read from but are FLARE's reading of it.
- **One number per condition.** The challenge gives some values as bounds ("30 % or greater",
  "10.2 psi or less"); FLARE ranks against the stated number, not the range.
- **Not compared:** research objectives and the outcomes each investigation measured. The
  outcomes are listed, not scored.

## The AI assistant and the stored summaries

- Answers come only from the PSI records and indexed documents, and every sourced sentence cites
  the words it rests on. A model can still misread a source; the citations are there so a reader
  can check, and the assistant's own explanation is marked apart.
- The 24 summaries and 3 readings were generated once by Claude Opus 5.5 and reviewed by one team
  member against their sources, with an AI checking each citation first. They describe what the
  sources say, not new findings.

## The FLEX model

- **One investigation.** It is trained on FLEX's 274 droplet tests (methanol and heptane in FLEX's
  chamber aboard the International Space Station). Nothing in it carries over to other fuels,
  materials or a spacecraft cabin.
- **A small test set.** 54 held-out tests on 17 days, so one test moves a class score a lot;
  cross-validation on the training days varies by ±0.109 macro-F1.
- **The chosen model did not score best on the held-out days.** The random forest was chosen
  beforehand, on cross-validation (0.566 against 0.484); on the held-out days logistic regression
  scored higher (0.541 against 0.475). The choice was kept, as decided before looking.
- **Rare endings are missed.** On the held-out days the random forest found 0 of 6 completions, 11
  of 12 disruptions and 26 of 36 extinctions.
- **SHAP is not cause.** It shows what the model relies on, not what makes a flame go out.

<!--
For the team (not for the form). Draft for the limitations part of the package, issue #15. Sources:
- Partial gravity, LUCI, FM2: the challenge page as quoted in the master prompt, section 5
  ("Partial gravity, stated exactly").
- 20 of 24 with tables, 2,009 rows: GET /api/runs (22 tables, 20 accessions) and /api/runs/rows on
  the live site, 15 Nov 2026. Four catalogue only, 1,147/1,001/570, Saffire 21 rows, 117 suspect
  values: submission/datasets.md (#36) and its sources.
- "a FLEX test at 0 mmHg": backend/data/flex_model/results.json data.pressure_zero_read_as_missing
  [114]. Unflagged suspect values still scored: found by #32, reported in submission/test_report.md
  (not rerun).
- 256 documents from 19 investigations: submission/datasets.md notes (backend/data/search.sqlite).
- Ranking: backend/app/ranking.py and submission/ranking.md (tolerances printed 15 Nov 2026).
- Tags cite a record field: the investigation page's footnote (frontend/src/pages/ExplorerInvestigation.jsx)
  and research/investigation_tags.csv.
- Bounds: master prompt section 5, "Presets need a source"; frontend REFERENCES "at least"/"at most".
- Summaries: backend/data/summaries/README.md, #63 (reviewed by Aminpatra after an AI check,
  docs/ai-use/Aminpatra.md).
- Model: backend/data/flex_model/results.json `limitations`, `cross_validation.scores`, `held_out`.
-->
