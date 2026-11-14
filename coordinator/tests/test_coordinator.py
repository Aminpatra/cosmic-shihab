"""Coordinator logic, tested by calling the tools directly (not over HTTP), plus the auth layer."""

import threading

from starlette.testclient import TestClient

import server


def claimed_id(result):
    assert result["ok"], result
    return result["task"]["id"]


# ── Readiness ────────────────────────────────────────────────────────────────────────────────────


def test_blocked_task_is_ready_only_after_its_blocker_completes(clock):
    server.add_task(1, "Build the API", touches=["backend/*"])
    server.add_task(2, "Build the pages", blocked_by=[1], touches=["frontend/*"])

    assert claimed_id(server.claim_next("alice")) == 1
    assert server.claim_next("bob") == {"ok": False, "reason": "nothing is ready", "board": [
        {"id": 1, "title": "Build the API", "state": "held by alice until 2027-01-15T08:30:00Z"},
        {"id": 2, "title": "Build the pages", "state": "waiting: blocked by #1"},
    ]}
    assert server.claim("bob", 2)["ok"] is False

    assert server.complete("alice", 1)["ok"]
    assert claimed_id(server.claim_next("bob")) == 2


def test_unknown_blocker_counts_as_closed(clock):
    server.add_task(5, "Depends on an issue that is not on the board", blocked_by=[999])
    assert claimed_id(server.claim_next("alice")) == 5


def test_overlapping_touches_hold_back_the_second_task(clock):
    server.add_task(1, "Explorer page", touches=["frontend/src/pages/Explorer*"])
    server.add_task(2, "Shell restyle", touches=["frontend/*"])
    server.add_task(3, "Ranking", touches=["backend/app/routes/rank.py"])

    assert claimed_id(server.claim("alice", 1)) == 1
    states = {row["id"]: row["state"] for row in server.board()["tasks"]}
    assert states[2] == "waiting: overlaps #1 held by alice"
    assert states[3] == "ready"
    assert claimed_id(server.claim_next("bob")) == 3  # 2 is skipped, not handed out

    server.release("alice", 1)
    assert claimed_id(server.claim_next("carol")) == 1  # lowest id among equals; 2 now overlaps carol's


def test_globs_overlap_by_prefix_before_the_first_star():
    assert server.globs_overlap("frontend/*", "frontend/src/pages/Home.jsx")
    assert server.globs_overlap("backend/app/*", "backend/*")
    assert not server.globs_overlap("backend/*", "frontend/*")
    assert not server.globs_overlap("pipeline/a.py", "pipeline/b.py")


def test_task_that_unblocks_the_most_goes_first(clock):
    server.add_task(1, "Leaf, high priority", priority=5)
    server.add_task(2, "Unblocks one", priority=0)
    server.add_task(3, "Unblocks two", priority=0)
    server.add_task(10, "Waits on 2 and 3", blocked_by=[2, 3])
    server.add_task(11, "Waits on 3", blocked_by=[3])

    order = [row["id"] for row in server.board()["tasks"]][:3]
    assert order == [3, 2, 1]  # unblocks 2, then 1, then priority breaks the tie among the rest
    assert claimed_id(server.claim_next("alice")) == 3


def test_add_task_upserts_without_touching_the_holder(clock):
    server.add_task(7, "Old title")
    server.claim("alice", 7)
    task = server.add_task(7, "New title", touches=["docs/x.md"], priority=2)["task"]
    assert (task["title"], task["owner"], task["touches"], task["priority"]) == ("New title", "alice", ["docs/x.md"], 2)


# ── The race ─────────────────────────────────────────────────────────────────────────────────────


def test_twenty_simultaneous_claims_produce_exactly_one_winner(clock):
    server.add_task(1, "The only ready task")
    start = threading.Barrier(20)
    results = [None] * 20

    def agent(i):
        start.wait()  # release all twenty at the same moment
        results[i] = server.claim_next(f"agent{i}")

    threads = [threading.Thread(target=agent, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    winners = [r["task"]["owner"] for r in results if r["ok"]]
    assert len(winners) == 1
    assert server.board()["tasks"][0]["state"].startswith(f"held by {winners[0]}")


# ── Leases ───────────────────────────────────────────────────────────────────────────────────────


def test_expired_lease_makes_the_task_claimable_again(clock):
    server.add_task(1, "Task")
    server.claim("alice", 1)
    clock.advance(29)
    assert server.claim("bob", 1)["ok"] is False
    clock.advance(2)  # 31 minutes after the claim
    assert server.claim("bob", 1)["task"]["owner"] == "bob"


def test_heartbeat_extends_the_lease(clock):
    server.add_task(1, "Task")
    server.claim("alice", 1)
    clock.advance(20)
    assert server.heartbeat("alice", 1)["ok"]
    clock.advance(20)  # 40 minutes after the claim, 20 after the heartbeat
    assert server.claim("bob", 1)["ok"] is False
    clock.advance(11)
    assert server.claim("bob", 1)["ok"] is True


def test_heartbeat_does_not_revive_an_expired_lease(clock):
    server.add_task(1, "Task")
    server.claim("alice", 1)
    clock.advance(31)
    assert "ran out" in server.heartbeat("alice", 1)["reason"]


def test_others_cannot_heartbeat_complete_or_release_your_task(clock):
    server.add_task(1, "Task")
    server.claim("alice", 1)
    for tool in (server.heartbeat, server.complete, server.release):
        result = tool("bob", 1)
        assert result == {"ok": False, "reason": "#1 is not yours (held by alice)"}
    state = server.board()["tasks"][0]["state"]
    assert state.startswith("held by alice")


def test_complete_works_after_the_lease_ran_out_if_nobody_took_over(clock):
    server.add_task(1, "Task")
    server.claim("alice", 1)
    clock.advance(120)  # the PR merged two hours later
    assert server.complete("alice", 1)["ok"]
    assert server.board()["tasks"][0]["state"] == "done (by alice)"


# ── Auth ─────────────────────────────────────────────────────────────────────────────────────────


INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}},
}
HEADERS = {"Accept": "application/json, text/event-stream"}


def test_request_without_a_valid_token_gets_401():
    client = TestClient(server.BearerAuth(server.mcp.streamable_http_app(), {"good-token"}))
    for headers in ({}, {"Authorization": "Bearer wrong"}, {"Authorization": "good-token"}):
        response = client.post("/mcp", json=INITIALIZE, headers=HEADERS | headers)
        assert response.status_code == 401, headers


def test_valid_token_reaches_mcp_and_lifespan_passes_through():
    # Entering the client runs the lifespan; if the middleware swallowed it, the MCP session
    # manager would not be running and this request would fail.
    with TestClient(server.BearerAuth(server.mcp.streamable_http_app(), {"good-token"})) as client:
        response = client.post("/mcp", json=INITIALIZE, headers=HEADERS | {"Authorization": "Bearer good-token"})
    assert response.status_code == 200
    assert "flare-coordinator" in response.text
