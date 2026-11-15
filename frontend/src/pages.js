// The eight pages of FLARE, in navigation order. Paths are fixed so each task drops its page
// into a known slot (docs/DECISIONS.md, #9). When a page lands, set `ready: true` and point
// its route in main.jsx at the real component.
export const PAGES = [
  {
    path: '/',
    nav: 'Home',
    title: 'Home',
    ready: true,
  },
  {
    path: '/explorer',
    nav: 'Explorer',
    title: 'NASA Research Explorer',
    summary: 'Browse the investigations, filter them, read their metadata and open the original NASA sources.',
    issue: 13,
    ready: true,
  },
  {
    path: '/scenario',
    nav: 'Scenario',
    title: 'Scenario Explorer',
    summary: 'Choose a space environment and enter the conditions you know. Fields you leave empty stay empty; FLARE never fills them in.',
    issue: 13,
    ready: true,
  },
  {
    path: '/comparison',
    nav: 'Comparison',
    title: 'Investigation Comparison',
    summary: 'Ranked investigations, lane by lane: the conditions that match your scenario, the ones that differ, and the ones never recorded.',
    issue: 13,
    ready: true,
  },
  {
    path: '/visualization',
    nav: 'Visualization',
    title: 'Data Visualization',
    summary: "Charts drawn from the investigations' own experimental tables, in their original units.",
    issue: 35,
    ready: true,
  },
  {
    path: '/assistant',
    nav: 'Assistant',
    title: 'SI Research Assistant',
    summary: 'Ask about the investigations. Answers cite their NASA sources and say plainly when no source answers the question.',
    issue: 10,
    ready: true,
  },
  {
    path: '/methodology',
    nav: 'Methodology',
    title: 'Methodology',
    ready: true,
  },
  {
    path: '/sources',
    nav: 'Sources',
    title: 'Sources',
    ready: true,
  },
]
