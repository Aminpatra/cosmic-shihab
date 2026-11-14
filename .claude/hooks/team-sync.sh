#!/usr/bin/env bash
# Team-sync digest: a compact snapshot of what the other Claude agents on this
# repo are doing. Runs at session start (.claude/settings.json) and on demand.
# Never fails the session: every step is time-limited and the script exits 0.
set -u

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}" 2>/dev/null || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
export GIT_TERMINAL_PROMPT=0 GH_PROMPT_DISABLED=1 NO_COLOR=1 GH_NO_UPDATE_NOTIFIER=1

DECISIONS=docs/DECISIONS.md
MAX_LINES=70

# limit <seconds> <command...>: run a command, kill it if it overruns (macOS has no `timeout`).
limit() {
  local secs=$1; shift
  "$@" &
  local pid=$!
  ( sleep "$secs"; kill "$pid" 2>/dev/null ) >/dev/null 2>&1 &
  local watchdog=$!
  wait "$pid" 2>/dev/null; local rc=$?
  kill "$watchdog" 2>/dev/null; wait "$watchdog" 2>/dev/null
  return $rc
}

# in_flight <base> <current-branch>: one line per unmerged remote branch with the areas it touches.
in_flight() {
  local base=$1 branch=$2 ref author when n areas mine
  git for-each-ref --sort=-committerdate --count=14 \
      --format='%(refname:short)|%(authorname)|%(committerdate:relative)' refs/remotes/origin |
  while IFS='|' read -r ref author when; do
    if [ "$ref" = "$base" ] || [ "$ref" = origin ] || [ "$ref" = origin/HEAD ]; then continue; fi
    mine=""
    [ "$ref" = "origin/$branch" ] && mine=" (yours)"
    n=$(git rev-list --count "$base..$ref" 2>/dev/null || echo 0)
    if [ "$n" = 0 ]; then
      areas="no commits yet"
    else
      areas=$(git diff --name-only "$base...$ref" 2>/dev/null |
        awk -F/ '{ k = (NF > 2) ? $1 "/" $2 "/" : (NF > 1 ? $1 "/" : $0); c[k]++ }
                 END { for (k in c) print c[k], k }' |
        sort -rn | head -6 | awk '{ printf "%s%s(%s)", (NR > 1 ? " " : ""), $2, $1 }')
    fi
    echo "  ${ref#origin/}${mine} | $author, $when | $areas"
  done
}

digest() {
  local gitdir stale="" base branch login="" have_gh=0 have_base=0
  gitdir=$(git rev-parse --git-dir)

  limit 10 git fetch -q --prune origin 2>/dev/null || stale=" (offline: showing last fetched state)"

  base=$(git symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null)
  [ -n "$base" ] || base=origin/main
  git rev-parse -q --verify "$base" >/dev/null 2>&1 && have_base=1
  branch=$(git symbolic-ref -q --short HEAD 2>/dev/null || echo detached)

  if command -v gh >/dev/null 2>&1 && limit 6 gh auth token >/dev/null 2>&1; then
    have_gh=1
    login=$(cat "$gitdir/team-sync-login" 2>/dev/null)
    if [ -z "$login" ]; then
      login=$(limit 6 gh api user --jq .login 2>/dev/null)
      [ -n "$login" ] && printf '%s' "$login" > "$gitdir/team-sync-login"
    fi
  fi

  # --- Where you stand -----------------------------------------------------
  local head="[team-sync]${stale} you=${login:+@}${login:-unknown} branch=$branch"
  local behind=0 ahead=0 dirty
  if [ "$have_base" = 1 ] && git rev-parse -q --verify HEAD >/dev/null 2>&1; then
    set -- $(git rev-list --left-right --count "$base...HEAD" 2>/dev/null)
    behind=${1:-0}; ahead=${2:-0}
    head="$head | ${behind} behind, ${ahead} ahead of ${base#origin/}"
  fi
  dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  [ "$dirty" != 0 ] && head="$head | $dirty uncommitted files"
  echo "$head"

  if [ "$have_base" = 0 ]; then
    echo "  origin has no ${base#origin/} branch yet: nothing to sync against."
  else
    [ "$behind" != 0 ] && echo "  -> main moved: commit, then merge origin/main into this branch before continuing."
    [ "$branch" = "${base#origin/}" ] && echo "  -> you are on ${base#origin/}: do not edit; ask your human to run /team-claim."
  fi

  # --- Claims (open issues) ------------------------------------------------
  if [ "$have_gh" = 1 ]; then
    local issues
    issues=$(limit 8 gh issue list --state open --limit 30 --json number,title,assignees --jq \
      '.[] | "  #\(.number) \(.title[0:64]) : \(if (.assignees|length) > 0 then (.assignees | map("@" + .login) | join(" ")) else "UNCLAIMED" end)"' 2>/dev/null)
    echo "Tasks (open issues : owner):"
    echo "${issues:-  none}"
  else
    echo "Tasks: unavailable (install GitHub CLI and run 'gh auth login' to see claims)."
  fi

  # --- In flight (unmerged remote branches and the areas they touch) --------
  if [ "$have_base" = 1 ]; then
    local rows
    rows=$(in_flight "$base" "$branch")
    echo "In flight (branch | last push | areas touched):"
    echo "${rows:-  none}"
  fi

  # --- Open PRs ------------------------------------------------------------
  if [ "$have_gh" = 1 ]; then
    local prs
    prs=$(limit 8 gh pr list --state open --limit 15 --json number,title,author,headRefName,isDraft --jq \
      '.[] | "  #\(.number) \(.title[0:64]) : @\(.author.login) (\(.headRefName))\(if .isDraft then " draft" else "" end)"' 2>/dev/null)
    [ -n "$prs" ] && { echo "Open PRs:"; echo "$prs"; }
  fi

  # --- What landed on main that this checkout does not have yet -------------
  if [ "$have_base" = 1 ] && [ "$behind" != 0 ]; then
    echo "New on main since your branch:"
    git log -8 --format='  %h %s (%an, %cr)' "HEAD..$base" 2>/dev/null
    [ "$behind" -gt 8 ] && echo "  ... and $((behind - 8)) more"
  fi

  # --- Team decisions (from main when available, so they are never stale) ---
  local entries="" total
  [ "$have_base" = 1 ] && entries=$(git show "$base:$DECISIONS" 2>/dev/null | grep '^- ')
  [ -z "$entries" ] && [ -f "$DECISIONS" ] && entries=$(grep '^- ' "$DECISIONS" 2>/dev/null)
  if [ -n "$entries" ]; then
    total=$(printf '%s\n' "$entries" | wc -l | tr -d ' ')
    echo "Decisions ($DECISIONS, latest $([ "$total" -gt 20 ] && echo 20 || echo "$total") of $total):"
    printf '%s\n' "$entries" | tail -20 | sed 's/^/  /'
  fi
}

digest 2>/dev/null | head -n "$MAX_LINES"
exit 0
