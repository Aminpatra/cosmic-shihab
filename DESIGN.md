---
name: FLARE
description: Fire Learning, Analysis & Research Explorer. NASA microgravity combustion investigations read as test records against your scenario.
colors:
  deep-blue: "#07173F"
  electric-blue: "#0042A6"
  neon-blue: "#0960E1"
  blue-yonder: "#2E96F5"
  neon-yellow: "#EAFE07"
  neon-yellow-lift: "#F2FF5C"
  rocket-red: "#E43700"
  white: "#FFFFFF"
  ramp-1: "#0A1D4D"
  ramp-2: "#0E2760"
  ramp-3: "#28467F"
  ramp-4: "#5C77AE"
  ramp-5: "#B9C6E4"
  ramp-6: "#E6ECF8"
  on-electric: "#D3DEFA"
  band-fill: "rgb(46 150 245 / 0.42)"
typography:
  display:
    fontFamily: "Fira Sans, Segoe UI, sans-serif"
    fontSize: "clamp(2.25rem, 1.4rem + 2.8vw, 3.25rem)"
    fontWeight: 900
    lineHeight: 1.04
    letterSpacing: "0.03em"
  headline:
    fontFamily: "Overpass, Segoe UI, sans-serif"
    fontSize: "clamp(1.625rem, 1.2rem + 1.4vw, 2.25rem)"
    fontWeight: 400
    lineHeight: 1.2
  title:
    fontFamily: "Overpass, Segoe UI, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.05em"
  lede:
    fontFamily: "Overpass, Segoe UI, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 300
    lineHeight: 1.5
  body:
    fontFamily: "Overpass, Segoe UI, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.55
  data:
    fontFamily: "Overpass, Segoe UI, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    fontFeature: "tnum"
  label:
    fontFamily: "Overpass, Segoe UI, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 700
    letterSpacing: "0.06em"
  footnote:
    fontFamily: "Overpass, Segoe UI, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.6
  identifier:
    fontFamily: "Fira Code, ui-monospace, monospace"
    fontSize: "0.92em"
    fontWeight: 400
rounded:
  radius: "4px"
spacing:
  "1": "0.25rem"
  "2": "0.5rem"
  "3": "0.75rem"
  "4": "1rem"
  "5": "1.5rem"
  "6": "2rem"
  "7": "3rem"
  "8": "4.5rem"
  "9": "6rem"
  gutter: "clamp(1rem, 0.2rem + 4vw, 4.5rem)"
  bar-height: "4rem"
components:
  button-primary:
    backgroundColor: "{colors.neon-yellow}"
    textColor: "{colors.deep-blue}"
    rounded: "{rounded.radius}"
    padding: "0.85rem 1.4rem 0.75rem"
    height: "3rem"
  button-primary-hover:
    backgroundColor: "{colors.neon-yellow-lift}"
    textColor: "{colors.deep-blue}"
  button-quiet:
    backgroundColor: "transparent"
    textColor: "{colors.white}"
    rounded: "{rounded.radius}"
    padding: "0.6rem 1rem 0.5rem"
    height: "2.5rem"
  top-bar:
    backgroundColor: "{colors.electric-blue}"
    textColor: "{colors.white}"
    height: "{spacing.bar-height}"
    padding: "0 {spacing.gutter}"
  nav-link:
    textColor: "{colors.white}"
    height: "{spacing.bar-height}"
    padding: "0.2rem 0.8rem 0"
  nav-link-pending:
    textColor: "{colors.on-electric}"
  lane-track:
    backgroundColor: "{colors.ramp-1}"
    height: "2.25rem"
  lane-band:
    backgroundColor: "{colors.band-fill}"
  scenario-tick:
    backgroundColor: "{colors.neon-yellow}"
    width: "3px"
  lane-lifted:
    backgroundColor: "{colors.ramp-2}"
    textColor: "{colors.ramp-6}"
  catalogue-cell:
    backgroundColor: "{colors.band-fill}"
    height: "2.6rem"
---

# Design System: FLARE

## Overview

**Creative North Star: "The Microgravity Test Record"**

FLARE reads like the log sheet of a combustion experiment, not a dashboard. Every comparison is a set of horizontal lanes, one per condition, laid on a shared measurement grid: the visitor's scenario is a Neon Yellow tick, an investigation's tested range is a translucent Blue Yonder band, and anything PSI never recorded is hatched. The world is the pinned NASA Space Apps brand palette on a Deep Blue ground, with every neutral drawn from one stepped blue ramp.

The system is flat and dense in the way a test record is dense: one text size inside data regions, rank carried by weight and case rather than by size, hairline rules dividing regions instead of cards or shadows. Provenance sits beside every claim, in a footnote under the figure that names the source column. Nothing is decorative; what is missing is drawn as missing.

The system refuses the category default for research tools: a sidebar dashboard of stat tiles and investigation cards.

**Key Characteristics:**
- Deep Blue ground, Electric Blue top bar as the shell's one committed colour field.
- Lanes on a shared grid: band for tested, tick for the scenario, hatch for not recorded.
- Neon Yellow has one job family: what can be acted on, focus, and where the scenario sits.
- Flat surfaces, hairline rules, 4px corners, no cards.
- Every result stated in words with an icon; colour never carries meaning alone.

## Colors

The NASA Space Apps brand palette (guidelines updated 25 June 2026), pinned and not reinterpreted, plus one stepped blue ramp for every neutral.

### Primary
- **Deep Blue** (deep-blue): the page ground everywhere, and the text colour on Neon Yellow. Body text sits only on Deep Blue, Electric Blue or White.
- **Electric Blue** (electric-blue): the top bar and the phone menu panel; the shell's single colour field.

### Secondary
- **Blue Yonder** (blue-yonder): data. The edge of every tested-range band, list markers, the "match" icon. Its translucent form (band-fill) fills bands, tested stops and ranked catalogue cells.
- **Neon Blue** (neon-blue): part of the pinned palette, held in reserve; no current surface uses it.

### Tertiary
- **Neon Yellow** (neon-yellow): the accent. The primary button, link text, focus rings, the active nav underline, text selection, the scenario tick and the frame on the visitor's stop or pair cell. Its lighter lift (neon-yellow-lift) is the primary button's hover only.
- **Rocket Red** (rocket-red): only the icon of a labelled "Differs" result. Never a background, never unlabelled.

Martian Red is in the brand palette but unused by the build; add it only with a role.

### Neutral
- **The Blue Ramp** (ramp-1 to ramp-6, with Deep Blue as step 0): ramp-1 is the lane track and raised bands (the catalogue section, error panel); ramp-2 is the hover and focus lift; ramp-3 is hairline rules and unit ticks; ramp-4 is hatch strokes, inactive marks and quiet borders; ramp-5 is secondary text (9.5:1 on ramp-1); ramp-6 is lede text and lifted readouts.
- **On-Electric Periwinkle** (on-electric): secondary text on the Electric Blue bar (6.6:1), including pending nav links.
- **White** (white): primary text and headings.

### Named Rules
**The One Job Rule.** Neon Yellow marks only what can be acted on, focus, and where the visitor's scenario sits. It is never a background behind text blocks and never a headline. One filled Neon Yellow control per screen.

**The One Ramp Rule.** Every neutral comes from the stepped Deep Blue ramp. No greys, no off-ramp tints.

**The Words-First Rule.** Colour never carries meaning alone. A result is always a word plus an icon; contrast is at least 4.5:1 for all text.

## Typography

**Display Font:** Fira Sans (with Segoe UI, sans-serif)
**Body Font:** Overpass (with Segoe UI, sans-serif)
**Label/Mono Font:** Fira Code (with ui-monospace), for identifiers only

**Character:** The Space Apps brand hierarchy, applied literally: a heavy, upright Fira Sans Black in capitals for page titles, and Overpass's open, engineering-drawing letterforms for everything read. All three faces are self-hosted through Fontsource.

### Hierarchy
- **Display** (Fira Sans 900, caps, display scale, 1.04): H1 only, one per page.
- **Headline** (Overpass 400, headline scale, 1.2): H2 section heads, sentence case.
- **Title** (Overpass 600, caps, 1.0625rem, tracked 0.05em): H3 group heads, such as catalogue tiers.
- **Lede** (Overpass 300, 1.25rem, 1.5): the one paragraph under an H1, in ramp-6, 36 to 50ch.
- **Body** (Overpass 400, 1.0625rem, 1.55): reading text, 68 to 72ch.
- **Data** (Overpass 400, 0.9375rem, tabular figures): the one size inside every data region: lanes, catalogue, tables, notes.
- **Label** (Overpass 700, data size, caps, tracked 0.06em): lane results and table column heads. The figure caption uses Fira Sans 700 caps at the same size.
- **Footnote** (Overpass 400, 0.8125rem, 1.6): provenance lines under figures.
- **Identifier** (Fira Code 400, 0.92em, ligatures off): accession numbers, DOIs and file names, nothing else.

### Named Rules
**The Timetable Rule.** Inside a data region there is one text size. Rank comes from weight, case and ramp step, never from a second size.

**The Identifier Rule.** Fira Code is for things a researcher would copy and paste into a search box. Never for labels, numbers or decoration.

## Layout

Full-bleed bands separated by hairline rules, with content held to a fluid gutter (`spacing.gutter`, 1rem at phone width to 4.5rem). The 4rem Electric Blue bar is sticky. Home sets a fixed intro column (31rem, narrowing to 26rem between 1280 and 1439px) beside a flexible figure column; below 1280px everything stacks. Sources uses a 13rem sticky table of contents beside the content; below 1024px the contents become wrapped outlined chips.

Spacing follows a nine-step scale from 0.25rem to 6rem; section breaks use steps 7 to 9, lane and list internals steps 2 to 4.

Breakpoints are 1280px (intro stacks, wordmark drops its full name), 1024px (phone menu, single-column footer and catalogue groups) and 720px (lanes and tables recompose into stacked records). Every screen is checked at 375px; nothing scrolls horizontally except the investigation table's own wrapper above 720px.

**The Measured Column Rule.** Fixed columns come from measured text, not round numbers: the lane label is 8.5rem (the longest unit), the result 12.5rem (the longest one-line readout), and the track keeps every remaining pixel.

## Elevation & Depth

Flat. Depth is tonal: a surface rises by stepping one notch up the blue ramp (ramp-0 ground, ramp-1 raised band, ramp-2 lifted on hover or focus). Hairline ramp-3 rules divide regions.

### Shadow Vocabulary
- **Overlay drop** (`box-shadow: 0 16px 32px rgb(3 10 30 / 0.5)`): only the two surfaces that lie over page content, the phone menu panel and the Scenario page's fuel suggestion list.

### Named Rules
**The Lift Rule.** Hover and focus raise an element one ramp step; nothing rises by shadow, scale or glow.

## Shapes

Square and ruled. The one radius (4px) belongs to controls: buttons, the skip link, the phone menu toggle, contents chips. Data marks (tracks, bands, cells, stops) and regions have square corners. Borders are 1px hairlines; the only heavier strokes are the 3px scenario tick, the 3px inset scenario frame, and the 3px active-nav underline. Missing data is a 135° hatch (1px ramp-4 strokes every 7px).

## Components

### Buttons
Few and direct.
- **Shape:** gently squared (4px).
- **Primary:** Neon Yellow fill, Deep Blue Overpass 700 at 1.0625rem, 3rem tall; a trailing arrow icon nudges 3px right on hover. One per screen.
- **Hover / Focus:** fill lifts to neon-yellow-lift; press moves down 1px; focus is the global 2px Neon Yellow ring offset 3px.
- **Quiet:** transparent with a 1px ramp-4 border, white Overpass 600 at 0.9375rem, 2.5rem tall; the border turns Neon Yellow on hover. Used for secondary actions such as retry.

### Links
Neon Yellow text with a 1px underline offset 0.22em, thickening to 2px on hover. Inside dense lists and provenance lines links are quiet (white or ramp-6 with a ramp-4 underline) and turn Neon Yellow only when pointed at, so the accent stays rare.

### Navigation
Electric Blue sticky bar: the FLARE wordmark in Fira Sans 900, its full name in Overpass 400 on-electric (hidden below 1280px), seven links in Overpass 600 at 0.9375rem filling the bar's height. The active link carries a 3px Neon Yellow underline; hover tints the link with white at 8%. Pages still being built are dimmed to on-electric at weight 400 with a Construction icon, and say "in progress" in words in the phone menu. Below 1024px a bordered Menu toggle opens a full-width Electric Blue panel.

### Condition Lanes (signature)
A figure that lays one investigation against the visitor's scenario, one table row per condition.
- **Lane:** label column (name in 700, unit in ramp-5), track, result column. Hairline ramp-3 rule under each lane.
- **Track:** ramp-1, 2.25rem tall, with 1px ramp-3 unit ticks and a scale line beneath. Continuous conditions draw a **band** (band-fill with a 1px Blue Yonder edge) and a 3px Neon Yellow **scenario tick** overhanging the track by 0.3rem. Categorical conditions draw **stops** (tested stops in band-fill, the visitor's stop framed by a 3px inset Neon Yellow ring) or a **pair** (theirs as a band, yours framed in Neon Yellow).
- **Not recorded:** the track is hatched with a short in-track note on ramp-1; never a colour, never a zero.
- **Result:** a word in Label style with an icon: Equal in Blue Yonder for Match, EqualNot in Rocket Red for Differs, CircleDashed in ramp-5 for Not recorded. CircleDashed is reserved for missing data.
- **Lift:** hovering or focusing a lane raises it to ramp-2, brightens its readout to ramp-6, and the figure's footnote swaps to that lane's PSI source column. The footnote holds its height so the page never moves.
- **Entrance:** the one authored motion. Each band is drawn left to right by clip-path (640ms), staggered 90ms per lane, then the scenario tick drops 0.6rem into place (420ms), all on the ease-out curve. Static under reduced motion.
- **Phone:** each lane recomposes as label and result on one line, track full-width below.

### Catalogue Lane
The whole PSI catalogue as one lane of cells grouped by data tier on a shared column grid (8fr / 12fr / 6fr): ranked investigations as band cells, show-only as edged ramp cells, catalogue-only as hatched cells. Pointing at an investigation in the list below outlines its cell in Neon Yellow and lifts it 3px.

### States
Loading is an empty ramp-1 track with a faint Blue Yonder sweep. Errors sit in a ramp-1 panel with a hairline border, a Neon Yellow warning icon and a quiet retry button. An unbuilt page shows a hatched empty lane and the Construction icon.

## Do's and Don'ts

### Do:
- **Do** use the lane vocabulary on every surface that compares conditions: Neon Yellow tick or frame for the scenario, Blue Yonder band for the tested range, 135° hatch for not recorded.
- **Do** state every result in words with an icon (Match, Differs, Not recorded).
- **Do** put provenance beside the claim: a footnote under the figure naming the PSI source.
- **Do** keep one text size (0.9375rem) inside data regions, with tabular figures.
- **Do** lift on hover and focus by one ramp step (ramp-1 to ramp-2).
- **Do** mark pages still being built with the Construction icon and the words "in progress".
- **Do** keep contrast at 4.5:1 or better and check every screen at 375px.

### Don't:
- **Don't** use Neon Yellow as a background behind text blocks or for a headline.
- **Don't** use Rocket Red as a background, or without the word "Differs" beside it.
- **Don't** show missing data as a colour, a blank or a zero; hatch it and say "Not recorded".
- **Don't** use CircleDashed for anything except missing data.
- **Don't** build cards, stat tiles or shadowed panels; regions divide by hairline rules and ramp steps.
- **Don't** use Fira Code for anything other than identifiers.
- **Don't** use the NASA insignia.
- **Don't** add a second authored entrance animation; the lane draw is the one moment.
