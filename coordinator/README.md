# coordinator

The team's shared task coordinator: one MCP server that every Claude agent on this repo connects
to. GitHub issues stay the task descriptions; the coordinator is the single source of truth for
who holds which task and which tasks are ready.

- **Atomic claims.** Every claim runs inside SQLite's `BEGIN IMMEDIATE`, so two agents claiming at
  the same moment never get the same task.
- **Claims expire.** A claim is a 30-minute lease, renewed by `heartbeat`. A session that ends
  stops renewing, and the task becomes claimable again.
- **Only ready work is handed out.** A task is ready when it is open, nobody holds it, every
  blocker is done (an issue not on the board counts as closed), and none of its `touches` overlap
  a held task's. Ready tasks go out in this order: the one that unblocks the most open tasks
  first, then the highest `priority`, then the lowest issue number.

## Tools

Each tool that acts for someone takes `agent`, the caller's GitHub login.

| Tool | What it does |
|---|---|
| `add_task(id, title, blocked_by, touches, priority)` | Add a task or update it (`id` = issue number). Never changes who holds it |
| `claim_next(agent)` | Claim the best ready task |
| `claim(agent, task_id)` | Claim one specific task, if it is ready |
| `heartbeat(agent, task_id)` | Renew your lease for 30 minutes. Call it after every commit |
| `complete(agent, task_id)` | Mark your task done once its PR has merged |
| `release(agent, task_id)` | Give your task back unfinished |
| `board()` | Every task: done, held by someone, ready, or waiting (and on what) |
| `wait_for_work(agent, timeout_s=240)` | Try to claim every 5 s until something is ready, at most 280 s |

`heartbeat`, `complete` and `release` refuse a task you don't hold and say who does. `heartbeat`
won't revive a lease that has run out (claim the task again); `complete` and `release` still work
after it runs out, as long as nobody else has claimed the task since.

**Writing `touches`.** Globs of the paths a task edits, such as `frontend/src/pages/Explorer*` or
`backend/app/routes/*`. Two globs overlap when the part of one before its first `*` starts with the
other's. Leave out files every task appends to (`docs/DECISIONS.md`, `docs/ai-use/*`), or every task
will overlap every other and only one can run at a time.

## Run it

Pick one always-on machine. It needs Python 3.12 or newer.

**1. Make one token per person.**

```
openssl rand -hex 16
```

Run it six times and send each person their own token privately (not in the repo, not in a group
chat). The server takes them all, comma-separated.

**2. Start the server.**

```
cd coordinator
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
COORD_TOKENS=tokenA,tokenB,tokenC,tokenD,tokenE,tokenF .venv/bin/python server.py
```

It listens on `http://127.0.0.1:8000/mcp`. `PORT` changes the port, `COORD_DB` the database file
(default `coordinator.db`, ignored by git), and `HOST` the address it binds to (`0.0.0.0` on a
server that is reached directly rather than through a tunnel).

**3. Expose it.**

```
cloudflared tunnel --url http://localhost:8000
```

`cloudflared` prints an address like `https://something.trycloudflare.com`. That free tunnel gets
a new address every time it restarts, and everyone then has to update `COORD_URL`. For something
longer-lived, run the server on Fly.io or a small server with a persistent disk, so the database
and the address both survive restarts.

## Connect your agent

Before starting Claude Code, export:

```
export COORD_URL=https://something.trycloudflare.com/mcp   # the tunnel address plus /mcp
export COORD_TOKEN=<your token>
export MCP_TOOL_TIMEOUT=300000                              # so wait_for_work isn't cut off
```

`.mcp.json` at the repo root reads those variables. On the first launch Claude Code asks whether to
approve the project's `coordinator` server; approve it. Then check:

```
claude mcp list        # coordinator: ... - ✔ Connected
```

If it can't connect, the agents fall back to the `/team-claim` flow in
`.claude/rules/team-sync.md`.

**If you had your own `.mcp.json`** (for example the Context7 server with its API key), move that
server out of the repo file before pulling, so the key is never committed:
`claude mcp add --scope local ...` stores it privately in your own config.

## Test it

```
cd coordinator && .venv/bin/python -m pytest -v
```

The tests call the tools directly: readiness, ordering, 20 threads racing for one task, lease
expiry and heartbeat, other agents being refused, and the 401 for a missing or wrong token.

**SI use:** written with Claude Code (Claude Opus 5.5) and reviewed by the team.
