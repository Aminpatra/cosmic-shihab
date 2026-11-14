---
name: team-sync
description: Catch this checkout up with the team. Refreshes the team digest, merges the latest main into the current branch, and pushes local commits so the other agents can see them.
disable-model-invocation: true
---

The human typed this command, so pushing the current task branch is authorized. Never push to main.

1. **Refresh.** Run `bash .claude/hooks/team-sync.sh` and read the digest.
2. **Catch up with main**, if the digest says this checkout is behind:
   - On main: `git pull --ff-only origin main`.
   - On a task branch: commit work in progress first (a `wip:` commit is fine), then `git merge origin/main`. Use merge, not rebase, because the branch is already published.
   - On a conflict: resolve it when both sides are clearly compatible. If the other side comes from someone else's task and the right resolution is not obvious, stop and ask the human; the author is sitting nearby.
3. **Publish.** If the task branch has unpushed commits, `git push`.
4. **Report in two lines at most:** what landed on main that affects the current task (new dependency, changed interface, new decision), or "nothing relevant". If new dependencies landed, run the project's install step.
