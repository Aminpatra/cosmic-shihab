---
version: 1
slug: "frontend-src-pages-home-jsx"
primary_target: "frontend/src/pages/Home.jsx"
related_targets: ["frontend/src/Layout.jsx","frontend/src/pages/Sources.jsx"]
---

Scope: the FLARE app shell (top bar, seven routes), Home and Sources & Methodology. Mode: operate (Sources reads as read mode inside the same world). Audience: combustion researchers first, mission planners, Space Apps judges at the door. Constraints: NASA Space Apps brand (pinned), relevance is not safety, missing shown as missing, real PSI data only.

## Direction contract

THESIS: Every comparison reads like a microgravity test record: one lane per condition, the visitor's scenario a Neon Yellow tick, an investigation's tested range a Blue Yonder band, what was never recorded hatched. Refuses the category default: a sidebar dashboard of stat tiles and investigation cards.

OWN-WORLD: Pinned Space Apps palette. Deep Blue #07173F ground, Electric Blue #0042A6 top bar, Blue Yonder #2E96F5 tested ranges and data, Neon Yellow #EAFE07 only for what can be acted on and the scenario tick, White text, Rocket Red #E43700 only as a labelled "differs" mark. Neutrals from one stepped blue ramp. Lanes: dark track, hairline unit ticks, translucent blue band, 3px yellow tick, 135° hatch. Fira Sans Black caps headings, Overpass body, Fira Code only for identifiers (accession, DOI, file). 4px corners, no cards, no shadows; hairline rules divide regions.

STORY: Within seconds the visitor knows FLARE ranks NASA's 24 microgravity combustion investigations against their scenario and shows why. They believe it because a real PSI record sits against a scenario on the first screen with its gaps showing. They act: start from a scenario, or browse. On Sources they trust it because every number shows where it came from.

FIRST VIEWPORT: Home at 1440x900. Electric Blue 64px top bar: FLARE wordmark and full name, seven page links (unbuilt ones marked "in progress"), active link underlined Neon Yellow. Left 470px column: H1 in Fira Sans Black caps, one-paragraph lede, Neon Yellow "Start from a scenario" button and a yellow "Browse all 24 investigations" link, the not-a-safety-assessment note. Right: FLEX (PSI-69) against an example cabin in five lanes (gravity, oxygen, pressure, fuel, air flow), a status per lane, provenance line under it. The fold opens on the catalogue lane: the 24 investigations as cells grouped by data tier.

FORM: Condition Lanes, position 6 on the ordered list; seed:58a9a8d89e295d8a. Signature interaction: each lane draws its band, then the tick lands (one orchestrated entrance; static under reduced motion); hovering or focusing a lane lifts its status and provenance. Raises: nothing disappears, it cancels (ticket wallet); one shared measurement grid (Crouwel); one text size inside data regions (timetable rack); provenance beside the claim (centre rail); Neon Yellow has one job family (warm app); one stepped blue ramp, hatch for missing (exposure record).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

Unresolved: the real Scenario, Comparison and Explorer pages belong to #13 and #10; lane data per investigation comes from #12 and #7.
