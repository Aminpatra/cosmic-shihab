// Helpers over the investigation summaries served by GET /api/investigations (#8).

// Tier 1 of docs/DATA_PLAN.md ("Which investigations are reliable", 14 Nov 2026): the eight
// investigations whose experimental tables are large enough to rank and model. Tier 2 is every
// other investigation with a table; tier 3 has none.
const RANKABLE = new Set(['PSI-10', 'PSI-25', 'PSI-26', 'PSI-39', 'PSI-69', 'PSI-101', 'PSI-107', 'PSI-159'])

export const TIERS = [
  { id: 'rank', label: 'Rank and compare', note: 'Enough runs to rank and model.' },
  { id: 'show', label: 'Show and compare', note: 'Too few runs to model; shown in full.' },
  { id: 'catalogue', label: 'Catalogue only', note: 'Ground-based modelling studies with no run table.' },
]

export const runsOf = (inv) => (inv.derived?.experimental_tables ?? []).reduce((sum, t) => sum + (t.rows ?? 0), 0)

export function tierOf(inv) {
  if (RANKABLE.has(inv.accession)) return 'rank'
  return runsOf(inv) > 0 ? 'show' : 'catalogue'
}

export const nameOf = (inv) => inv.investigationAcronym?.trim() || inv.accession

export const byAccession = (a, b) => Number(a.accession.split('-')[1]) - Number(b.accession.split('-')[1])

export function summarise(investigations) {
  const files = investigations.reduce((sum, inv) => sum + (inv.derived?.file_count ?? 0), 0)
  const bytes = investigations.reduce((sum, inv) => sum + (inv.derived?.bytes_listed ?? 0), 0)
  const retrieved = investigations.find((inv) => inv.derived?.retrieved)?.derived.retrieved
  return { count: investigations.length, files, bytes, retrieved }
}

export const formatNumber = (n) => n.toLocaleString('en-US')

// "1 investigation", "24 investigations"
export const countOf = (n, one, many = `${one}s`) => `${formatNumber(n)} ${n === 1 ? one : many}`

export const formatTB = (bytes) => `${(bytes / 1e12).toFixed(1)} TB`

export function formatDate(iso) {
  if (!iso) return 'an unknown date'
  return new Date(`${iso}T00:00:00Z`).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC',
  })
}
