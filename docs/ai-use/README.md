# How we used AI

The Space Apps submission form has a "Use of Super Intelligence (SI)" field, and the Submission
Guide requires us to show where and how AI tools were used. This folder is the record that field
is written from.

## How to log

Each team member keeps their own file here, named after their GitHub login (`UncCodes.md`), so six
branches never edit the same file. After each milestone, add one row:

| Column | What to write |
|---|---|
| Date | The day the work was done |
| Tool and model | For example "Claude Code, Claude Opus 5.5" |
| What the AI did | One sentence, specific |
| Where the output is | File, commit or PR |
| Human check | Who read, tested or changed it |

Log only what happened. If a person rewrote the AI's output, say so.

## What the Submission Guide requires

- AI may speed up the work. It may not come up with the idea of how to solve the challenge.
- **Images and videos** made by AI carry a visible watermark saying so.
- **Audio** made by AI is acknowledged in descriptive text and in metadata.
- **Code and data** made by AI are acknowledged in descriptive text and in metadata.
- AI-made content never uses or alters NASA logos, flags or mission identifiers.

How we meet the code and data rule:

- Every commit an AI agent helped write ends with a `Co-Authored-By: Claude ...` line. List them with
  `git log --format='%h %an %s %(trailers:key=Co-Authored-By,valueonly)'`.
- The public README states that the project was built with Claude Code.
- Any text the product's assistant generates (summaries, interpretations) is labelled as
  AI-generated on screen, and stored with the model's name beside it.
- Data taken from NASA is never altered by AI. A file an AI derived from it says so in its header.

## Team to confirm before submitting

These are facts only the team knows. Do not fill them in by guessing.

- [ ] Who came up with the FLARE idea, and that it was not an AI tool.
- [x] The team logo is the team's own work, not made with AI (confirmed 2026-11-15). The AI-made
      `Logo.jpg` was replaced by the logos in `brand/`, so it needs no watermark.
- [ ] Every AI tool used outside this repo (chat assistants, image tools, translation).

## AI inside the product

The assistant will use Claude Opus 5.5 through the Anthropic API (decided 14 November 2026). This
is not built yet. When it is, record here what it generates and how its output is labelled.
