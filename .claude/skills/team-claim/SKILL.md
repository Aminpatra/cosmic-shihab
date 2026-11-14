---
name: team-claim
description: Claim a task so the other Claude agents on this repo know it is taken. Claims it in the coordinator, assigns the GitHub issue (creating one if needed) and publishes a branch from fresh main.
argument-hint: <issue number | short task description>
disable-model-invocation: true
---

Claim this task for the current user: $ARGUMENTS

The human typed this command, so pushing the branch is authorized.

1. **Refresh.** Run `bash .claude/hooks/team-sync.sh` and read the digest. If the working tree has uncommitted changes from other work, stop and ask the human what to do with them.
2. **Resolve the task to an issue.**
   - A number: `gh issue view <n> --json number,title,state,assignees`. If it is assigned to someone else, stop and tell the human who holds it.
   - A description: if an open issue in the digest already covers it, use that one. Otherwise create it: `gh issue create --title "<imperative, under 60 chars>" --body "<one or two lines: scope and the files or areas it will touch>"`.
3. **Check for overlap.** Compare the areas this task will touch with "In flight" in the digest. If another branch is already in those areas, tell the human which branch and whose it is, and wait for their call.
4. **Claim it, coordinator first.** With `agent` = `gh api user -q .login`:
   - Call the coordinator's `claim(agent, <n>)`. If it answers that the task is not on the board, register it with `add_task` (number, title, `blocked_by` from the issue's "Depends on", `touches` from the areas it edits) and claim again.
   - If the claim is refused (held by someone else, blocked, or overlapping held work), stop and tell the human why. Don't assign the issue.
   - Only after `ok: true`: `gh issue edit <n> --add-assignee @me`, for visibility.
   - If the coordinator can't be reached, say so and fall back to `gh issue edit <n> --add-assignee @me` alone.
5. **Branch from fresh main and publish it** so the claim shows up in everyone's digest:
   ```
   git fetch origin
   git switch -c <feat|fix|chore>/<n>-<short-slug> origin/main
   git push -u origin HEAD
   ```
6. **Report in one line:** issue number, branch name, and any overlap the human should know about. Then start the work, following `CLAUDE.md`.
