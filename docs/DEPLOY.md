# Deploying FLARE

**Live site:** https://flare-sandy.vercel.app (first deployed 14 November 2026, #14)

It is the Vercel project `flare` on @UncCodes's personal Vercel account (Hobby plan). Only that
account can redeploy it until the project is moved or shared; see "Open points".

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
B=https://flare-sandy.vercel.app
curl -s $B/api/health                       # {"status":"ok","investigations":24,"files":60866,...}
curl -s -o /dev/null -w "%{http_code}\n" $B/explorer       # 200, text/html
curl -s -o /dev/null -w "%{http_code}\n" $B/favicon.svg    # 200, image/svg+xml
curl -s -o /dev/null -w "%{http_code}\n" $B/api/nope       # 404
```

On 14 November 2026 every page, `/api/health`, `/api/investigations/{accession}`, `/api/files`,
`/api/search`, the download redirect and `/api/docs` answered correctly.

## Test it locally

`vercel dev --local --listen 3123` runs both services together, with no Vercel login.

## Open points

- **Automatic deploys.** Connecting the GitHub repo to the Vercel project would redeploy on every
  merge to `main`. That needs the repo owner (@gheathwahab) to let Vercel's GitHub app read the repo.
- **The assistant's key.** When #10 needs it, set `ANTHROPIC_API_KEY` in the Vercel project's
  environment variables. Never commit it.
- **Judges' networks.** `CRITERIA.md` recommends requesting a FortiGuard Web Filter
  Classification for the live URL.
