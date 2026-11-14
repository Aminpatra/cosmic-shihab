// Turns a GET /api/rank answer into ConditionLanes figures: one figure per condition the
// scenario set, one row per picked investigation, every row on the same axis.
import { nameOf } from '../catalogue.js'
import { formatValue, niceAxis } from './ScenarioParams.js'

export { formatValue }

export const LANE_VARIABLES = {
  oxygen: { label: 'Oxygen', unit: '%', scale: 100, kind: 'range' },
  pressure: { label: 'Pressure', unit: 'atm', scale: 1, kind: 'range' },
  flow_velocity: { label: 'Airflow', unit: 'cm/s', scale: 1, kind: 'range' },
  fuel_phase: { label: 'Fuel phase', kind: 'stops', stops: ['gas', 'liquid', 'solid'] },
  concern: { label: 'Concern', kind: 'stops', stops: ['prevention', 'detection', 'suppression'] },
  fuel: { label: 'Fuel', kind: 'pair' },
}

const MAX_FUEL_NAMES = 3

// Display units, rounded so 0.34 x 100 is 34 and not 34.00000000000001.
const display = (variable, x) => (x == null ? null : Number((x * LANE_VARIABLES[variable].scale).toPrecision(6)))

export function axisFor(variable, options, scenarioValue) {
  const v = options?.variables?.[variable]
  const points = [display(variable, v?.min), display(variable, v?.max), scenarioValue]
  if (variable === 'oxygen') points.push(0, 100)
  const known = points.filter(Number.isFinite)
  return known.length ? niceAxis(Math.min(...known), Math.max(...known)) : niceAxis(0, 1)
}

const entryOf = (item, variable) =>
  [...(item.matches ?? []), ...(item.differences ?? [])].find((e) => e.variable === variable)

export function statusOf(item, variable) {
  if ((item.matches ?? []).some((e) => e.variable === variable)) return 'match'
  if ((item.differences ?? []).some((e) => e.variable === variable)) return 'differs'
  if ((item.unavailable ?? []).includes(variable)) return 'missing'
  return null
}

export const countsOf = (item) => ({
  match: item.matches?.length ?? 0,
  differs: item.differences?.length ?? 0,
  missing: item.unavailable?.length ?? 0,
})

function sourceOf(item, variable) {
  const test = (item.best_tests ?? []).find((t) => t.values?.[variable])
  return test ? `"${test.values[variable].column}" in ${test.file}` : `${item.accession} experimental table`
}

function fuelNames(tested, fuel) {
  const q = String(fuel ?? '').toLowerCase()
  const hit = (name) => q && name.toLowerCase().includes(q)
  const ordered = [...tested.filter(hit), ...tested.filter((n) => !hit(n))]
  const more = ordered.length - MAX_FUEL_NAMES
  return ordered.slice(0, MAX_FUEL_NAMES).join(', ') + (more > 0 ? ` +${more} more` : '')
}

export function laneFor(item, variable, scenario, axis) {
  const meta = LANE_VARIABLES[variable]
  const entry = entryOf(item, variable)
  const lane = {
    id: `${item.accession}-${variable}`,
    label: nameOf(item),
    unit: item.accession,
    status: statusOf(item, variable) ?? 'missing',
    source: sourceOf(item, variable),
    kind: meta.kind,
  }

  if (meta.kind === 'range') {
    const value = display(variable, scenario?.[variable])
    if (!entry) return { ...lane, axis, band: null, value, readout: 'Not recorded' }
    const [lo, hi, closest] = [entry.tested_min, entry.tested_max, entry.closest].map((x) => display(variable, x))
    const span = lo === hi ? formatValue(lo) : `${formatValue(lo)}–${formatValue(hi)}`
    return {
      ...lane,
      axis,
      band: [lo, hi],
      value,
      readout: `tested ${span} ${meta.unit}, closest ${formatValue(closest)} ${meta.unit}`,
    }
  }

  const tested = entry?.tested ?? []
  if (meta.kind === 'stops') {
    return {
      ...lane,
      stops: meta.stops,
      band: tested.map((t) => meta.stops.indexOf(String(t).toLowerCase())).filter((i) => i >= 0),
      value: meta.stops.indexOf(scenario?.[variable]),
      readout: entry ? `tested ${tested.join(', ')}` : 'Not recorded',
    }
  }

  return {
    ...lane,
    theirs: entry ? fuelNames(tested, scenario?.fuel) : null,
    yours: scenario?.fuel ?? '',
    readout: entry ? `${tested.length} ${tested.length === 1 ? 'fuel' : 'fuels'} tested` : 'Not recorded',
  }
}

function summaryOf(lanes) {
  const n = (status) => lanes.filter((l) => l.status === status).length
  return [
    [n('match'), 'match'],
    [n('differs'), 'differs'],
    [n('missing'), 'not recorded'],
  ]
    .filter(([count]) => count > 0)
    .map(([count, word]) => `${count} ${word}`)
    .join(', ')
}

export function figuresFor(result, picks, options) {
  const items = (result?.items ?? []).filter((item) => picks.includes(item.accession))
  return (result?.method?.variables ?? [])
    .filter((variable) => LANE_VARIABLES[variable])
    .map((variable) => {
      const meta = LANE_VARIABLES[variable]
      const axis =
        meta.kind === 'range' ? axisFor(variable, options, display(variable, result.scenario?.[variable])) : undefined
      const lanes = items.map((item) => laneFor(item, variable, result.scenario, axis))
      return {
        variable,
        caption: meta.unit ? `${meta.label}, ${meta.unit}` : meta.label,
        summary: summaryOf(lanes),
        lanes,
      }
    })
}

export function parsePicks(param, items) {
  const known = (items ?? []).map((item) => item.accession)
  if (param == null) return known.slice(0, 2)
  const picks = []
  for (const a of param.split(',').map((s) => s.trim())) {
    if (known.includes(a) && !picks.includes(a)) picks.push(a)
  }
  return picks.slice(0, 3)
}
