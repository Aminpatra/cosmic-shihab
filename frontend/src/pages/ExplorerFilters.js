// Explorer's filters over derived.tags (docs/DECISIONS.md, #17) and the search snippets'
// [[match]] markers (#18). Plain JS so Node can test it.

export const FILTERS = [
  { key: 'platform', label: 'Platform' },
  { key: 'fuel_phase', label: 'Fuel phase' },
  { key: 'fire_safety_role', label: 'Fire-safety role' },
  { key: 'gravity_level', label: 'Gravity' },
  { key: 'flare_data', label: 'Data in FLARE' },
]

export function tagValues(inv, key) {
  const text = inv?.derived?.tags?.values?.[key]
  if (!text) return []
  return String(text)
    .split(';')
    .map((v) => v.trim())
    .filter(Boolean)
}

// Repeated keys in the link: ?fuel_phase=gas&fuel_phase=solid
export function readFilters(params) {
  const selected = {}
  for (const { key } of FILTERS) {
    const values = params.getAll(key).filter(Boolean)
    if (values.length) selected[key] = new Set(values)
  }
  return selected
}

export function matchesFilters(inv, selected) {
  return Object.entries(selected).every(([key, values]) => tagValues(inv, key).some((v) => values.has(v)))
}

export function optionsFor(investigations, key) {
  const counts = new Map()
  for (const inv of investigations) {
    for (const v of new Set(tagValues(inv, key))) counts.set(v, (counts.get(v) ?? 0) + 1)
  }
  return [...counts]
    .map(([value, count]) => ({ value, count }))
    .sort((a, b) => b.count - a.count || a.value.localeCompare(b.value))
}

// "a [[b]] c" -> plain, matched, plain. Only complete [[...]] pairs count, and the text is
// always rendered as text, never as HTML.
export function splitSnippet(snippet) {
  const parts = []
  const re = /\[\[(.+?)\]\]/g
  let last = 0
  for (const m of String(snippet ?? '').matchAll(re)) {
    if (m.index > last) parts.push({ text: snippet.slice(last, m.index), match: false })
    parts.push({ text: m[1], match: true })
    last = m.index + m[0].length
  }
  if (last < String(snippet ?? '').length) parts.push({ text: snippet.slice(last), match: false })
  return parts
}
