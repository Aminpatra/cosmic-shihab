# Submission form: what goes in each field

For the team member who fills in the Project Submission page. Each field below says what to paste
and from where. Paste the text of a file **without** its closing `<!-- … -->` comment, which holds
our sources and is not for the form. Only the last saved submission is judged, so it can be saved
and corrected until the deadline: **Sunday 15 November 2026, 11:59 p.m. local time.**

| Field | What to paste |
|---|---|
| **Project Name** | `FLARE: Fire Learning, Analysis & Research Explorer` |
| **High-Level Project Summary** | The "Summary" section of `description.md` (one paragraph). |
| **Link to Project Demo** | `https://cosmic-shihab.vercel.app/pitch.html`, the 7-slide deck (#90). Live: it answered 200 on 15 November 2026. Open it in a private window before pasting it, and see the deck item in the checklist below. |
| **Link to Final Project** | `https://cosmic-shihab.vercel.app` |
| **Detailed Project Description** | `description.md` from "The solution" to "Team", then the short version of the ranking: the first paragraph of `ranking.md` and its "An example" table. Add a line: "Method, limitations, impact and our test report: https://github.com/Aminpatra/cosmic-shihab/tree/main/submission". |
| **Use of Super Intelligence (SI)** | `ai_use.md`, all of it above the comment. |
| **NASA Data** | `datasets.md`, all of it above the comment. |
| **Space Agency Partner Data and Other References** | First the line "No space agency partner data was used; FLARE uses NASA PSI data only." Then `references.md`, all of it above the comment. |

If a field turns out to have a length limit, keep the first paragraph and link the rest of the file
on GitHub (`https://github.com/Aminpatra/cosmic-shihab/blob/main/submission/<file>`).

## Before pressing Submit

Things only a person can do, from `CRITERIA.md`:

- [ ] Challenge selected: **Flame in Freefall**.
- [ ] All six members registered for the same Local Event (none waitlisted) and shown on the
      Members tab: Amin Mohamed Amin, Gheath Wahab, Mohammed Al-julandani, Samin Rezaei, Rahaf
      Abubaker Mustafa Mubarak, Ruayma Khair Mohammed Albalushi.
- [x] The deck shows the team name, the six members' names and the challenge. Since #99, slide 7
      shows "Cosmic Shihab", "NASA Space Apps Challenge 2026 · Flame in Freefall" and the six
      names; the deck has 7 slides, is in English and keeps the "Illustration made with AI" mark.
      Check once the redeploy is live that https://cosmic-shihab.vercel.app/pitch.html shows them.
- [ ] Every link opens in a private browser window with no login: the deck, the live site, and
      the GitHub links.
- [ ] Recount the AI co-authored commits for `ai_use.md` (the command is in its comment) if more
      PRs merge before submitting.
- [ ] Optional but recommended: request a FortiGuard Web Filter Classification for
      `cosmic-shihab.vercel.app` (company name "N/A") so judges' networks don't block it.
- [ ] Both checkboxes ticked: the Submission Guide, Terms and Privacy agreement, and the
      original-work declaration.
- [ ] Images uploaded to the page, if any, are JPG, PNG or GIF up to 10 MB
      (`pitch/site-qr.png` is the site's QR code).

## Already checked

- Live site and every concrete check: `test_report.md` (15 November 2026, all passing).
- No image or video shows anyone under 18; the pitch uses three NASA public-domain portraits of the
  Apollo 1 crew.
- No AI-made content uses or alters NASA logos, flags or mission identifiers (`ai_use.md`).

<!--
For the team (not for the form). Issue #15. Field list and rules: CRITERIA.md "From the Project
Submission Guide" and "Hard requirements". Deck location: decided by @Aminpatra on 15 Nov 2026
(live site, /pitch.html; a static file must contain a dot, docs/DECISIONS.md #14). The deck itself
is the team's separate work. Apollo 1 portraits: submission/pitch/flare-opening.html header
(public domain: S64-32110, S66-35219, S64-31447). Partner data: none is used (datasets.md,
references.md list NASA PSI only).
Deck check, 15 Nov 2026, main at 3e617c0: submission/pitch/FlareOpening.jsx has SLIDE_COUNT = 7;
its on-screen TEXT holds the team name "Cosmic Shihab" and the AI watermark, but no member's name,
and "Flame in Freefall" appears only in a source comment. frontend/public/pitch.html is byte for
byte submission/pitch/flare-opening.html (#90), and GET /pitch.html on the live site answered 200.
-->
