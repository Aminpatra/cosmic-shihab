# References

Every external resource FLARE uses or was built with: data, rules, software, fonts, SI tools,
services and images. Licences are given where the resource states one.

## NASA data

- **NASA Physical Sciences Informatics (PSI)**, https://psi.nasa.gov. Research area Combustion
  Science: investigation records, file lists, experimental tables and documents, retrieved
  14 November 2026. 23 investigations CC0-1.0; PSI-10 states no licence.
- **The 24 investigations, cited by DOI:**
  PSI-10 ACME Flame Design, https://doi.org/10.60555/w4zy-bt45 ·
  PSI-20 ACME BRE, https://doi.org/10.60555/vb93-3y72 ·
  PSI-21 ACME CLD Flame, https://doi.org/10.60555/23e1-9950 ·
  PSI-22 ACME E-FIELD Flames, https://doi.org/10.60555/se5a-8c73 ·
  PSI-23 ACME s-Flame, https://doi.org/10.60555/k57n-p030 ·
  PSI-25 BASS-II, https://doi.org/10.60555/4qc4-de67 ·
  PSI-26 BASS, https://doi.org/10.60555/58h4-dy80 ·
  PSI-39 CFI, https://doi.org/10.60555/m6pj-a914 ·
  PSI-47 DAFT / DAFT-2, https://doi.org/10.60555/ztgj-d202 ·
  PSI-60 SPICE data analysis, https://doi.org/10.60555/mzjm-yv57 ·
  PSI-62 Concurrent flame spread modeling, https://doi.org/10.60555/e9xp-ex83 ·
  PSI-68 FLEX-2, https://doi.org/10.60555/byp8-h018 ·
  PSI-69 FLEX, https://doi.org/10.60555/mbq8-0451 ·
  PSI-98 Saffire-I, https://doi.org/10.60555/0t15-1z43 ·
  PSI-99 Saffire-II, https://doi.org/10.60555/2chp-m469 ·
  PSI-100 Saffire-III, https://doi.org/10.60555/040q-4h36 ·
  PSI-101 SAME-R, https://doi.org/10.60555/2np7-jv14 ·
  PSI-102 SAME, https://doi.org/10.60555/gd4k-8h62 ·
  PSI-106 SLICE, https://doi.org/10.60555/pm12-rg61 ·
  PSI-107 SPICE, https://doi.org/10.60555/9kbh-e962 ·
  PSI-115 SAME data for smoke modeling, https://doi.org/10.60555/q0v5-1v28 ·
  PSI-117 Cool flame dynamics CFD, https://doi.org/10.60555/gz0q-b577 ·
  PSI-142 Cool flame transitions, https://doi.org/10.60555/80qf-vj95 ·
  PSI-159 ACME CFI-G, https://doi.org/10.60555/cyt1-kh64

## Challenge and guidelines

- NASA Space Apps Challenge 2026, "Flame in Freefall" challenge page,
  https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=details (quoted in our
  problem statement).
- NASA Space Apps Challenge brand guidelines, updated 25 June 2026,
  https://www.spaceappschallenge.org/brand/ (palette and typefaces).
- NASA Space Apps Challenge Judging & Awards Guide and Project Submission Guide, dated
  13 November 2026, https://www.spaceappschallenge.org/resources/judging-awards-guide.

## Software

**Website:** React 19.3.1 and React DOM (MIT), React Router 8.5.1 (MIT), Vite 8.3.8 and
@vitejs/plugin-react 6.3.0 (MIT), Lucide icons via lucide-react 1.73.0 (ISC).

**Typefaces:** Fira Sans and Fira Code (Mozilla) and Overpass (Red Hat), SIL Open Font License
1.1, self-hosted through Fontsource 5.3.0.

**API:** FastAPI 0.162.7 (MIT) with Starlette (BSD-3-Clause) and Pydantic (MIT); Anthropic Python
SDK 2.8.0 (Apache-2.0); Uvicorn 0.54.0 (BSD-3-Clause) and httpx2 2.16.0 (BSD-3-Clause) for local
running and tests; SQLite with full-text search (public domain).

**Data pipeline and model:** pypdf 7.1.0 (BSD-3-Clause), scikit-learn 1.9.1 (BSD-3-Clause), SHAP
0.54.1 (MIT), NumPy 2.5.4 (BSD-3-Clause).

**Analysis charts:** Matplotlib 3.10.3 (Matplotlib License, PSF-based).

**Team tooling:** Model Context Protocol Python SDK, `mcp` 1.x (MIT), for our task coordinator;
Playwright 1.65.1 and playwright-core 1.56.1 (Apache-2.0) for browser QA, with Google Chrome
and Microsoft Edge run headless (Edge also driven through its DevTools protocol for the test
report).

**Runtimes:** Python and Node.js.

## SI tools

- **Claude Code** by Anthropic, with the models Claude Opus 5.5 and Claude Fable 5.2: the coding
  agent the team built FLARE with (see Use of SI).
- **Anthropic API, Claude Opus 5.5:** the model behind FLARE's research assistant.
- **Context7** (Upstash), an MCP server that gave the coding agents current library documentation.

## Instructions for the coding agents

Public instruction packs ("skills") and guidelines installed in our repository for Claude Code,
by source:

- Anthropic, https://github.com/anthropics/skills (algorithmic-art, canvas-design, frontend-design)
  and https://github.com/anthropics/knowledge-work-plugins (analyze, explore-data, validate-data)
- Superpowers, https://github.com/obra/superpowers (brainstorming, writing-plans,
  systematic-debugging, verification-before-completion)
- Emil Kowalski, https://github.com/emilkowalski/skills (animate, animation-performance, break-ui,
  choreograph, emil-design-eng, gestures, pick-ui-library, review-animations)
- K-Dense AI, https://github.com/K-Dense-AI/scientific-agent-skills (matplotlib, polars,
  scikit-learn, seaborn, shap, statistical-analysis)
- Vercel, https://github.com/vercel-labs/agent-skills (deploy-to-vercel,
  vercel-react-best-practices, web-design-guidelines)
- Hugging Face, https://github.com/huggingface/skills (huggingface-gradio, huggingface-spaces,
  transformers-js)
- Remotion, https://github.com/remotion-dev/skills (remotion-best-practices, remotion-captions,
  remotion-create, remotion-render)
- Orchestra Research, https://github.com/Orchestra-Research/AI-Research-SKILLs
  (ml-training-recipes, stable-diffusion-image-generation)
- https://github.com/affaan-m/ECC (frontend-slides, ui-demo)
- Motion, https://github.com/motiondivision/ai-kit (motion)
- https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (ui-ux-pro-max)
- https://github.com/Leonxlnx/taste-skill (design-taste-frontend)
- OpenAI, https://github.com/openai/skills (jupyter-notebook)
- https://github.com/mattpocock/skills (handoff)
- https://github.com/JuliusBrussee/caveman (caveman)
- daymade, https://github.com/daymade/claude-code-skills (claude-usage-analyst, MIT; repackaged
  by us as usage-aware)
- impeccable design skill (Apache-2.0) [source URL: team to confirm]
- Context7 skill [source URL: team to confirm]
- Andrej Karpathy's coding guidelines, https://github.com/multica-ai/andrej-karpathy-skills (our
  working rules)

## Services

- **Vercel:** hosts the website and the API.
- **GitHub:** our repository, issues and pull requests.
- **doi.org:** resolves every DOI link.

## Images

- **Team logo** (Cosmic Shihab): the team's own work, not made with SI (`brand/`).
- **Illustrations:** the pitch opening's drawings, the flame drawings on the Methodology and
  Scenario pages and the astronaut on the Home page, made with SI (Claude Code), each marked
  "Illustration made with SI".
- **Charts:** drawn by FLARE from NASA PSI data (SVG on the website; Matplotlib in our analysis).
- No other images, and no copyrighted music, images or text.

<!--
For the team (not for the form). Draft for the "Space Agency Partner Data and Other References"
field, issue #36. Sources:
- DOIs, licences, retrieval date: backend/data/investigations/*.json.
- Challenge URL: FLARE_Master_Execution_Prompt (1).md section 1. Brand guidelines: the Sources
  page (frontend/src/pages/Sources.jsx). Judging and submission guides: CRITERIA.md (the
  Submission Guide's own URL is not recorded there; add it).
- Website versions and licences: frontend/node_modules/*/package.json, read 2026-11-14.
- anthropic, fastapi, httpx2, uvicorn, starlette, pydantic: licence metadata in backend/.venv,
  read 2026-11-14. pypdf, scikit-learn, shap, numpy, matplotlib, mcp: not installed on this
  machine; versions from pipeline/requirements.txt, research/analysis/requirements.txt and
  coordinator/requirements.txt, licences as each project publishes them (check before submitting).
- Playwright 1.65.1: submission/qa_results.md (#37). playwright-core with Microsoft Edge: the
  browser check of #47 (not committed).
- Skills and their sources: skills-lock.json; usage-aware's origin and licence:
  .claude/skills/usage-aware/SKILL.md; impeccable's licence: its SKILL.md frontmatter (source
  repo not recorded in the repo); Karpathy guidelines: CLAUDE.md.
- Context7 MCP: .claude/rules/context7.md.
- Logo: brand/cosmic-shihab-logo-white.png (the copy in frontend/src/assets/ is on the Sources
  page) and brand/cosmic-shihab-logo-black.png; the team's own, not SI-made (2026-11-15, #62).
- Recharts and Motion are named in CLAUDE.md and PRODUCT.md but are not in frontend/package.json,
  so they are not listed. Add them if a later PR installs them.
-->
