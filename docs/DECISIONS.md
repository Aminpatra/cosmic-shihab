# Team decisions

Agreements between tasks that every agent must respect: API contract, data shape, env var, new dependency, folder or naming convention. One line each, append only, newest last. Skill and stack choices belong in `CLAUDE.md`, not here.

`- YYYY-MM-DD @github-login: the agreement, in one sentence (#issue-or-PR)`

- 2026-11-14 @UncCodes: the assistant's key is read from `ANTHROPIC_API_KEY` in `.env` (ignored by git), and every feature must still work when it is absent.
- 2026-11-14 @UncCodes: each member logs their AI use in their own file, `docs/ai-use/<github-login>.md`, so branches never collide on it.
- 2026-11-14 @UncCodes: folders follow the master prompt's section 13: `frontend/` and `backend/` deploy as two Vercel services, `pipeline/` runs offline and writes read-only files to `backend/data/`, raw PSI files stay in `datasets/`, downloads go to the ignored `.cache/`.
- 2026-11-14 @UncCodes: backend code targets Python 3.12 to 3.14 (what Vercel runs), with runtime dependencies only in `backend/pyproject.toml`.
