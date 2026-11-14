---
name: team-pr
description: Finish the current task and give it to the team. Syncs with main, records shared decisions, pushes, and opens a pull request whose description is the note other agents read.
argument-hint: [optional note, e.g. "unfinished: map layer still missing"]
disable-model-invocation: true
---

Open the pull request for the work on the current branch. Extra note from the human: $ARGUMENTS

The human typed this command, so pushing the branch and opening the PR are authorized. This is not `/handoff`, which passes a conversation to a fresh session.

1. **Verify.** Follow `verification-before-completion`: run the checks this task defined and the project's build or tests. If something fails and cannot be fixed now, carry on but say so in the PR.
2. **Sync.** `git fetch origin && git merge origin/main`. Resolve conflicts; if one involves someone else's task and the answer is not obvious, ask the human.
3. **Record agreements.** If this work set an API contract, data shape, env var, new dependency or convention that other tasks must follow, append one line each to `docs/DECISIONS.md`:
   `- YYYY-MM-DD @github-login: the agreement, in one sentence (#issue)`
4. **Commit and push** everything on the branch.
5. **Open the PR** with `gh pr create`. Title: what the change does, imperative. Body, 15 lines at most, because other agents read it:
   ```
   Closes #<issue>   (or "Part of #<issue>" if unfinished)

   ## What changed
   - up to 5 bullets, by area

   ## New dependencies, env vars, commands
   - or "none"

   ## Others should know
   - changed interfaces, things left unfinished, follow-ups
   ```
   If the work is unfinished, open it as a draft (`--draft`) and unassign yourself from the issue (`gh issue edit <n> --remove-assignee @me`) so someone else can claim it.
6. **Merge.** Ask the human whether to merge now. If yes: `gh pr merge --squash --delete-branch`, then `git switch main && git pull --ff-only origin main`. Finished work that is not merged stays invisible on main.
7. **Report:** the PR link, merged or not, and anything the human should say out loud to the team.
