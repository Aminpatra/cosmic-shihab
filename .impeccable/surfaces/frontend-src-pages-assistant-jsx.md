---
version: 1
slug: "frontend-src-pages-assistant-jsx"
primary_target: "frontend/src/pages/Assistant.jsx"
related_targets: ["frontend/src/components/CatalogueLane.jsx"]
---

# Assistant surface (/assistant)

Mode: Operate. Researchers ask one question at a time about the 24 PSI investigations and check
the answer against its NASA sources. Judges see it in the demo. No chat history.

States to design: idle (no question yet), asking, generated answer, retrieval-only answer (no key,
model declined, or API failure: sources only, reason in words, no prose), nothing found, error
(API unreachable), scoped to 1-4 investigations or unscoped.

## Direction contract

THESIS: The question is scoped on the catalogue, not typed into a chat. The page refuses the
chat-bubble transcript; it is one question, one cited reading, one source register.

OWN-WORLD: DESIGN.md unchanged: Deep Blue ground, Electric Blue bar, hairline ramp-3 rules, the
catalogue lane cells (band, edged, hatched) as the scope selector with Neon Yellow frames on the
chosen cells, Blue Yonder underline on sourced text, ramp-5 for the assistant's own explanation,
Fira Code for accessions and file names only.

STORY: The visitor sees which investigations a question covers, asks, reads an answer whose every
sentence says whether it rests on NASA text or is the assistant's explanation, follows a citation
to the source, and is told plainly when FLARE has no source or no AI key.

FIRST VIEWPORT: H1 and lede at left; a full-width question field with the one Neon Yellow Ask
button; directly below, the catalogue lane at full width labelled SCOPE, chosen cells framed in
Neon Yellow with removable chips naming them; the answer region starts below with its mode label.

FORM: Scope on the catalogue lane, position 6 of 7 on my list. seed: none (unavailable)
SIGNATURE MOVE: picking cells on the catalogue lane narrows the question. In the answer, text
that rests on a NASA source carries a 1px Blue Yonder underline and numbered citation links; the
assistant's own explanation is set in ramp-5 without them; a legend says so in words. (Revised
from per-sentence gutter rules: citations arrive as fragments inside paragraphs.)

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
