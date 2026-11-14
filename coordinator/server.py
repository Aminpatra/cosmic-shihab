"""FLARE task coordinator: one MCP server every Claude agent on the repo connects to.

GitHub issues stay the task descriptions. This server is the single source of truth for who holds
which task and which tasks are ready, so that claiming is atomic, claims expire, and only unblocked,
non-overlapping tasks are handed out.

    COORD_TOKENS=tok1,tok2 python server.py      # serves http://127.0.0.1:8000/mcp

AI use: written with Claude Code (Claude Opus 5.5) and reviewed by the team.
"""

from __future__ import annotations

import asyncio
import hmac
import json
import os
import sqlite3
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# ── Configuration ────────────────────────────────────────────────────────────────────────────────

DB_PATH = os.environ.get("COORD_DB", "coordinator.db")
TOKENS = {t.strip() for t in os.environ.get("COORD_TOKENS", "").split(",") if t.strip()}
HOST = os.environ.get("HOST", "127.0.0.1")  # cloudflared reaches it locally; Fly.io needs 0.0.0.0
PORT = int(os.environ.get("PORT", "8000"))

LEASE_S = 30 * 60  # a claim lasts 30 minutes unless the holder calls heartbeat
POLL_S = 5  # wait_for_work tries to claim this often
# Claude Code cuts a tool call off at MCP_TOOL_TIMEOUT (we ask for 300 s), so never wait longer.
MAX_WAIT_S = 280


def now() -> float:
    """Seconds since the epoch. One function, so tests can move the clock."""
    return time.time()


# ── Storage ──────────────────────────────────────────────────────────────────────────────────────
# One small SQLite file. Leases are stored as epoch seconds (REAL); lists as JSON text.

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY,                  -- the GitHub issue number
    title       TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'done')),
    blocked_by  TEXT    NOT NULL DEFAULT '[]',        -- JSON list of issue numbers
    touches     TEXT    NOT NULL DEFAULT '[]',        -- JSON list of path globs
    owner       TEXT,                                 -- GitHub login of the last holder
    lease_until REAL,                                 -- epoch seconds; NULL when nobody holds it
    priority    INTEGER NOT NULL DEFAULT 0            -- higher goes first among equals
)
"""


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    """A write transaction taken with BEGIN IMMEDIATE.

    IMMEDIATE takes SQLite's write lock before the first read, so two agents claiming at the same
    moment are serialized: the second one reads the board only after the first has committed, and
    can never be handed the same task. A fresh connection per call keeps this thread-safe.
    """
    db = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)  # we issue BEGIN ourselves
    db.row_factory = sqlite3.Row
    try:
        db.execute(SCHEMA)
        db.execute("BEGIN IMMEDIATE")
        yield db
        db.execute("COMMIT")
    except sqlite3.Error:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise
    finally:
        db.close()  # closing also discards a transaction left open by any other exception


def load_tasks(db: sqlite3.Connection) -> dict[int, dict]:
    tasks = {}
    for row in db.execute("SELECT * FROM tasks"):
        task = dict(row)
        task["blocked_by"] = json.loads(task["blocked_by"])
        task["touches"] = json.loads(task["touches"])
        tasks[task["id"]] = task
    return tasks


def iso(epoch: float | None) -> str | None:
    if epoch is None:
        return None
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def public(task: dict) -> dict:
    """A task as tools return it."""
    return {
        "id": task["id"],
        "title": task["title"],
        "status": task["status"],
        "blocked_by": task["blocked_by"],
        "touches": task["touches"],
        "owner": task["owner"],
        "lease_until": iso(task["lease_until"]),
        "priority": task["priority"],
    }


# ── Readiness ────────────────────────────────────────────────────────────────────────────────────


def is_held(task: dict, at: float) -> bool:
    """Held = open, with an owner whose lease has not run out."""
    return (
        task["status"] == "open"
        and task["owner"] is not None
        and task["lease_until"] is not None
        and task["lease_until"] > at
    )


def globs_overlap(a: str, b: str) -> bool:
    """Two globs overlap when the part of one before its first `*` starts with the other's.

    Deliberately coarse: `frontend/*` overlaps `frontend/src/pages/Home.jsx`, and two different
    files never overlap. It errs towards holding a task back rather than letting two agents edit
    the same folder.
    """
    prefix_a, prefix_b = a.split("*", 1)[0], b.split("*", 1)[0]
    return prefix_a.startswith(prefix_b) or prefix_b.startswith(prefix_a)


def touches_overlap(a: list[str], b: list[str]) -> bool:
    return any(globs_overlap(x, y) for x in a for y in b)


def open_blockers(task: dict, tasks: dict[int, dict]) -> list[int]:
    """Blockers still open. An issue missing from the table counts as closed."""
    return [b for b in task["blocked_by"] if b in tasks and tasks[b]["status"] != "done"]


def overlapping_held(task: dict, tasks: dict[int, dict], at: float) -> list[dict]:
    return [
        other
        for other in tasks.values()
        if other["id"] != task["id"]
        and is_held(other, at)
        and touches_overlap(task["touches"], other["touches"])
    ]


def is_ready(task: dict, tasks: dict[int, dict], at: float) -> bool:
    return (
        task["status"] == "open"
        and not is_held(task, at)
        and not open_blockers(task, tasks)
        and not overlapping_held(task, tasks, at)
    )


def unblocks(task: dict, tasks: dict[int, dict]) -> int:
    """How many open tasks list this one as a direct blocker."""
    return sum(1 for t in tasks.values() if t["status"] == "open" and task["id"] in t["blocked_by"])


def ready_tasks(tasks: dict[int, dict], at: float) -> list[dict]:
    """Ready tasks, best first: most tasks unblocked, then highest priority, then lowest id."""
    ready = [t for t in tasks.values() if is_ready(t, tasks, at)]
    return sorted(ready, key=lambda t: (-unblocks(t, tasks), -t["priority"], t["id"]))


def describe(task: dict, tasks: dict[int, dict], at: float) -> str:
    """The task's state, as the board shows it."""
    if task["status"] == "done":
        return f"done (by {task['owner']})" if task["owner"] else "done"
    if is_held(task, at):
        return f"held by {task['owner']} until {iso(task['lease_until'])}"
    reasons = [f"blocked by #{b}" for b in open_blockers(task, tasks)]
    reasons += [f"overlaps #{o['id']} held by {o['owner']}" for o in overlapping_held(task, tasks, at)]
    return "waiting: " + "; ".join(reasons) if reasons else "ready"


# ── Tools ────────────────────────────────────────────────────────────────────────────────────────

mcp = FastMCP(
    "flare-coordinator",
    stateless_http=True,
    # FastMCP checks the Host header when bound to 127.0.0.1 and accepts only localhost, which
    # would reject every request arriving through the cloudflared tunnel. The bearer tokens below
    # already stop the browser-based attack that check exists for, and the tunnel host changes on
    # every restart, so a fixed allowlist would break.
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


@mcp.tool()
def add_task(
    id: int, title: str, blocked_by: list[int] | None = None, touches: list[str] | None = None, priority: int = 0
) -> dict:
    """Add a task, or update its title, blockers, touches and priority if it exists.

    id is the GitHub issue number. blocked_by lists issue numbers that must be done first.
    touches lists the path globs the task edits (for example "frontend/src/pages/*"); leave out
    shared append-only files such as docs/DECISIONS.md, or every task will overlap every other.
    Higher priority goes first among tasks that unblock equally many. Never changes who holds it.
    """
    blocked_by, touches = blocked_by or [], touches or []
    if id in blocked_by:
        return {"ok": False, "reason": f"#{id} cannot block itself"}
    with transaction() as db:
        db.execute(
            """INSERT INTO tasks (id, title, blocked_by, touches, priority) VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET title = excluded.title, blocked_by = excluded.blocked_by,
                   touches = excluded.touches, priority = excluded.priority""",
            (id, title, json.dumps(blocked_by), json.dumps(touches), priority),
        )
        task = load_tasks(db)[id]
    return {"ok": True, "task": public(task)}


def _take(db: sqlite3.Connection, task: dict, agent: str, at: float) -> dict:
    db.execute("UPDATE tasks SET owner = ?, lease_until = ? WHERE id = ?", (agent, at + LEASE_S, task["id"]))
    task.update(owner=agent, lease_until=at + LEASE_S)
    return {"ok": True, "task": public(task)}


@mcp.tool()
def claim_next(agent: str) -> dict:
    """Claim the best ready task for agent (your GitHub login). The lease lasts 30 minutes."""
    with transaction() as db:
        at, tasks = now(), load_tasks(db)
        ready = ready_tasks(tasks, at)
        if not ready:
            return {"ok": False, "reason": "nothing is ready", "board": _board(tasks, at)}
        return _take(db, ready[0], agent, at)


@mcp.tool()
def claim(agent: str, task_id: int) -> dict:
    """Claim one specific task for agent, if it is ready."""
    with transaction() as db:
        at, tasks = now(), load_tasks(db)
        task = tasks.get(task_id)
        if task is None:
            return {"ok": False, "reason": f"#{task_id} is not on the board; add it with add_task"}
        if is_held(task, at) and task["owner"] == agent:
            return {"ok": True, "task": public(task), "note": "already yours; call heartbeat to extend"}
        if not is_ready(task, tasks, at):
            return {"ok": False, "reason": f"#{task_id} is {describe(task, tasks, at)}"}
        return _take(db, task, agent, at)


def _held_by(task: dict | None, agent: str, task_id: int) -> str | None:
    """Why agent may not act on this task, or None if it holds it."""
    if task is None:
        return f"#{task_id} is not on the board"
    if task["status"] == "done":
        return f"#{task_id} is already done"
    if task["owner"] != agent:
        return f"#{task_id} is not yours (held by {task['owner'] or 'nobody'})"
    return None


@mcp.tool()
def heartbeat(agent: str, task_id: int) -> dict:
    """Extend agent's lease on a task it holds by another 30 minutes. Call it after every commit."""
    with transaction() as db:
        at, task = now(), load_tasks(db).get(task_id)
        refusal = _held_by(task, agent, task_id)
        # An expired lease is not renewed: an overlapping task may have been handed out meanwhile.
        if refusal is None and not is_held(task, at):
            refusal = f"your lease on #{task_id} ran out at {iso(task['lease_until'])}; claim it again"
        if refusal:
            return {"ok": False, "reason": refusal}
        return _take(db, task, agent, at)


@mcp.tool()
def complete(agent: str, task_id: int) -> dict:
    """Mark a task agent holds as done, once its pull request has merged."""
    with transaction() as db:
        task = load_tasks(db).get(task_id)
        # Allowed after the lease ran out, as long as nobody else has taken the task since: a PR
        # often merges long after its author's last heartbeat.
        refusal = _held_by(task, agent, task_id)
        if refusal:
            return {"ok": False, "reason": refusal}
        db.execute("UPDATE tasks SET status = 'done', lease_until = NULL WHERE id = ?", (task_id,))
        task.update(status="done", lease_until=None)
    return {"ok": True, "task": public(task)}


@mcp.tool()
def release(agent: str, task_id: int) -> dict:
    """Give back a task agent holds without finishing it, so someone else can claim it."""
    with transaction() as db:
        task = load_tasks(db).get(task_id)
        refusal = _held_by(task, agent, task_id)
        if refusal:
            return {"ok": False, "reason": refusal}
        db.execute("UPDATE tasks SET owner = NULL, lease_until = NULL WHERE id = ?", (task_id,))
        task.update(owner=None, lease_until=None)
    return {"ok": True, "task": public(task)}


def _board(tasks: dict[int, dict], at: float) -> list[dict]:
    order = {t["id"]: i for i, t in enumerate(ready_tasks(tasks, at))}
    rows = [{"id": t["id"], "title": t["title"], "state": describe(t, tasks, at)} for t in tasks.values()]
    # Ready tasks first in the order claim_next hands them out, then the rest by id.
    return sorted(rows, key=lambda r: (r["id"] not in order, order.get(r["id"], 0), r["id"]))


@mcp.tool()
def board() -> dict:
    """Every task, as done, held by someone, ready, or waiting (and on what)."""
    with transaction() as db:
        return {"tasks": _board(load_tasks(db), now())}


@mcp.tool()
async def wait_for_work(agent: str, timeout_s: int = 240) -> dict:
    """Wait until a task is ready for agent and claim it, trying every 5 seconds.

    Returns the claimed task, or the board when timeout_s (at most 280) passes with nothing ready.
    Call it instead of stopping when nothing is ready.
    """
    deadline = now() + max(0, min(timeout_s, MAX_WAIT_S))
    while True:
        # The tools are synchronous and FastMCP runs them on the event loop, so every database
        # call in this process is already serialized and never waits on SQLite's lock.
        result = claim_next(agent)
        if result["ok"] or now() + POLL_S > deadline:
            return result
        await asyncio.sleep(POLL_S)


# ── HTTP and auth ────────────────────────────────────────────────────────────────────────────────


class BearerAuth:
    """Pure ASGI middleware: an HTTP request needs `Authorization: Bearer <token>` with a known token.

    Pure ASGI rather than Starlette's BaseHTTPMiddleware, which buffers responses and gets in the
    way of the streamed MCP replies.
    """

    def __init__(self, app, tokens: set[str]):
        self.app, self.tokens = app, tokens

    def authorized(self, scope) -> bool:
        header = dict(scope["headers"]).get(b"authorization", b"").decode("latin-1")
        scheme, _, token = header.partition(" ")
        return scheme.lower() == "bearer" and any(hmac.compare_digest(token.strip(), t) for t in self.tokens)

    async def __call__(self, scope, receive, send):
        # Lifespan events carry no headers and must reach the app, or the MCP session manager never starts.
        if scope["type"] == "lifespan" or (scope["type"] == "http" and self.authorized(scope)):
            await self.app(scope, receive, send)
            return
        if scope["type"] == "http":
            await send({
                "type": "http.response.start",
                "status": 401,
                "headers": [(b"content-type", b"application/json"), (b"www-authenticate", b"Bearer")],
            })
            await send({"type": "http.response.body", "body": b'{"error": "missing or unknown bearer token"}'})
        # Any other scope (a websocket) is dropped unanswered: the coordinator serves none.


app = BearerAuth(mcp.streamable_http_app(), TOKENS)


def main() -> None:
    if not TOKENS:
        raise SystemExit("Set COORD_TOKENS to a comma-separated list of tokens, one per person.")
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
