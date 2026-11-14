# Team sync: you are not the only agent here

Six people each run their own Claude agent on this repo, in parallel, on separate machines. Agents cannot talk to each other. The only shared state is GitHub: **issues = who owns which task, branches and PRs = work in progress, main = truth**. The humans sit together, so any ownership question is settled by asking yours. `CLAUDE.md` governs how to build; this file only covers staying in sync.

A `[team-sync]` digest is injected at session start: open tasks and owners, in-flight branches and the areas they touch, open PRs, team decisions. If it is missing, run `bash .claude/hooks/team-sync.sh` before your first edit.

- **Work only on a claimed task, on its branch.** Never commit on main. If nothing is claimed, ask your human to run `/team-claim <issue# or short description>`.
- **Stay out of other people's areas.** If the digest shows another branch touching files your task needs, tell your human before editing them.
- **You commit, your human publishes.** Commit after each working step, as `CLAUDE.md` says. Never push, open a PR or merge on your own; that happens only inside these three commands, which your human types:
  - `/team-claim` takes a task and publishes its branch.
  - `/team-sync` merges the latest main into the branch and pushes your commits. Suggest it at natural stopping points and when the digest says main moved, because unpushed work is invisible to the other agents.
  - `/team-pr` opens the pull request when the task is done; its description is the note other agents read. (`/handoff` is different: it passes this conversation to a fresh session.)
- **Record cross-task agreements** (API contract, data shape, env var, new dependency) as one line in `docs/DECISIONS.md`, on the same branch. Skill and stack choices still go in `CLAUDE.md`.
- **Read on demand.** Trust the digest; open an issue or PR (`gh issue view N`, `gh pr view N`) only when it bears on your task.
