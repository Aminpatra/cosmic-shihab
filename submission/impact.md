# Why it matters

## The stakes

A fire in a spacecraft or a habitat is one the crew cannot walk away from, and the people who
design those spaces work from the evidence NASA has gathered on how flames behave without gravity.
That evidence exists: NASA's PSI repository publishes 24 combustion investigations, most of them
flown on the International Space Station. But it is spread across records, tables in different
layouts and units, and thousands of documents, and the question a designer actually has, "which of
these tests looks like my cabin?", has no direct answer in it. FLARE gives it one.

## What FLARE changes

- **From a scenario to the evidence in one step.** A researcher or mission planner describes the
  conditions they care about and gets NASA's investigations ranked by how closely their actual
  tests match, with the closest tests, NASA's own column names and units, and a link to each
  source. What took reading 24 records and their files becomes a ranked, explained list.
- **The gaps become visible.** Every result says which conditions NASA never recorded, the
  coverage matrix shows which conditions each table holds, and a lunar or Martian scenario is told
  plainly that no NASA test ran in partial gravity. Knowing where the evidence is thin is as useful
  to a designer as knowing where it is thick, and it points the next experiment at the gap.
- **AI that can be checked.** The assistant answers from NASA's sources only and ties each sourced
  sentence to the words it rests on, so a reader can verify it instead of trusting it.
- **Honest about what the data cannot say.** FLARE never turns a relevance score into a safety
  verdict and never fills a missing value, which is what makes it usable for research.

## Who it helps

- **Combustion and fire-safety researchers,** who need depth and traceability: the exact tests,
  units and documents behind every number.
- **Mission planners and engineers** working on habitats, rovers and spacecraft cabins, who start
  from a scenario and need a short, explained list.
- **Students and teachers,** the challenge's own audience, who can explore real NASA microgravity
  experiments without knowing PSI's file layout.

## Beyond spaceflight

Microgravity removes buoyancy, the flow that shapes every flame on Earth, so these experiments
isolate how combustion itself works. The same investigations inform fire science on the ground,
and FLARE makes them easier to reach for anyone who studies it.

## Built to last

FLARE uses only NASA's public data, keeps every value as NASA published it, and is open source.
When PSI adds investigations, such as the partial-gravity results expected from LUCI and FM2, the
pipeline can read them the same way, and once their tables are processed, the ranking and
comparison work on them without changes.

<!--
For the team (not for the form). Draft for the impact part of the package (and the "why it
matters" part of the High-Level Summary), issue #15. No numbers here beyond those already sourced:
- 24 investigations, most on the ISS (16 of 24): submission/problem.md and datasets.md.
- Audience: the challenge page as quoted in submission/problem.md ("Who it affects").
- Microgravity and buoyancy: submission/problem.md.
- LUCI and FM2: master prompt section 5, from the challenge page.
- "the pipeline can read them the same way": pipeline/harvest.py and psi_client.py read PSI's web
  service by accession (submission/architecture.md); a new investigation's table still has to be
  processed and tagged (pipeline/process_tables.py, research/investigation_tags.csv), hence "once
  their tables are processed". Do not change this to "automatically".
- No users, testimonials or adoption numbers exist; none are claimed (CLAUDE.md).
-->
