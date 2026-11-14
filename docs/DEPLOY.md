# Deploying FLARE

**Live site:** https://cosmic-shihab.vercel.app (chosen by the team 15 November 2026, #66)

The first deploy, https://flare-sandy.vercel.app (Vercel project `flare` on @UncCodes's personal
account, #14), is an older build; don't send anyone there (`submission/test_report.md`, check 8).
Which Vercel project and account serve cosmic-shihab.vercel.app is not recorded yet: its owner
should add that here and replace `--project flare` below.

## How it is built

`vercel.json` defines two services in one deployment:

| Service | Folder | What Vercel does |
|---|---|---|
| `frontend` | `frontend/` | Runs `vite build` and serves the static files |
| `backend` | `backend/` | Installs `pyproject.toml` with Python 3.12 and runs FastAPI (`main:app`) as a function |

Requests under `/api/` go to the backend; everything else goes to the frontend. In the frontend,
any path without a dot (`/explorer`, `/sources`) gets `index.html`, so the React router can draw
the page; paths with a dot (`/favicon.svg`, `/assets/...`) are served as files.

Everything the API reads is in `backend/data/`, about 34 MB, well under Vercel's 500 MB limit for a
Python function.

## Redeploy after a merge

Deploy from a clean export of `main`, so local folders (`.venv`, `node_modules`, `.cache`) are
never uploaded:

```
git switch main && git pull --ff-only origin main
D=$(mktemp -d) && git archive HEAD | tar -x -C "$D" && rm -rf "$D/.claude"
cd "$D" && vercel link --yes --project flare && rm -f .env.local
vercel deploy --prod --yes
```

## Check it

All of these must pass after every deploy, opened with no login:

```
B=https://cosmic-shihab.vercel.app
curl -s $B/api/health                       # {"status":"ok","investigations":24,"files":60866,...}
curl -s -o /dev/null -w "%{http_code}\n" $B/explorer       # 200, text/html
curl -s -o /dev/null -w "%{http_code}\n" $B/favicon.svg    # 200, image/svg+xml
curl -s -o /dev/null -w "%{http_code}\n" $B/api/nope       # 404
curl -s "$B/api/rank?oxygen=0.3&pressure=0.7" | head -c 200    # JSON with ranked items
```

**Deploy log**

| When (14 Nov 2026) | What was deployed | Result |
|---|---|---|
| First deploy | `main` at #24 plus `vercel.json` | Every page, `/api/health`, `/api/investigations/{accession}`, `/api/files`, `/api/search`, the download redirect and `/api/docs` answered correctly |
| Redeploy | `main` at #34, adding the ranking API (#31) | All of the above plus `/api/rank` and `/api/rank/options` answered correctly. The download redirect returned 502 "PSI did not answer", because PSI's download-link service was timing out for everyone, even called directly; PSI's search and website were up |
| Redeploy | `main` at #41, adding the AI assistant | All of the above plus `/assistant`, `/api/assistant/status` and `/api/assistant/ask`, which answer in `retrieval_only` mode (sources, no generated text) because no `ANTHROPIC_API_KEY` is set yet. `/api/assistant/summaries/{accession}` returns 404 until #28 writes summaries. PSI's download links were still timing out |

A 502 from `/api/files/{file_id}/download` means PSI is not answering, not that the deploy is broken.
Call PSI directly to tell the two apart (see `download_url` in `pipeline/psi_client.py`).

## Test it locally

`vercel dev --local --listen 3123` runs both services together, with no Vercel login.

## Open points

- **Automatic deploys.** Connecting the GitHub repo to the Vercel project would redeploy on every
  merge to `main`. That needs the repo owner (@gheathwahab) to let Vercel's GitHub app read the repo.
- **The assistant's key.** When #10 needs it, set `ANTHROPIC_API_KEY` in the Vercel project's
  environment variables. Never commit it.
- **Judges' networks.** `CRITERIA.md` recommends requesting a FortiGuard Web Filter
  Classification for the live URL.
