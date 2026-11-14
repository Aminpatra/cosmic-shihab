# Setup status (claude-starter-kit)

Resume with: `Read claude-starter-kit/MASTER-PROMPT.md and finish the setup.`

## Answers (step 1, 2026-11-14)
- Runs Claude Code in: VS Code extension (status line not used; Playwright MCP allowed)
- Plan: Pro/Max subscription (budgets in tokens). Budget: decide later
- Building: FLARE, React + Vite frontend, Python FastAPI backend, plain CSS (no shadcn/ui), deploy to Vercel
- Animation: Motion. Video: Remotion. ML: none yet. Simulation: none
- Local NVIDIA GPU: RTX 3050 6 GB, install stable-diffusion skill; no ComfyUI
- git-guardrails: no
- spendcap: project scope only (do not touch ~/.claude/settings.json)

## Steps
- [x] Step 1 · Questions
- [x] Step 2 · Tools (Node 26.13.1, Python 3.15.2, Git 2.56.1 already present)
- [x] Step 3 · Installs (2026-11-14)
  - ML/data: scikit-learn, statistical-analysis, shap, polars, matplotlib, seaborn, explore-data,
    analyze, validate-data, ml-training-recipes, jupyter-notebook, huggingface-gradio,
    huggingface-spaces, transformers-js
  - Design: impeccable (+ hook, installed 2026-11-13), Emil's 8 skills, web-design-guidelines
  - Manual-only: frontend-design, design-taste-frontend, ui-ux-pro-max, caveman
  - Workflow: brainstorming, writing-plans, systematic-debugging, verification-before-completion,
    handoff, frontend-slides, ui-demo
  - Usage: usage-aware (copied from kit); spendcap as plugin, scope local (.claude/settings.local.json),
    no budget yet — set later with
    `npx -y github:nrzz/claude-cost-guard budget set --project . --daily <N>M --weekly <N>M`
  - ccusage status line: skipped (VS Code extension; terminal-only feature)
  - Stack: vercel-react-best-practices (upstream renamed from react-best-practices), motion,
    deploy-to-vercel
  - Media: canvas-design, algorithmic-art, remotion-best-practices/create/render/captions,
    stable-diffusion-image-generation
  - MCP: Playwright (local scope); Context7 (project scope, signed in). Context7 also added skill
    `context7-mcp` and rule `.claude/rules/context7.md`. Its API key is in `.mcp.json`, which is
    gitignored.
  - git-guardrails: not installed (user said no)
  - CLAUDE.md filled in; .claude/CONFLICTS.md copied; .gitignore has claude-starter-kit/
- [x] Step 4 · check-skills.mjs: 47 skills, 40 auto, 7 manual, no duplicate names, ~3,128 tokens
- [x] Step 5 · New session (2026-11-14): all 40 auto skills listed, 7 manual-only (caveman,
  design-taste-frontend, frontend-design, handoff, pick-ui-library, review-animations,
  ui-ux-pro-max); check-skills: no duplicates, ~3,128 tokens. usage-aware checkpoint: 6.7M tokens
  today (96% cache reads), no active 5-hour block. `/impeccable init` wrote PRODUCT.md (primary
  user: researchers; laptop + projected demo). No image tool, so no buildPath recorded; live mode
  skipped until the app runs. Node is installed but VS Code's PATH is stale: restart VS Code fully.
  Pending from user: FLARE logo file location, team member names to credit.
- [x] Step 6 · Cheat sheet given (2026-11-14). Setup COMPLETE.
- Open decision: commit `.claude/skills/` (75 MB, 37 MB of it design-taste-frontend example
  assets) or have teammates reinstall from skills-lock.json. impeccable's binary is gitignored.
- Note: hooks and spendcap live in `.claude/settings.local.json`, which is gitignored, so
  teammates don't get them from git.
