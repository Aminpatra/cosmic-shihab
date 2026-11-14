---
name: usage-aware
description: Keeps Claude aware of the Claude Code tokens and credits it is spending, using local ccusage evidence. Use at the start of any large task (a new feature, a refactor, training a model, generating media), after each major milestone, whenever the user mentions credits, usage, budget, tokens, quota, limits or cost, when a budget warning appears, and when the user asks why usage was high or which model costs more. Reports today's burn and the live 5-hour block, then adjusts how the work is done.
---

# Usage aware

Repackaged from [daymade/claude-code-skills `claude-usage-analyst`](https://github.com/daymade/claude-code-skills)
(MIT, © 2025 daymade). Changes: Claude may invoke it on its own at checkpoints, it uses the
machine's timezone, it runs on Windows without extra packages, and it adds a short checkpoint mode
and the guidance on what to do with the numbers.

## Checkpoint (the default, a few seconds)

```bash
python "${CLAUDE_SKILL_DIR}/scripts/analyze_claude_usage.py" --checkpoint
```

Use `python3` where `python` isn't Python 3. It needs Node.js for ccusage (it falls back to
`npx ccusage@latest` when ccusage isn't installed globally).

Run it:
- before starting anything large, so you can say roughly what it will cost relative to what's left;
- after each milestone, in one line to the user ("That feature took about X of today's usage.");
- whenever the user raises usage, or a spendcap warning shows up in the conversation.

Don't run it on every turn. Each run costs a tool call.

## What to do with the numbers

Say them plainly, then act. In order of how much they save:

1. **Stop re-reading.** Most burn is cache reads: the same large context sent again on every turn.
   Read the specific lines you need (Grep first, then a ranged Read), not whole files again.
2. **Suggest `/compact`** when the conversation is long and the next task doesn't need its
   history, or **`/clear` plus a handoff** (the `handoff` skill) when switching to unrelated work.
3. **Fewer, bigger steps.** Batch questions to the user, batch independent tool calls, and avoid
   screenshot-check-fix loops: verify with text tools (page text, computed styles) and take one
   screenshot at the end.
4. **Don't spawn subagents** unless the user asked; each one starts from zero and re-reads context.
5. **Suggest a cheaper model** for routine work (the user switches it in the model picker; you
   can't), and the `caveman` skill for terse replies when the budget is tight.
6. If the user has set a budget (spendcap), tell them when a task you're about to start would
   likely cross it, and let them decide.

Never cut corners on correctness to save tokens without saying so.

## Full analysis (when the user asks why usage was high)

```bash
python "${CLAUDE_SKILL_DIR}/scripts/analyze_claude_usage.py" --since YYYY-MM-DD --until YYYY-MM-DD
python "${CLAUDE_SKILL_DIR}/scripts/analyze_claude_usage.py" --model-a opus --model-b sonnet
```

Defaults are today in the local timezone. For historical comparison, set `--since` to an earlier
date; otherwise rank and median fields only describe the single day. Read
`references/explanation-guide.md` before writing the answer.

## Evidence rules

- Base numeric claims on `ccusage` output or the bundled analyzer output.
- State the scope: `ccusage claude` measures local Claude Code usage logs, including Claude
  Desktop's Claude Code sessions when those local logs exist. It isn't a complete Claude.ai bill.
- Dollar figures are estimates at API list price. On a Pro or Max plan they show relative burn,
  not money spent; say "quota pressure" rather than inventing plan limits.
- Explain cache plainly: cache reads are still usage even though nobody typed those words.
- When comparing models, compare both token volume and estimated cost.

## Output shape for a full analysis

1. Short conclusion in plain language.
2. Evidence table: total tokens, cost, input, output, cache create, cache read.
3. Model comparison table.
4. 5-hour block table when quota is the question.
5. Why the burn happened.
6. Confidence and caveats.

Keep it readable for non-technical users; translate any term like "cache read" in one sentence.
