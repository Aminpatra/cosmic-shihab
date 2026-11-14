# CLAUDE.md

> **FLARE** (Fire Learning, Analysis & Research Explorer), our NASA Space Apps 2026 entry for the
> "Flame in Freefall" challenge: a research tool that lets researchers and mission planners explore,
> compare and rank NASA microgravity combustion investigations (PSI data) for a chosen scenario.
> Stack: React + Vite + Recharts + Lucide (plain CSS) · Python FastAPI + pandas + SQLite · deploy on
> Vercel. Deadline: the Space Apps 2026 submission deadline. Full brief: `FLARE_Master_Execution_Prompt (1).md`.

## Priorities

Machine learning and design quality come first, then shipping a working demo inside the time and
usage budget, then images and video. When they compete, say so and let the team choose.

## Skills: who owns what

Each job has one owner skill; the full table and the rules for disagreements are in
`.claude/CONFLICTS.md`. In short:

- **Design direction, layout, critique:** impeccable. Run `/impeccable init` once per project.
  Emil Kowalski's skills decide *how* things move; impeccable decides *whether*.
  `frontend-design`, `design-taste-frontend` and `ui-ux-pro-max` are manual second opinions.
- **Data:** `explore-data` → `analyze` → `validate-data`. **ML:** K-Dense `scikit-learn`,
  `statistical-analysis`, `shap`; `ml-training-recipes` for PyTorch.
- **Planning:** `brainstorming` → `writing-plans`. **Debugging:** `systematic-debugging`.
  **Before saying anything works:** `verification-before-completion`.
- **Usage:** `usage-aware`.

If two loaded skills disagree and `CONFLICTS.md` doesn't settle it, quote both, recommend one, and
ask. Record the answer here.

## How to work

Based on [Andrej Karpathy's coding guidelines](https://github.com/multica-ai/andrej-karpathy-skills):

- **Think first.** State assumptions; if a request has two readings, ask instead of picking one.
- **Simplest thing that works.** Nothing speculative, no abstractions for one use, no options
  nobody asked for. A hackathon rewards a working demo, not architecture.
- **Surgical changes.** Touch only what the task needs; mention unrelated problems, don't fix them.
- **Define done, then prove it.** Turn each task into a check (a test, a command, a rendered page)
  and run it before saying it works.

## Machine learning

- A simple baseline first (majority class, linear model, last value). Every later model is judged
  against it.
- Split the data before any preprocessing, scaling, imputation or feature selection; keep related
  rows (same user, patient, site) in one split, and split by time when predicting the future.
- Pick the metric for the problem (imbalanced classes → precision/recall/F1 or PR-AUC, not
  accuracy) and report it on held-out data only.
- Fix seeds and record versions, so a result can be run again.
- Run `validate-data` before any number goes on a slide. Never state an accuracy that a run in
  this session didn't produce.

## Design

- `/impeccable` before deciding what a screen looks like; its hook flags generated-looking UI after
  edits.
- Check every screen at phone width (375px) as well as desktop, and run `break-ui` with worst-case
  data before the demo.
- One animation library per project (Motion or GSAP), chosen once and recorded here.
  **Chosen: Motion** (2026-11-14). Video framework: **Remotion**.
- Follow the NASA Space Apps brand guidelines (palette, Fira Sans / Overpass, Neon Yellow as accent
  only, contrast ≥ 4.5:1, no NASA insignia); `DESIGN.md` records them once impeccable writes it.

## Usage and credits

- Run the `usage-aware` checkpoint before starting anything large and after each milestone, and
  tell the team in one line what it cost.
- Read only what a task needs (search first, then ranged reads), batch questions and independent
  steps, and don't spawn subagents unless asked.
- Suggest `/compact` when the history isn't needed any more, and `/handoff` then `/clear` when
  switching to unrelated work.

## Images and video

No paid APIs or credits. Use the free routes in order: made in code (`canvas-design`,
`algorithmic-art`, SVG, three.js), a video framework (Remotion or HyperFrames, one per project),
public free-GPU Hugging Face Spaces through `gradio predict`, and local models only if there's a GPU.
If something can't be made for free, say so instead of reaching for a paid service.

## Housekeeping

- Commit after each working step with a message that says why. The team pushes.
- Secrets live in `.env`, never in git or in a slide.
- Never invent data, results, users, testimonials or numbers for the pitch.
