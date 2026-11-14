# CONFLICTS.md: how these skills work together

Every skill in this kit was chosen so that **each job has exactly one owner**. Where two good skills
cover the same job, one leads and the other is either left out or set to manual-only. This file is
the rulebook for that. Claude reads it before installing anything and whenever two skills seem to
pull in different directions.

## The four kinds of conflict, and the rule for each

1. **Same name.** Two skills with the same `name` overwrite each other on install, and the survivor
   isn't the one you meant. *Rule:* never install a second skill whose name is already taken. The
   install step checks this. (Known clashes avoided: `prototype` exists in both Emil Kowalski's and
   Matt Pocock's repos, so neither is installed; `statistical-analysis` exists in K-Dense and in
   Anthropic's data plugin, so only K-Dense's is installed.) **Personal skills count too:** a skill
   in `~/.claude/skills/` loads in every project, and when the same name exists there and in the
   project, the personal copy wins. An old personal `impeccable` would silently replace the
   project's. `tools/check-skills.mjs` lists both places and flags these.
2. **Same job, different opinions.** Two design skills both trying to set the visual direction will
   give Claude contradictory instructions (one says "hover animation on every card", another says
   that's the tell of generated UI). *Rule:* one owner per job (table below). The others are
   manual-only or left out.
3. **Hooks and settings.** Hooks run outside Claude and can block, slow down or re-trigger work.
   Claude Code allows **one** status line. *Rule:* only the hooks listed below, nothing that
   replaces the status line, and no plugin whose session-start hook pushes extra context every turn.
4. **Same file.** Two skills that both write a project memory file (for example `DESIGN.md`) will
   overwrite each other's format. *Rule:* one writer per file.

## Who owns what

| Job | Owner | Supporting (load only for their narrow part) | Deliberately not installed, and why |
|---|---|---|---|
| Visual direction, layout, hierarchy, critique, `DESIGN.md` | **impeccable** | `web-design-guidelines` audits accessibility and UX rules after building | Anthropic `frontend-design`, `taste-skill`, `ui-ux-pro-max`: installed **manual-only** as second opinions. ibelick `ui-skills`, Dammyjay93 `interface-design`, ECC `frontend-design-direction`, Emil `learn-taste`: overlap impeccable or write their own design memory file |
| Whether something should move | **impeccable** | | |
| How motion is built (curve, duration, interruption, choreography, gestures, frame budget) | **Emil Kowalski's skills** (`emil-design-eng`, `animate`, `choreograph`, `gestures`, `animation-performance`, `review-animations`) | | Emil `improve-animations` (overlaps `review-animations` for a short project) |
| An animation library's API | **one per project:** `motion` (React UI) **or** the `gsap-*` skills (scroll scenes, timelines) | | Installing both libraries' skills in one project |
| Worst-case data before a demo | `break-ui` | | |
| React performance | `react-best-practices` (React/Next only) | | |
| Components | `shadcn` (only if the project uses shadcn/ui) | | |
| Data workflow: explore, answer, check | Anthropic `explore-data` → `analyze` → `validate-data` | | Anthropic `create-viz`, `data-visualization`, `build-dashboard`, `statistical-analysis` (overlap K-Dense or the app itself); K-Dense `exploratory-data-analysis` (aimed at scientific file formats) |
| Statistics, ML libraries, leakage-safe evaluation | **K-Dense** (`statistical-analysis`, `scikit-learn`, `shap`, `polars`, `transformers`, `matplotlib`, `seaborn`) | | |
| Training deep models | Orchestra `ml-training-recipes` | | ECC `pytorch-patterns` (same job) |
| Notebooks | OpenAI `jupyter-notebook` | | marimo skills (pick one notebook style) |
| ML demo UI and free hosting | Hugging Face `huggingface-gradio`, `huggingface-spaces` | | Streamlit (its skills now ship inside Streamlit 1.60+; use it instead only if the team already knows it) |
| ML inside the browser app | `transformers-js` | | |
| Simulation | K-Dense `simpy` (queues, events), `stable-baselines3` (agents learning in a simulated world), `pymoo` (optimization), `sympy`, `networkx`; `threejs-*` for 3D in the browser | | |
| Planning a feature | superpowers `brainstorming` → `writing-plans` | | Matt Pocock `grill-me`, `to-spec` (same job) |
| Debugging | superpowers `systematic-debugging` | | Matt Pocock `diagnosing-bugs` (same job) |
| "Is it actually done?" | superpowers `verification-before-completion` | | |
| Handing work to a fresh session | Matt Pocock `handoff` | | |
| Pitch deck | ECC `frontend-slides` (HTML deck) | Anthropic `pptx` only if a `.pptx` file is required | |
| Demo video of the app | ECC `ui-demo` (Playwright recording) | | |
| Explainer and product videos | **one per project:** `remotion-*` (React) **or** HyperFrames (HTML + GSAP) | ECC `manim-video` for math and simulation explainers | Installing both video frameworks |
| Images without paid credits | Anthropic `canvas-design`, `algorithmic-art` (made in code); `huggingface-gradio` to call public free-GPU Spaces; Orchestra `stable-diffusion` or ComfyUI only with a local GPU | | Any paid image/video API (fal, OpenAI, Gemini image, OpenRouter, Pollinations) |
| Spending limits | **spendcap** (budgets, warnings to the person, optional hard stop) | | ECC cost-tracking (needs ECC's whole setup), claude-context-optimizer (a hook on every tool call) |
| Claude knowing what it spends | **usage-aware** (in this kit, repackaged from daymade's `claude-usage-analyst`) | `caveman`, manual-only, for terse replies when the budget is tight | |
| Live usage display for the person | **ccusage** status line (terminal only) | | caveman's status line and hooks (Claude Code has one status line) |

## Hooks this kit allows

| Hook | From | What it does | Cost |
|---|---|---|---|
| Session start, after UI file edits, and on Stop | impeccable | Prepares its context, then scans changed UI files for generated-design patterns | Small; no model tokens unless it finds something to report |
| Before each prompt | spendcap | Checks the budget; warns the person; blocks only in hard mode | Zero tokens |
| Before Bash runs | git-guardrails (optional) | Blocks `git push`, `reset --hard`, `clean -f`, `branch -D` | Zero tokens. The team pushes themselves |
| On Stop, only after it was invoked manually | taste-skill | Runs its browser check on a landing page | Runs Chrome; up to 10 minutes |
| Session start, once | team-sync (this repo, `.claude/hooks/team-sync.sh`, PR #1) | Prints a 10–20 line digest: task owners, branches in flight, open PRs, team decisions | One short digest per session, not per turn; about 3.5 s |

Never install: superpowers as a **plugin** (its session-start hook injects its rules every session;
the skills are installed individually instead), caveman's hooks or status line, or any second
status line.

## When two loaded skills still disagree

1. The project's `CLAUDE.md` and the user's words win over every skill.
2. Then the **owner** in the table above wins over a supporting skill.
3. A library's own skill wins on that library's API (GSAP on GSAP, Remotion on Remotion), and only
   there.
4. If none of these settles it, follow neither silently: say which two skills disagree, quote the
   two instructions, recommend one, and let the user choose. Record the decision in `CLAUDE.md` so
   it isn't asked twice.

## Adding a skill later

Before installing anything new, check: is its name taken? Does an owner already exist for its job?
Does it bring hooks, a status line or a memory file? If it duplicates an owner, either replace the
owner (and remove the old one) or install the new one with `disable-model-invocation: true` added
to its frontmatter, so it only runs when called by name. Skills from public registries vary a lot
in quality: read the `SKILL.md` and any scripts before installing, the way this kit's choices were
checked.
