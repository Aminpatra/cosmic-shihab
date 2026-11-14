# Team decisions

Agreements between tasks that every agent must respect: API contract, data shape, env var, new dependency, folder or naming convention. One line each, append only, newest last. Skill and stack choices belong in `CLAUDE.md`, not here.

`- YYYY-MM-DD @github-login: the agreement, in one sentence (#issue-or-PR)`

- 2026-11-14 @UncCodes: the assistant's key is read from `ANTHROPIC_API_KEY` in `.env` (ignored by git), and every feature must still work when it is absent.
- 2026-11-14 @UncCodes: each member logs their AI use in their own file, `docs/ai-use/<github-login>.md`, so branches never collide on it.
- 2026-11-14 @UncCodes (proposed; stands once the lead merges it): folders follow the master prompt's section 13: `frontend/` and `backend/` deploy as two Vercel services, `pipeline/` runs offline and writes read-only files to `backend/data/`, raw PSI files stay in `datasets/`, downloads go to the ignored `.cache/`.
- 2026-11-14 @UncCodes (proposed; stands once the lead merges it): backend code targets Python 3.12 to 3.14 (what Vercel runs), with runtime dependencies only in `backend/pyproject.toml`.
- 2026-11-14 @UncCodes: the catalogue the API reads is `backend/data/investigations/<ACCESSION>.json` (PSI's own field names, FLARE's additions under `derived`) and `backend/data/files.csv` (accession, file_id, file_name, category, subcategory, extension, kind, bytes, version, updated); both are written only by `pipeline/build_catalogue.py` (#5)
- 2026-11-14 @gheathwahab: the catalogue endpoints are `GET /api/health`, `GET /api/investigations` (summary fields), `GET /api/investigations/{accession}` (whole record) and `GET /api/files` (`{total, limit, offset, items}`, filters `accession`, `kind`, `category`, `limit` ≤ 500); every backend route starts with `/api` because Vercel passes the path unchanged, and the shapes are in `backend/README.md` (#8)
- 2026-11-14 @gheathwahab: `backend/main.py` defines `app` and includes one router per module in `backend/app/routes/`; ranking (#7) adds its own module there rather than editing the catalogue routes (#8)
- 2026-11-14 @gheathwahab: the API sends no CORS headers; the frontend calls relative `/api/...` paths, and in development Vite proxies `/api` to `http://127.0.0.1:8000` (#8)
- 2026-11-14 @saminre: each investigation record carries `derived.tags` = `{note, values, sources, notes}`, where `values` and `sources` both have the keys `hardware_facility`, `platform`, `fuel_phase`, `fire_safety_role`, `gravity_level`, `flare_data`; several values are joined by `"; "`, the allowed values are in `research/data_dictionary.md`, and they are written only in `research/investigation_tags.csv` and copied by `pipeline/build_catalogue.py`. `flare_data == "catalogue metadata only"` is what the explorer labels "catalogued, no run data in FLARE" (#17)
