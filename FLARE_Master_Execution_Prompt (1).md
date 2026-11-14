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

------------------------------------------------------------------------

## 2. EXECUTION RULES

Follow these rules throughout the project:

-   Execute tasks directly instead of giving me a list of instructions.
-   Work in small, organized phases.
-   Show me what you are doing and what has been completed.
-   Do not stop after creating a plan. Start executing it.
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
-   Do not ask me questions unless a decision or missing access
    genuinely blocks execution. Make sensible technical decisions and
    explain them.
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

------------------------------------------------------------------------

## 6. PHASE FOUR --- BUILD THE INTERACTIVE WEB APPLICATION

Build FLARE as a polished, responsive web application.

### Recommended technology

**Frontend:** - React - Vite - Modern CSS - Recharts or another suitable
charting library - Lucide icons

**Backend:** - Python - FastAPI - Pandas - NumPy - Appropriate
scientific data-processing libraries

**Database:** - Start with a structured local database or processed
JSON/CSV files. - Use SQLite or another suitable database if needed. -
Avoid unnecessary infrastructure.

Choose a practical architecture and explain it briefly before
implementation.

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

Create:

-   `test_report.md`
-   `known_limitations.md`
-   `methodology.md`

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

------------------------------------------------------------------------

## 10. EXECUTION ORDER AND PRIORITIES

Follow this order:

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

------------------------------------------------------------------------

## 11. HOW TO WORK WITH ME

I am a student participating in NASA Space Apps. I understand AI and
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

Maintain a `PROJECT_STATUS.md` file and update it as work progresses.

------------------------------------------------------------------------

## 12. START EXECUTING NOW

Begin with the following actions:

1.  Inspect the current working directory and available tools.
2.  Check whether a project already exists. Preserve useful existing
    work.
3.  Create an organized project structure if needed.
4.  Open and investigate the official NASA PSI sources.
5.  Identify the first accessible combustion investigation and its
    actual downloadable files.
6.  Download and inspect the first manageable dataset and its data
    organization document.
7.  Report the actual variables and units you find.
8.  Begin building the data-processing pipeline.

**Do not stop after giving me a plan. Start with Phase One and execute
the first real task immediately.**

Your ultimate objective is to deliver a functional, tested,
scientifically responsible FLARE application that demonstrates a
meaningful use of NASA's Physical Sciences Informatics data for the
Flame in Freefall challenge.
