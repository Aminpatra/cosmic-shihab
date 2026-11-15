# FLARE: Fire Learning, Analysis & Research Explorer

**Team Cosmic Shihab · NASA Space Apps Challenge 2026 · Flame in Freefall**

Live: https://cosmic-shihab.vercel.app · Code: https://github.com/Aminpatra/cosmic-shihab

## Summary

FLARE is a research tool for NASA's microgravity combustion data. A researcher or mission planner
describes a fire scenario, such as a Moon base at 30 % oxygen and 10.2 psi, and FLARE ranks NASA's
24 combustion investigations in the Physical Sciences Informatics (PSI) repository by how closely
their actual tests match it. For each one it shows which conditions match, which differ and what
NASA never recorded, with a link to the NASA source. Investigations can be laid side by side on
shared axes, filtered, searched inside NASA's own documents, and questioned through an SI assistant
that separates what the sources say, with citations, from its own explanation. It answers the
Flame in Freefall challenge by making NASA's flame research usable for the next cabin, habitat or
rover design, and it says plainly what the evidence cannot show: a relevance score is not a safety
assessment, and none of NASA's tests ran in lunar or Martian gravity.

## The solution

FLARE turns PSI's 24 combustion investigations into something a person can question with a
scenario.

- **Scenario.** The visitor sets the conditions they care about: environment (spacecraft, space
  station, lunar habitat, pressurized rover, Mars habitat or custom gravity), oxygen, pressure,
  airflow, fuel, fuel phase and fire-safety role. Only the values the challenge page states
  (spacesuit, Moon base, Earth at sea level) are offered as presets, each shown with its source.
  Anything left empty stays empty.
- **Ranking.** FLARE scores every one of NASA's 2,009 recorded test rows against the scenario and
  ranks the investigations by their closest test. Each result says why it ranked where it did:
  the conditions that match, the ones that differ, the ones NASA never recorded, the variables
  used, how many tests came close, and the three closest tests with NASA's own column names and
  units. The method is in `ranking.md`.
- **Comparison.** Up to three investigations are drawn on the same axes, one lane per condition:
  the scenario as a yellow tick, each investigation's tested range as a band, and anything not
  recorded as hatching rather than a zero.
- **Explorer.** All 24 investigations with filters by platform, fuel phase, fire-safety role,
  gravity and the data FLARE holds, a page for each with NASA's record unchanged, its files with download links, its
  publications, and a search inside its documents.
- **Visualization.** The experimental tables as charts, a coverage matrix that shows which
  conditions each table recorded, the tests that sit near the visitor's scenario, and the results
  of FLARE's one model.
- **SI assistant.** Questions about the investigations, answered by Claude Opus 5.5 only from PSI
  records and documents. Every sentence that rests on a source is cited and links to the quoted
  words; the assistant's own explanation is marked as such, and when no source answers it says so.
  Without an SI key it still returns the matching sources.
- **Stored summaries and readings.** An SI-written summary of each investigation and a plain
  reading of the ranking for the three challenge scenarios, generated once, checked by a team
  member against their sources, and labelled as SI-generated with the model, the date and the
  reviewer.

## How it works

An offline Python pipeline reads PSI's public web service once and writes plain files: the 24
records, the file lists, 22 experimental tables from 20 investigations (2,009 rows, every value
kept as NASA published it and every conversion marked), and a full-text search index of NASA's
documents. A read-only FastAPI service serves those files, ranks scenarios and runs the assistant;
a React website presents them. Both run on Vercel. Details are in `architecture.md`, the data in
`datasets.md`.

## What the data shows: one model, judged against a baseline

FLARE trains one model, on the 274 tests of FLEX (the Flame Extinguishment Experiment on the
International Space Station), to ask how a droplet test ended (extinction, disruption or
completion) given only what was set before it: fuel, pressure, oxygen, CO2, helium and droplet
size. Tests from the same day stay on one side of the split, and the model is scored on 54 tests
from 17 held-out days with macro-F1, which weighs the three endings equally.

| Model | Macro-F1, cross-validation on training days | Macro-F1, held-out days |
|---|---|---|
| Majority-class baseline | 0.270 | 0.267 |
| Logistic regression | 0.484 | 0.541 |
| Random forest (chosen beforehand, on cross-validation) | 0.566 | 0.475 |

Both models beat the baseline. On the training days the random forest also beats the same model
trained on shuffled endings (macro-F1 0.537 against a shuffled mean of 0.319 over 40 shuffles,
p = 0.024, the smallest 40 shuffles can give). Oxygen is the input it relies on most to tell
extinction and disruption apart (SHAP). The held-out set is small: the random forest found none of
the 6 completions. This describes a pattern in FLEX's tests aboard the station; it is not a
prediction of a real fire, and the limits are in `limitations.md`.

## Benefits and goals

- **For researchers:** go from a scenario to the NASA investigations that bear on it, and to the
  exact tests and documents, in minutes instead of reading 24 records and their files.
- **For mission planners:** a short, explained list for a habitat or rover scenario, with the gaps
  in NASA's evidence stated, not hidden.
- **For the field:** show where NASA's microgravity combustion data is thick and where it is thin,
  so the next experiment can aim at the gap.

## Tools and languages

Python (pipeline and API, FastAPI, scikit-learn and SHAP for the model, SQLite full-text search),
JavaScript with React and Vite (website), CSS, and Vercel for hosting. The assistant uses Claude
Opus 5.5 through the Anthropic API. The team built FLARE with Claude Code (Claude Opus 5.5 and
Claude Fable 5.2); how is in `ai_use.md`, and every external resource is in `references.md`.

## Team

Amin Mohamed Amin, Gheath Wahab, Mohammed Al-julandani, Samin Rezaei, Rahaf Abubaker Mustafa
Mubarak and Ruayma Khair Mohammed Albalushi.

<!--
For the team (not for the form). Draft for "High-Level Project Summary" (the Summary section) and
"Detailed Project Description" (the rest), issue #15. Sources:
- 24 investigations, 60,866 files: GET /api/health on cosmic-shihab.vercel.app, 15 Nov 2026.
- 22 tables from 20 investigations, 2,009 rows: GET /api/runs and /api/runs/rows on the live site,
  15 Nov 2026; also submission/datasets.md.
- Presets and their source: frontend/src/pages/ScenarioParams.js REFERENCES; docs/DECISIONS.md (#28).
- Ranking behaviour: backend/app/ranking.py; submission/ranking.md.
- Explorer filters: frontend/src/pages/ExplorerFilters.js (FILTERS).
- Assistant behaviour and model: backend/app/assistant.py; GET /api/assistant/status on the live site
  gives {"mode": "generated", "model": "claude-opus-5-5"} (15 Nov 2026).
- Stored summaries reviewed: backend/data/summaries/*.json (reviewed_by Aminpatra, #63).
- Model numbers: backend/data/flex_model/results.json (held_out, cross_validation.scores,
  chance_check, limitations). The pipeline test test_committed_results_are_what_this_code_produces
  retrained the model on 15 Nov 2026 and matched these numbers (submission/test_report.md).
  Oxygen: shap.by_end lists oxygen first for Extinction (mean |SHAP| 0.207) and Disruption;
  for Completion droplet_diameter is first. Chance check: chance_check (macro_f1 0.537 on the
  training days, shuffled_mean 0.319, 40 shuffles, p_value 0.024 = smallest_possible_p).
- Explorer filters: frontend/src/pages/ExplorerFilters.js FILTERS (platform, fuel phase,
  fire-safety role, gravity, data in FLARE).
- Team names and order: PRODUCT.md "Brand Commitments".
-->
