# The problem

A fire aboard a spacecraft is an emergency the crew cannot walk away from. The air, the water and
the equipment that keep people alive share one small, sealed space. As crews go back to the Moon,
on to Mars, and stay longer in orbit, the people who design cabins, habitats and pressurized rovers
need to know how materials catch fire, how flames spread and how they go out when gravity is weak
or absent. Without gravity, hot gas does not rise away from a flame, so fire behaves differently
than it does on Earth, and fire-safety rules written on the ground cannot simply be carried over.

NASA has studied this in space. Its Physical Sciences Informatics (PSI) repository publishes 24
combustion investigations: 16 flown on the International Space Station, three run on uncrewed
Cygnus cargo vehicles after they left the station, and five ground or computational studies.

## Why that knowledge is hard to use

- **It is large and scattered.** The 24 investigations hold 60,866 files, 13.5 TB. Archives and
  video are 99.7% of it. The conditions of each test sit in 22 small experimental tables spread
  across 20 investigations, and the findings sit in 1,926 separate documents.
- **It does not line up.** Every table has its own columns and units. Of the 2,009 test rows, 1,147
  record the oxygen level, 1,001 the pressure and 570 the airflow; the rest leave them out.
- **It is uneven.** The three Saffire spacecraft fire experiments have tables of 4, 15 and 2 rows.
  Four investigations have no table at all. When we profiled the tables, 117 values looked wrong
  (duplicated rows, negative concentrations, chemical formulas that cannot exist, a percentage
  over 100), and FLARE's processing flags only 41 of them.

So a researcher or mission planner who asks "which NASA experiments tested conditions like the ones
in our habitat, and what did they find?" has to open records one by one, read each table's own
headers, convert units by hand, and guess what is missing.

## Who it affects

The challenge names professors, graduate and undergraduate students, aerospace researchers and
aerospace engineers. FLARE is built first for combustion and fire-safety researchers, who need
depth and traceability, and then for mission planners, who start from a scenario (a spacecraft, a
lunar or Martian habitat) and need a short, explained list of the investigations that bear on it.

## What the challenge asks

"Flame in Freefall" asks teams to "build an SI-powered, web-based dashboard that summarizes, ranks,
and interprets combustion science investigations to deliver critical foundational insights for fire
safety" in habitable crew environments: spacecraft, space stations, bases on the lunar and Martian
surfaces, and pressurized rovers. Fire safety of rockets and propellants is outside its scope.

FLARE answers that by ranking and comparing NASA's investigations against a scenario the user
describes. It shows how closely their tested conditions match, never whether a real fire would
start or spread: it does not predict fires, certify safety, or prove an environment is safe.

<!--
For the team (not for the form). Draft for the High-Level Project Summary and the problem part of
the Detailed Project Description, issue #36. Every number, and where it comes from:
- 24 investigations; 16 ISS, 3 Cygnus, 4 computation, 1 ground laboratory and computation:
  backend/data/investigations/*.json, `derived.tags.values.platform` (pipeline/build_catalogue.py,
  tags from research/investigation_tags.csv).
- 60,866 files, 13.5 TB (13.47e12 bytes), 99.7% of bytes in .zip/.ts/.mp4/.avi/.mpg, 1,926
  documents (.pdf/.doc/.docx/.ppt/.pptx/.rtf): backend/data/files.csv, recounted 2026-11-14.
- 22 tables, 20 investigations, 2,009 rows: backend/data/runs/*.json (pipeline/process_tables.py);
  also backend/tests/test_runs.py.
- 1,147 / 1,001 / 570 rows with oxygen / pressure / flow velocity: GET /api/rank/options, run
  2026-11-14 on the committed data.
- Saffire I/II/III rows 4, 15, 2; four investigations without a table (PSI-60, -62, -115, -117):
  backend/data/runs/ and docs/DATA_PLAN.md.
- 117 suspect values, 41 flagged by the pipeline: research/analysis/README.md,
  research/analysis/suspect_values.csv (research/analysis/explore_runs.py, #27). Its rules: 50
  exact duplicate rows, 23 impossible formulas, 15 spelling variants, 13 negative concentrations,
  8 negative flow velocities, 3 leading zeros, 2 percentages over 100, 2 values from flagged cells,
  1 zero or negative pressure.
- Challenge quote and audience: the official challenge page, as quoted in
  FLARE_Master_Execution_Prompt (1).md section 1 (read 2026-11-14).
- "Saffire spacecraft fire experiments": the investigation titles are "Spacecraft Fire Safety
  Experiment-I" and "Spacecraft Fire Experiment-II/-III".
-->
