# Team sync: you are not the only agent here

Six people each run their own Claude agent on this repo, in parallel, on separate machines. Agents cannot talk to each other. They share two things: **the coordinator** (an MCP server, see `coordinator/README.md`) is the source of truth for who holds which task and which tasks are ready; **GitHub** holds the rest: issues = task descriptions, branches and PRs = work in progress, main = truth. The humans sit together, so any ownership question is settled by asking yours. `CLAUDE.md` governs how to build; this file only covers staying in sync.

A `[team-sync]` digest is injected at session start: open tasks and owners, in-flight branches and the areas they touch, open PRs, team decisions. If it is missing, run `bash .claude/hooks/team-sync.sh` before your first edit.

## The coordinator

Its tools appear as `coordinator`. Every call that acts for someone takes `agent` = your human's GitHub login (`gh api user -q .login`).

- **Claim through it.** `claim_next(agent)` hands out the best ready task (blockers done, no overlap with held work); `claim(agent, task_id)` takes a specific one. The claim is atomic: if it answers `ok: true`, the task is yours. Then, for visibility, assign the GitHub issue to yourself and create its branch, as `/team-claim` does.
- **Heartbeat after every commit.** `heartbeat(agent, task_id)`. A claim is a 30-minute lease; if you stop renewing it, someone else may take the task.
- **Complete once the PR merges.** `complete(agent, task_id)`. Use `release(agent, task_id)` instead if you stop without finishing.
- **Don't stop when nothing is ready.** Call `wait_for_work(agent)`; it claims a task as soon as one is free. While waiting, review open PRs (`gh pr list`, `gh pr view N`) and tell your human what you found.
- **Register new issues.** When an issue is created, call `add_task` with its number, title, the issue numbers it depends on (`blocked_by`) and the paths it edits (`touches`, as globs such as `frontend/src/pages/Explorer*`). Leave out files every task appends to (`docs/DECISIONS.md`, `docs/ai-use/*`).
- **`board()`** shows every task as done, held, ready or waiting, and on what.
- **If the coordinator can't be reached** (not configured, tunnel down, 401), fall back to the GitHub-only flow below and tell your human.

## Rules

- **Work only on a claimed task, on its branch.** Never commit on main. If nothing is claimed, ask your human to run `/team-claim <issue# or short description>`.
- **Catch up on your own.** When the digest says main moved, commit your work and run `git merge origin/main` (on main: `git pull --ff-only origin main`) before continuing. This is local, so it needs no permission; ask your human only when a conflict involves someone else's task. Rerun the digest before starting each new task.
- **Stay out of other people's areas.** If the digest or `board()` shows another task touching files your task needs, tell your human before editing them.
- **You commit, your human publishes.** Commit after each working step, as `CLAUDE.md` says. Never push, open a PR or merge on your own; that happens only inside these three commands, which your human types:
  - `/team-claim` takes a task and publishes its branch.
  - `/team-sync` catches up and pushes your commits. Suggest it at natural stopping points, because unpushed work is invisible to the other agents.
  - `/team-pr` opens the pull request when the task is done; its description is the note other agents read. (`/handoff` is different: it passes this conversation to a fresh session.)
- **Record cross-task agreements** (API contract, data shape, env var, new dependency) as one line in `docs/DECISIONS.md`, on the same branch. Skill and stack choices still go in `CLAUDE.md`.
- **Read on demand.** Trust the digest; open an issue or PR (`gh issue view N`, `gh pr view N`) only when it bears on your task.
