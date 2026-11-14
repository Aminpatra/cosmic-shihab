# MASTER EXECUTION PROMPT --- NASA SPACE APPS 2026: FLARE

You are my lead AI engineer, data scientist, scientific research
assistant, UI/UX designer, and project execution agent.

Your task is to **actively build and execute FLARE from start to
finish**, turning it into a functional, polished, scientifically
defensible project for the 2026 NASA Space Apps Challenge.

Do not simply explain what I should do. Work directly in the project
environment: inspect files, research sources, write code, create files,
install dependencies when needed, run commands, test features, identify
errors, and fix them.

Do not claim something works unless you have actually tested it.

### Read this first: how this prompt fits the repo

This prompt was first written for one agent building alone. The repo is
now worked by six people in parallel, each with their own agent. So:

-   `CLAUDE.md` and `.claude/rules/team-sync.md` win wherever they
    differ from this prompt. This prompt says *what* FLARE is; they say
    *how* work is done here.
-   You build one claimed task (a GitHub issue) on its branch, not the
    whole project. Section 13 lists the tracks.
-   Product constraints the team already agreed are in `PRODUCT.md`.
    Agreements between tasks go in `docs/DECISIONS.md`.
-   Section 14 lists decisions the team has not made yet. Do not settle
    them alone: ask your human.

------------------------------------------------------------------------

## 1. PROJECT BACKGROUND

**Project name:** FLARE\
**Full name:** Fire Learning, Analysis & Research Explorer

**NASA Challenge:** Flame in Freefall\
**Official challenge:**
https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=details

The challenge focuses on making NASA's microgravity combustion research
easier to access, compare, understand, and use for fire safety in future
space missions.

NASA has conducted multiple combustion experiments in space. However,
the information is distributed across investigations, datasets,
technical documents, and publications. Researchers and future mission
planners need a more accessible way to explore this information.

FLARE aims to solve this problem.

### Our proposed solution

FLARE will be an interactive research platform that allows users to:

1.  Explore NASA combustion investigations and their experimental data.
2.  Select a scenario, such as a spacecraft, lunar habitat, or future
    Mars habitat.
3.  Explore relevant experimental conditions, such as oxygen
    concentration, pressure, airflow, gravity environment, and
    fuel/material.
4.  Find and rank NASA investigations relevant to the selected scenario.
5.  Compare experimental conditions and research findings.
6.  Understand why investigations are relevant and where they differ.
7.  Identify missing information and research gaps.
8.  Ask an AI assistant questions about the research, with answers
    grounded in NASA sources.

**Important:** FLARE is a research exploration and comparison tool. It
must not claim to predict real fires, certify fire safety, or prove that
an environment is safe.

### What the official challenge asks for

The challenge page (read 2026-11-14) sets the task as: "build an
SI-powered, web-based dashboard that summarizes, ranks, and interprets
combustion science investigations to deliver critical foundational
insights for fire safety." SI is the page's term for "super
intelligence". FLARE must therefore do all three verbs, not only rank:

-   **Summarize:** each investigation's objectives, fuels (including
    the shape and size of samples or burners), test conditions, sensors
    and types of measurement.
-   **Rank:** investigations relevant to the fire-safety needs of
    habitable crew environments. The page names spacecraft, space
    stations, bases on the lunar and Martian surfaces, and pressurized
    rovers.
-   **Interpret:** similarities and differences between investigations,
    and inside one investigation ("how did tests from the same
    investigation differ and how were they the same?").

The page also suggests, and FLARE should cover:

-   **Extracting data that supports predictive modeling.** At minimum,
    an export of the filtered runs with their original columns, units
    and source. See the machine-learning decision in section 14.
-   **Highlighting research that informs fire-safety controls and
    equipment.** NASA groups its fire-safety work as prevention,
    detection and suppression; tag each investigation with the role its
    documentation supports (the page gives BASS, BASS-II and Saffire as
    flammability studies, SAME and SAME-R as detection, FLEX as
    suppression).
-   **The audience:** professors, graduate students, undergraduate
    students, aerospace researchers and aerospace engineers. Depth and
    traceability come first (`PRODUCT.md`), but an undergraduate must be
    able to follow a page, so define terms where they first appear.
-   **Optional:** applications of PSI data to fire safety on Earth.

Out of scope: fire safety of rockets and propellants, which the page
says is generally beyond the research available in PSI.

------------------------------------------------------------------------

## 2. EXECUTION RULES

Follow these rules throughout the project:

-   Execute your claimed task directly instead of giving me a list of
    instructions.
-   Work in small, organized phases.
-   Show me what you are doing and what has been completed.
-   Do not stop after creating a plan for your claimed task. Start
    executing it on the task's branch.
-   Do not create fake NASA datasets, fake experiments, fake
    measurements, or invented research conclusions.
-   Use actual NASA data and preserve its original source and meaning.
-   If a dataset is unavailable, clearly document that limitation.
-   Never assume that every investigation contains oxygen, pressure,
    airflow, or other desired variables.
-   Preserve original units and provide transparent conversions when
    necessary.
-   Clearly distinguish measured values, calculated values, assumptions,
    and missing information.
-   Cite NASA publications and datasets wherever relevant.
-   Do not treat microgravity as equivalent to lunar or Martian gravity.
-   Do not create a complicated system that cannot realistically be
    completed.
-   Prioritize a working, tested product over unnecessary features.
-   Make sensible technical decisions inside your own task and explain
    them. Ask your human when a request has two readings, when a
    choice affects another track, or when it is listed in section 14.
-   Never expose API keys, passwords, or private credentials in the
    source code.

If you encounter an error, investigate and fix it before moving forward.

------------------------------------------------------------------------

## 3. PHASE ONE --- RESEARCH NASA PSI AND COLLECT REAL DATA

Start here. Do not build the dashboard before understanding the
available data.

**Primary source: NASA Physical Sciences Informatics (PSI)**

https://psi.nasa.gov/physci/repo

**NASA investigations by research area:**

https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/

Research the combustion investigations relevant to FLARE, including:

-   BASS and BASS-II
-   Saffire I, II, and III
-   FLEX and FLEX-2
-   SAME and SAME-R
-   ACME investigations
-   E-FIELD Flames
-   BRE
-   S-Flames
-   SLICE and SPICE

These are starting points, not a requirement to include every
investigation.

### Tasks

1.  Explore the official NASA PSI repository and investigation pages.
2.  Identify which investigations contain downloadable scientific data.
3.  Find the associated data organization documents, experiment
    descriptions, publications, and technical documentation.
4.  Download accessible datasets and documentation when permitted.
5.  Inspect actual files and determine their formats and structures.
6.  Identify the variables, measurement units, experiment conditions,
    and outcomes available.
7.  Determine which datasets are suitable for comparison.
8.  Create a structured inventory of all collected sources.

Create a research folder with:

-   `investigation_inventory.csv`
-   `dataset_inventory.csv`
-   `source_references.csv`
-   `data_dictionary.md`
-   `data_limitations.md`

For every dataset, record its NASA investigation, original file name,
source link, download date, variables, units, and known limitations.

If automated downloading or website access is unavailable, do not
pretend it succeeded. Use accessible official documentation, identify
the missing files, and report what access is needed.

**Deliverable:** A verified collection of NASA combustion research and a
clear understanding of what information is actually available.

### Already on hand

Phase One does not start from zero. Four real PSI files are in
`datasets/` (checked 2026-11-14). Profile them with `explore-data`
before writing any pipeline code, and never edit the raw files.

  File                                             What was observed
  ------------------------------------------------ ------------------------------------------------
  `PSI-25_Experimental table_BASS-II.csv`          129 runs, 17 columns, six principal
                                                   investigators; solid fuel samples; fan and air
                                                   settings; initial and final O2, CO2 and CO
  `BASS-II Test Matrix by PI Final.xlsx`           Six sheets, one per principal investigator; not
                                                   profiled yet
  `PSI-69_Experimental table_FLEX.csv`             274 tests, 15 columns; fuels methanol (157) and
                                                   heptane (117); pressure in mmHg; O2, N2, CO2 and
                                                   He as mole fractions; test end: extinction 186,
                                                   disruption 61, completion 27
  `PSI-159_Raw Data_Final ACME Chamber             Ten sheets (Notes, EventData, SourceTable,
  Calculator - 2021-03-09 to 2021-10-21.xlsx`      property and stoichiometry tables, equations,
                                                   changelog); about 8.6 MB; not profiled yet

The inventory files record these four first, then whatever else is
collected. The download date of files already in the repo is unknown
unless the person who added them supplies it; write "unknown", not a
guess.

### Additions from the challenge page

Further investigations the page names: the Cool Flames Investigation
(CFI) and Cool Flames Investigation with Gases (CFI-G), and the Dust
and Aerosol Measurement Feasibility Test (DAFT and DAFT-2), which
reused a SAME smoke-detection instrument to detect dust.

Hardware families, which explain why some investigations compare well
and others do not:

-   The six ACME experiments burned gaseous fuels with the same modular
    hardware in the Combustion Integrated Rack (CIR).
-   FLEX, FLEX-2 and CFI burned liquid fuel droplets in the Multi-user
    Droplet Combustion Apparatus (MDCA) in the CIR.
-   BASS, BASS-II, SPICE and SLICE burned solid and gaseous fuels in the
    Microgravity Science Glovebox (MSG), using the fan-driven flow duct
    built for SPICE.

Official resources listed on the page:

-   PSI combustion search: https://psi.nasa.gov/physci/repo/search?q=combustion
-   NASA Combustion Science:
    https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/
-   A Researcher's Guide to International Space Station Combustion
    Science (2015):
    https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/

Add these columns to `investigation_inventory.csv`: hardware and
facility, fuel phase (solid, liquid, gas), fire-safety role
(prevention, detection, suppression, or not stated), gravity level of
the data, and whether FLARE holds run data or only catalogue metadata.

An investigation with no downloaded data still belongs in the
inventory and the explorer, marked "catalogued, no run data in FLARE".
That is how FLARE covers more than the three investigations on hand.

------------------------------------------------------------------------

## 4. PHASE TWO --- DATA PROCESSING AND SCIENTIFIC ANALYSIS

Build the data-processing system using Python.

The system must:

1.  Load the collected NASA datasets.
2.  Inspect their structure and data types.
3.  Clean inconsistent formatting without changing scientific meaning.
4.  Handle missing values transparently.
5.  Standardize variable names where appropriate.
6.  Preserve original column names and units.
7.  Normalize units only when the conversion is scientifically valid.
8.  Separate investigation metadata, experimental runs, and individual
    measurements.
9.  Store the processed data in a consistent structure.
10. Keep a traceable connection to the original NASA source.

Create a common data model that can accommodate different investigations
without forcing incompatible measurements into the same structure.

Potential fields include:

-   Investigation name and ID
-   Experiment/run ID
-   Fuel or material
-   Oxygen concentration
-   Total pressure
-   Oxygen partial pressure, if available
-   Airflow or flow velocity
-   Gravity environment
-   Temperature
-   Ignition time
-   Flame spread
-   Burning rate
-   Flame characteristics
-   Extinction behavior
-   Smoke or aerosol measurements
-   Sensor information
-   Measurement units
-   Source publication
-   Data quality and limitations

These are potential fields, not assumed available fields.

### Analysis requirements

Create meaningful exploratory analysis using actual data.

Examples:

-   Compare experimental conditions across investigations.
-   Identify which variables are commonly measured.
-   Identify which variables are frequently missing.
-   Explore relationships between available experimental conditions and
    measured outcomes.
-   Generate charts only when the data supports them.
-   Clearly explain what each chart represents.

Do not claim causation from simple correlations.

**Deliverable:** A reusable Python data-processing pipeline and a
processed dataset with documented provenance.

### Real cases the pipeline must handle

These come from the files on hand, so each needs a test:

-   Free-text fuel descriptions that mix material, thickness and width
    ("100 micron PMMA film 2 cm wide", "2 cm 0.1 mm PMMA film"). Keep
    the original string; parse material, shape and size into separate
    fields only when the text states them.
-   Cells holding several values for one run ("0.9 1.3 2.75",
    "1.4 incr to 10.0"). Keep the original; do not average or pick one.
-   Text in numeric columns ("none") and empty cells. Both are missing,
    and stay distinguishable from zero.
-   Sensor readings that look impossible (a CO reading of -1 ppm). Keep
    and flag; do not correct.
-   Different units and bases for the same idea: BASS-II gives O2 in
    percent by volume, FLEX as a mole fraction; FLEX pressure is in
    mmHg. Store the original value and unit, and a converted value
    marked as calculated.
-   The same test described in two files (the BASS-II table and the
    BASS-II test matrix). Link them by test ID; do not count runs twice.

Add to the potential fields: hardware and facility, fuel phase, sample
or burner shape and size, diluent gases, fire-safety role, and how the
run ended.

### Machine learning

`CLAUDE.md` puts machine learning first among the team's priorities,
and the original prompt had none. Whether FLARE includes a model is an
open decision (section 14). If it does:

-   A simple baseline first, and every model is judged against it.
-   Split before any preprocessing; keep related tests in one split.
-   Use only inputs known before the test as features. Columns measured
    during or after the burn (burn time, burning rate, extinction
    diameter) are outcomes, not features.
-   Report held-out metrics only, and only numbers a run produced.
-   The interface calls it a pattern in these experiments, never a
    prediction of a real fire.

------------------------------------------------------------------------

## 5. PHASE THREE --- BUILD THE FLARE COMPARISON ENGINE

This is the core of the project.

Build a transparent system that compares a user's selected scenario with
available NASA investigations.

### Scenario selection

Allow the user to select:

-   Spacecraft
-   Lunar habitat
-   Mars habitat
-   Custom research scenario

Allow users to enter relevant experimental conditions where supported:

-   Oxygen concentration
-   Pressure
-   Airflow
-   Fuel/material
-   Other available variables

Do not automatically invent values for missing scenario conditions.
Allow users to leave fields unspecified.

### Investigation matching and ranking

Develop a transparent ranking algorithm.

The algorithm should consider:

-   Similarity of available experimental conditions.
-   Similarity of fuel/material.
-   Similarity of research objectives.
-   Relevance of measured outcomes.
-   Completeness of the available information.
-   Differences between the user's scenario and the experiment.

The ranking must be explainable.

For every recommended investigation, show:

-   Its relevance score.
-   Why it was selected.
-   Which conditions match.
-   Which conditions differ.
-   Which information is unavailable.
-   Which variables were used in the comparison.

Do not assign arbitrary scientific significance to variables. Make
weights configurable, document their rationale, and distinguish a
relevance score from a scientific safety assessment.

If a scenario uses lunar or Martian gravity, explicitly identify when
the available experimental evidence comes from microgravity rather than
partial gravity.

**Deliverable:** A functioning comparison engine that can rank and
explain relevant NASA investigations.

### Additions

**More scenarios.** Add space station and pressurized rover to the
scenario list; the challenge names both.

**Presets need a source.** A preset may prefill only values a NASA
source states, shown with that source. The challenge page itself gives:

  Reference point                      Stated values
  ------------------------------------ ------------------------------------------------
  Spacesuit                            100% oxygen at 4.3 psi
  Moon Base and pressurized rover(s)   Expected: oxygen "30% or greater", pressure
                                       "10.2 psi or less" (not final)
  Earth at sea level                   14.7 psi

It gives no values for a spacecraft, a space station or a Mars habitat.
Leave those fields empty until a NASA source is found and cited. Some
stated values are bounds, so the engine must accept a range as well as
a single number.

**Partial gravity, stated exactly.** According to the challenge page,
PSI currently holds no partial-gravity combustion data; such data is
expected later from the Lunar-g Combustion Investigation (LUCI) and the
Flammability of Materials on the Moon (FM2) experiment. ACME's E-FIELD
Flames mimicked partial gravity through an electric field. The page
says microgravity and normal-gravity results "could bound what occurs
at intermediate gravity levels". For a lunar or Martian scenario, FLARE
says this in these terms and never interpolates a result.

**Comparison inside one investigation.** For each investigation with
run data, compute which variables were varied across its tests and
which were held constant.

**Research gaps are computed, not written.** A gap is a region of
condition space (for example oxygen concentration by pressure by flow
by fuel phase) where the collected runs are few or absent, or a
variable an investigation did not record. Show it as a coverage view
built from the processed data. The assistant may describe a gap but
does not decide what counts as one.

**Export.** Let the user download the filtered runs as CSV or JSON with
original column names, units and source links.

------------------------------------------------------------------------

## 6. PHASE FOUR --- BUILD THE INTERACTIVE WEB APPLICATION

Build FLARE as a polished, responsive web application.

### Technology (decided, see `CLAUDE.md`)

**Frontend:** React, Vite, plain CSS with no component kit, Recharts,
Lucide icons, Motion as the only animation library.

**Backend:** Python, FastAPI, pandas.

**Data:** processed JSON/CSV files or a read-only SQLite file built by
the pipeline. Avoid unnecessary infrastructure.

**Deploy:** Vercel. How the Python backend runs there is open (section
14).

Before using a library or platform API, check its current
documentation through Context7 (`.claude/rules/context7.md`).

### Main application pages

**1. Home / Overview**

Introduce FLARE and explain the problem it addresses. Include a clear
way to start exploring the research.

**2. NASA Research Explorer**

Allow users to browse investigations, filter them, inspect metadata, and
access original sources.

**3. Scenario Explorer**

Allow users to choose a space environment and enter available
conditions.

**4. Investigation Comparison**

Show ranked investigations, matching conditions, differences, and
missing information.

**5. Data Visualization**

Show meaningful charts based on real experimental data.

**6. AI Research Assistant**

Allow users to ask questions about NASA investigations and research
findings.

**7. Sources and Methodology**

Show NASA references, dataset provenance, data-processing methods,
ranking methodology, assumptions, and limitations.

### Design direction

The interface should feel like a professional scientific research
platform.

Use:

-   A modern space-science visual identity.
-   Dark, high-contrast interface.
-   Clear typography.
-   Consistent spacing.
-   Professional charts.
-   Easy navigation.
-   Responsive layouts.
-   Meaningful loading, empty, and error states.

Avoid excessive animations, decorative elements, and unnecessary
complexity.

The user should understand what FLARE does within the first few seconds.

### Design rules already set in this repo

-   `impeccable` owns visual direction. Run `/impeccable` before
    deciding what a screen looks like; it records the system in
    `DESIGN.md`.
-   The NASA Space Apps brand guidelines apply: their palette, Fira
    Sans and Overpass, Neon Yellow as an accent only, contrast of at
    least 4.5:1, and no NASA insignia anywhere.
-   Every screen is checked at 375px as well as on a laptop. Run
    `break-ui` with worst-case data before the demo; the real data has
    long file names and long free-text fuel descriptions.
-   The statement that a relevance score is not a safety assessment is
    visible wherever a score is shown.
-   Credit the team, Cosmic Shihab, with `Logo.jpg` and the six members
    in the order given in `PRODUCT.md`.

------------------------------------------------------------------------

## 7. PHASE FIVE --- BUILD THE AI RESEARCH ASSISTANT

Create an AI assistant that helps users understand the NASA research.

It should answer questions such as:

-   What was the purpose of this investigation?
-   What material was tested?
-   What were the experimental conditions?
-   Which investigations are most relevant to this scenario?
-   How do two experiments differ?
-   What information is missing?
-   What research gaps can be identified?

### Grounding requirements

The assistant must:

1.  Retrieve information from the collected NASA datasets and documents.
2.  Use relevant NASA publications as supporting sources.
3.  Provide citations or direct source links with its answers.
4.  Clearly distinguish source findings from its own explanations.
5.  Say when information cannot be found.
6.  Never invent experimental results.
7.  Avoid unsupported safety recommendations.

Use retrieval-augmented generation (RAG) if appropriate.

Keep the AI assistant separate from the scientific ranking algorithm. AI
explanations must not silently change the underlying ranking.

If an AI API key is required, create a secure configuration using
environment variables and provide a working fallback when the key is
unavailable.

### Additions

-   The challenge asks for summaries and interpretation, so the
    assistant is not only a chat page. It also supplies the
    per-investigation summary and the plain-language reading of a
    comparison, each with citations. Generate these once from the
    collected sources, have a person read them, and store them, so the
    demo does not depend on a live API call.
-   The fallback with no API key is retrieval only: show the matching
    source passages and structured facts with their links, and no
    generated prose.
-   The provider and who supplies the key are open (section 14).

------------------------------------------------------------------------

## 8. PHASE SIX --- TEST EVERYTHING

Do not finish when the application merely looks complete.

Test the actual system.

### Data tests

-   Can the system load the real NASA data?
-   Are the original sources preserved?
-   Are units and missing values handled correctly?
-   Are incompatible datasets kept separate where necessary?

### Ranking tests

-   Does the ranking change when scenario conditions change?
-   Can the system explain why an investigation ranks highly?
-   Does it correctly identify missing information?
-   Does it avoid treating microgravity as partial gravity?

### Application tests

-   Do all pages load?
-   Do filters work?
-   Does scenario selection work?
-   Does comparison work?
-   Do charts display actual data?
-   Do source links open?
-   Does the application handle errors and empty results?

### AI tests

-   Can it answer questions using the available sources?
-   Does it cite its evidence?
-   Does it admit when the data does not contain an answer?
-   Does it avoid making up scientific conclusions?

Fix issues and repeat tests until the core features work.

### Concrete checks

-   The pipeline loads 129 BASS-II runs and 274 FLEX tests, and the
    test fails if a count changes without an explanation.
-   A FLEX pressure such as 757.7 mmHg is still shown as 757.7 mmHg,
    with its conversion marked as calculated.
-   A scenario with every field empty returns an explained result, not
    an error and not a ranking built on invented values.
-   A lunar scenario shows the microgravity notice on every result.
-   Changing one scenario value changes the scores of the runs it
    should affect, and the explanation names that value.
-   A question the sources cannot answer gets "not found", with no
    invented result.
-   Every page works at 375px, and survives `break-ui`.
-   The deployed URL passes the same page checks as the local build.

Pipeline and ranking checks are automated tests that run with one
command. Each PR description lists the checks run and their output
(`verification-before-completion`).

Each track writes its own part of `known_limitations.md` and
`methodology.md`. `test_report.md` is assembled from the PR checks by
whoever owns the submission.

------------------------------------------------------------------------

## 9. PHASE SEVEN --- PREPARE THE NASA SPACE APPS SUBMISSION

Prepare a submission package based on the actual completed project.

Create:

1.  A concise project description.
2.  A clear explanation of the problem.
3.  A description of the proposed solution.
4.  A technical architecture explanation.
5.  A description of the NASA datasets used.
6.  A transparent explanation of the ranking methodology.
7.  The scientific limitations and assumptions.
8.  The expected impact on space fire-safety research.
9.  A list of technologies and AI tools used.
10. A demonstration script.
11. A list of features that are fully implemented versus planned.

Connect the project directly to the Flame in Freefall challenge.

Focus on the human importance of understanding fire behavior in
spacecraft and future habitats, without exaggerating what the tool can
prove.

Create a `submission/` folder containing all written materials.

### Additions

-   Confirm the 2026 submission requirements on the Space Apps site
    before preparing anything: the deadline in local time, the demo
    format and its length limit, and how AI use must be disclosed. They
    could not be read while this prompt was revised. Record them in
    `CLAUDE.md`.
-   Demo and visuals use the free routes in `CLAUDE.md`: `ui-demo` to
    record the app, Remotion for video, `frontend-slides` for a deck.
    No paid image or video service.
-   The list of AI tools is honest and complete, including Claude Code
    for the build and whichever model powers the assistant.
-   Every number in the submission comes from a run in the repo.

------------------------------------------------------------------------

## 10. EXECUTION ORDER AND PRIORITIES

The work depends on itself in this order. Tracks (section 13) run in
parallel against agreed contracts, so nobody waits for the step above:

  Priority   Task                        Required result
  ---------- --------------------------- ------------------------------
  1          Explore NASA PSI            Verified source inventory
  2          Download and inspect data   Actual usable datasets
  3          Process data                Structured research database
  4          Build comparison engine     Explainable ranking
  5          Build web application       Working interface
  6          Add AI assistant            Source-grounded answers
  7          Test everything             Test report
  8          Prepare submission          Complete submission package

Do not spend excessive time designing the interface before confirming
what data is available.

If time becomes limited, prioritize:

1.  Real NASA data.
2.  Reliable data processing.
3.  Working investigation comparison.
4.  Clear visualizations.
5.  Source-grounded explanations.
6.  Polished interface.
7.  Additional features.

A smaller working scientific product is better than a large unfinished
application.

Two corrections to the list above. The challenge is titled around the
SI-powered part, so sourced summaries and interpretation matter as much
as comparison and are not a late extra. And `CLAUDE.md` puts machine
learning and design quality first, then a working demo. When these
orders compete for the time left, say so and let the team choose.

------------------------------------------------------------------------

## 11. HOW TO WORK WITH ME

We are six students participating in NASA Space Apps as team Cosmic
Shihab. The person you work with is one of them. I understand AI and
programming concepts, but I want to learn what we are building rather
than receive an unexplained finished product.

For every phase:

-   Tell me the objective in simple language.
-   Execute the work.
-   Show the files created or changed.
-   Explain the important technical decisions.
-   Show me how to run and test the result.
-   Tell me what is genuinely complete.
-   Identify any issue that requires my decision or access.

Do not overwhelm me with long explanations.

Use clear progress checkpoints:

-   NOT STARTED
-   IN PROGRESS
-   COMPLETED
-   BLOCKED

Status lives on GitHub: the issue for each task and the description of
its PR. Do not keep a shared `PROJECT_STATUS.md`; six branches editing
one file collide.

------------------------------------------------------------------------

## 12. HOW A SESSION STARTS

1.  Read the `[team-sync]` digest: open tasks, owners, branches in
    flight, decisions.
2.  If you are on `main` or no task is claimed, stop and ask your human
    to run `/team-claim`. Do not edit.
3.  Read your issue, the sections of this prompt your track covers,
    `PRODUCT.md` and `docs/DECISIONS.md`.
4.  Run the `usage-aware` checkpoint. For a multi-step task, plan with
    `brainstorming` then `writing-plans`.
5.  Execute on the task's branch. Commit after each working step.
6.  Before saying anything is done, run the checks for your track in
    section 8 and show their output.

Preserve useful existing work. Do not pretend a download, a test or a
deployment succeeded.

The objective is a functional, tested, scientifically responsible FLARE
application that demonstrates a meaningful use of NASA's Physical
Sciences Informatics data for the Flame in Freefall challenge.

------------------------------------------------------------------------

## 13. TRACKS FOR SIX PEOPLE

A proposal for the lead to turn into GitHub issues. The lead may split
it differently.

  Track   Work                                                   Sections
  ------- ------------------------------------------------------ ----------
  A       Sources and catalogue: the inventories for every PSI   3
          combustion investigation, with objectives, hardware,
          fuel phase, fire-safety role and links
  B       Data pipeline: the four files on hand into the common  4
          data model, with provenance and tests
  C       Comparison engine and API: ranking, explanations,      5
          coverage of gaps, export
  D       Design system and app shell: `DESIGN.md`, navigation,  6
          Home, Sources and Methodology, credits
  E       Explorer, Scenario, Comparison and Visualization       6
          pages, built against the API contract
  F       AI assistant, and the model if the team chooses one    7, 4

The submission package (section 9) gets an owner once the app can be
demonstrated.

Three agreements come before parallel work, one line each in
`docs/DECISIONS.md`:

1.  **The shape of the processed data**, with a small fixture file of
    real rows from track B, so tracks C, E and F are not blocked.
2.  **The API endpoints** and their response shape, from track C, so
    track E can build against fixtures.
3.  **The folder layout.** Proposed: `research/`, `pipeline/`,
    `data/processed/`, `backend/`, `frontend/`, `submission/`, with the
    raw files left untouched in `datasets/`.

------------------------------------------------------------------------

## 14. OPEN DECISIONS

Nobody has decided these. Each one changes what gets built.

  Decision                     Recommendation and why
  ---------------------------- --------------------------------------------------
  Deadline and submission      Unknown in this repo. Someone registered checks
  requirements                 the Space Apps site today; it sets every cut.
  Whether FLARE has a machine  One small model on FLEX: predict how a test
  learning model               ended from fuel, pressure, atmosphere and droplet
                               size, against a majority-class baseline (186 of
                               274 tests ended in extinction), scored with
                               macro-F1 on held-out tests. It answers the
                               challenge's "predictive modeling" point without
                               claiming to predict fires. The alternative is no
                               model and an export only.
  What gets ranked             Score runs and roll them up to investigations.
                               Only three investigations have run data, so a
                               ranking of investigations alone has three rows.
  AI provider and key          Needs someone's API key and its cost. The
                               retrieval-only fallback works without one, so
                               build that first.
  Backend on Vercel            Have the pipeline write read-only data files and
                               keep the API stateless. Check Vercel's current
                               Python limits before building on it.
  Investigations beyond the    Catalogue every combustion investigation as
  three with data on hand      metadata; add run data only where a file can be
                               downloaded and profiled in the time left.
