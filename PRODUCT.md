# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

React + Vite + Recharts + Lucide icons, plain CSS (no component kit). Python FastAPI + pandas +
SQLite (or processed JSON/CSV) backend. Deploy on Vercel. Animation library: Motion.

## Users

**Primary: combustion and fire-safety researchers.** They come to find which NASA microgravity
combustion investigations bear on a question, check the exact conditions, units and provenance,
and see what is missing. When needs conflict, their need for depth and traceability wins.

**Secondary: mission planners** choosing a scenario (spacecraft, lunar habitat, Mars habitat,
custom) and wanting a ranked, explained shortlist of relevant investigations.

**Also present: NASA Space Apps 2026 judges**, who see FLARE in a short demo. Their need is a
constraint, not the goal: within the first few seconds of the home screen they must understand
what FLARE does.

## Product Purpose

NASA's microgravity combustion research is spread across investigations, datasets, technical
documents and publications in the Physical Sciences Informatics (PSI) repository. FLARE (Fire
Learning, Analysis & Research Explorer) makes it explorable and comparable: browse investigations,
pick a scenario and its conditions, get a transparent ranking of relevant investigations, compare
conditions and findings, see research gaps, and ask a source-grounded assistant.

Success: a researcher can go from a scenario to the relevant investigations and their original
sources, and can say exactly why each one ranked where it did and what data it lacks.

Built for the NASA Space Apps 2026 "Flame in Freefall" challenge.

## Positioning

An explainable relevance ranking built only on real PSI data. Every result shows its score, the
conditions that match, the ones that differ, the information that is unavailable, and the
variables used, with links back to the NASA source. It is a research exploration and comparison
tool, never a fire predictor or safety assessment.

## Operating Context

- Used mainly on laptops; demoed on a projector during judging. Phones (375px) must work but are
  not the main scene.
- Pages planned in the brief: Home/Overview, NASA Research Explorer, Scenario Explorer,
  Investigation Comparison, Data Visualization, SI Research Assistant, Sources and Methodology.
- Researchers cross-check against PSI investigation pages, data organization documents and
  publications.

## Capabilities and Constraints

- Must not claim to predict real fires, certify fire safety, or prove an environment is safe. A
  relevance score is not a safety assessment, and the UI says so.
- Microgravity is not lunar or Martian gravity: when a scenario uses partial gravity, the UI states
  that the evidence comes from microgravity.
- Never assume an investigation has oxygen, pressure, airflow or any other variable. Missing
  information is shown as missing, never filled in.
- Preserve original units; show conversions transparently. Distinguish measured, calculated,
  assumed and missing values.
- Scenario fields may be left unspecified; FLARE never invents values for them.
- Ranking weights are configurable and documented. The SI assistant is separate from the ranking
  and cannot change it.
- The assistant cites sources, separates source findings from its own explanation, and says when
  it can't find an answer. It needs a working fallback when no API key is present.
- Terminology: PSI, investigation, run, scenario, relevance score.
- Decided 2026-11-14: Claude Opus 5.5 powers the assistant. Proposed in `docs/DATA_PLAN.md`:
  which investigations make the final dataset.

## Brand Commitments

- Name: FLARE, "Fire Learning, Analysis & Research Explorer".
- NASA Space Apps brand guidelines apply: their palette, Fira Sans / Overpass, Neon Yellow as an
  accent only, contrast at least 4.5:1, and no NASA insignia.
- The brief asks for the feel of a professional scientific research platform, dark and
  high-contrast, with no excessive animation or decoration.
- Team: **Cosmic Shihab**. Team logo: a shooting star crossing a ring, four-point stars and the
  "COSMIC SHIHAB" wordmark, as transparent PNGs in `brand/`: `cosmic-shihab-logo-white.png` for
  dark backgrounds (the site) and `cosmic-shihab-logo-black.png` for light ones. The team's own
  work, not made with SI. It is the team's mark, not a FLARE product logo; FLARE has no separate
  mark yet.
- Team members to credit on the site, in this order: Amin Mohamed Amin, Gheath Wahab, Mohammed
  Al-julandani, Samin Rezaei, Rahaf Abubaker Mustafa Mubarak, Ruayma Khair Mohammed Albalushi.

## Evidence on Hand

Real NASA PSI files in `datasets/`:
- `PSI-25_Experimental table_BASS-II.csv`
- `BASS-II Test Matrix by PI Final.xlsx`
- `PSI-69_Experimental table_FLEX.csv`
- `PSI-159_Raw Data_Final ACME Chamber Calculator - 2021-03-09 to 2021-10-21.xlsx`

No users, testimonials, benchmarks or accuracy figures exist yet. None may be invented.

## Product Principles

1. **Traceable or absent.** Every number links to its NASA source; what isn't in the data is shown
   as missing, never estimated silently.
2. **Explain the ranking.** A score without its reasons is not shown.
3. **Relevance, not safety.** FLARE helps people find and compare research; it never tells them an
   environment is safe.
4. **Depth for researchers, clarity at the door.** The first screen explains FLARE in seconds;
   everything after serves people who check details.
5. **A smaller working tool beats a larger unfinished one.**

## Accessibility & Inclusion

Text contrast at least 4.5:1 (NASA Space Apps brand rule). Must stay legible on a projector.
Respect reduced-motion preferences.
