// The Scenario form's model: what can be chosen, how typed values become GET /api/rank parameters,
// and back again, so a scenario is just a link (docs/superpowers/specs/2026-11-14-research-pages-design.md).
// Plain JS with no imports, so Node can test it.

// The API's `environment` only sets gravity, so the station rides with spacecraft (0 g) and the
// rover with the Moon base (0.17 g), as the challenge page groups them.
export const PLACES = [
  { id: 'spacecraft', label: 'Spacecraft', environment: 'spacecraft' },
  { id: 'station', label: 'Space station', environment: 'spacecraft' },
  { id: 'lunar', label: 'Lunar habitat', environment: 'lunar' },
  { id: 'rover', label: 'Pressurized rover', environment: 'lunar' },
  { id: 'mars', label: 'Mars habitat', environment: 'mars' },
  { id: 'custom', label: 'Custom', environment: 'custom' },
]

export const PRESSURE_UNITS = ['psi', 'kPa', 'atm']
export const ATM_IN = { psi: 14.6959, kPa: 101.325, atm: 1 }

// The only scenario values a NASA source states. Each fills a field only when clicked.
export const REFERENCE_SOURCE = {
  label: 'Flame in Freefall challenge page, NASA Space Apps 2026',
  url: 'https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=details',
}
export const REFERENCES = {
  oxygen: [
    { label: 'Spacesuit', value: 100 },
    { label: 'Moon base', value: 30, bound: 'at least', note: 'expected for a Moon base and pressurized rovers, not final' },
  ],
  // in psi, as the challenge page states them
  pressure: [
    { label: 'Spacesuit', value: 4.3 },
    { label: 'Moon base', value: 10.2, bound: 'at most', note: 'expected for a Moon base and pressurized rovers, not final' },
    { label: 'Sea level', value: 14.7 },
  ],
}

// Every value is the text the visitor typed: oxygen in %, pressure in `pUnit`.
export const EMPTY_FORM = {
  place: '',
  gravity: '',
  oxygen: '',
  pressure: '',
  pUnit: 'psi',
  flow: '',
  fuel: '',
  fuelPhase: '',
  concern: '',
}

const FUEL_PHASES = ['gas', 'liquid', 'solid']
const CONCERNS = ['prevention', 'detection', 'suppression']
const CONDITIONS = ['oxygen', 'pressure', 'flow_velocity', 'fuel', 'fuel_phase', 'concern']
const API_KEYS = new Set(['environment', 'gravity_g', ...CONDITIONS])

// Values read back are rounded to six significant figures; pressure is written in atm with
// eight, so 4.3 psi -> 0.29259861 atm -> 4.3 psi survives the round trip.
const round6 = (x) => Number(x.toPrecision(6))
const round8 = (x) => Number(x.toPrecision(8))

export function parseNumber(text) {
  const t = String(text ?? '').trim().replace(',', '.')
  if (t === '') return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

// At most three significant figures, for readouts; never used for what is sent.
export const formatValue = (n) => n.toLocaleString('en-US', { maximumSignificantDigits: 3 })

// A measurement axis with 3 to 6 round ticks that covers lo..hi, shared by the Scenario
// field lanes and the Comparison figures.
export function niceAxis(lo, hi) {
  if (lo === hi) {
    const pad = Math.abs(lo) / 4 || 1
    lo -= pad
    hi += pad
  }
  const raw = (hi - lo) / 4
  const mag = 10 ** Math.floor(Math.log10(raw))
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw)
  const ticks = []
  for (let t = Math.floor(lo / step) * step; t <= Math.ceil(hi / step) * step + step / 1e6; t += step) {
    ticks.push(Number(t.toPrecision(6)))
  }
  return { min: ticks[0], max: ticks.at(-1), ticks }
}

export const toAtm = (value, unit) => value / ATM_IN[unit]
export const fromAtm = (atm, unit) => atm * ATM_IN[unit]

export function validate(form) {
  const errors = {}
  const hints = {}
  const number = (field) => {
    if (String(form[field] ?? '').trim() === '') return null
    const n = parseNumber(form[field])
    if (n == null) errors[field] = 'Enter a number.'
    return n
  }

  const oxygen = number('oxygen')
  if (oxygen != null) {
    if (oxygen < 0 || oxygen > 100) errors.oxygen = 'Oxygen must be between 0 and 100 %.'
    else if (oxygen > 0 && oxygen < 1)
      hints.oxygen = `Read as ${oxygen} %. If you meant a mole fraction of ${oxygen}, enter ${round6(oxygen * 100)} %.`
  }
  const pressure = number('pressure')
  if (pressure != null && pressure < 0) errors.pressure = 'Pressure cannot be negative.'
  const flow = number('flow')
  if (flow != null && flow < 0) errors.flow = 'Airflow cannot be negative.'
  if (form.place === 'custom') {
    const gravity = number('gravity')
    if (gravity != null && (gravity < 0 || gravity > 1)) errors.gravity = 'Gravity must be between 0 and 1 g.'
  }

  const anyCondition = ['oxygen', 'pressure', 'flow', 'fuel', 'fuelPhase', 'concern'].some(
    (field) => String(form[field] ?? '').trim() !== '',
  )
  if (!anyCondition) errors.form = 'Enter at least one condition. FLARE ranks only on what you set.'
  return { errors, hints }
}

export function formToParams(form) {
  const p = new URLSearchParams()
  const place = PLACES.find((pl) => pl.id === form.place)
  if (place) p.set('environment', place.environment)
  const gravity = parseNumber(form.gravity)
  if (place?.id === 'custom' && gravity != null) p.set('gravity_g', String(round6(gravity)))
  const oxygen = parseNumber(form.oxygen)
  if (oxygen != null) p.set('oxygen', String(round6(oxygen / 100)))
  const pressure = parseNumber(form.pressure)
  const pUnit = PRESSURE_UNITS.includes(form.pUnit) ? form.pUnit : 'psi'
  if (pressure != null) p.set('pressure', String(round8(toAtm(pressure, pUnit))))
  const flow = parseNumber(form.flow)
  if (flow != null) p.set('flow_velocity', String(round6(flow)))
  const fuel = String(form.fuel ?? '').trim()
  if (fuel) p.set('fuel', fuel)
  if (FUEL_PHASES.includes(form.fuelPhase)) p.set('fuel_phase', form.fuelPhase)
  if (CONCERNS.includes(form.concern)) p.set('concern', form.concern)
  if (place) p.set('place', place.id)
  if (pressure != null) p.set('p_unit', pUnit)
  return p
}

// Reads a link back into the form. Anything unknown or unreadable comes back empty, so a
// hand-edited link never breaks the page.
export function paramsToForm(params) {
  const known = (value, list) => (list.includes(value) ? value : '')
  const number = (key, scale = (n) => n) => {
    const n = parseNumber(params.get(key))
    return n == null ? '' : String(round6(scale(n)))
  }
  const placeIds = PLACES.map((pl) => pl.id)
  const place = known(params.get('place'), placeIds) || known(params.get('environment'), placeIds)
  const pUnit = known(params.get('p_unit'), PRESSURE_UNITS) || 'psi'
  return {
    place,
    gravity: place === 'custom' ? number('gravity_g') : '',
    oxygen: number('oxygen', (n) => n * 100),
    pressure: number('pressure', (n) => fromAtm(n, pUnit)),
    pUnit,
    flow: number('flow_velocity'),
    fuel: params.get('fuel')?.trim() ?? '',
    fuelPhase: known(params.get('fuel_phase'), FUEL_PHASES),
    concern: known(params.get('concern'), CONCERNS),
  }
}

export const hasScenario = (params) => CONDITIONS.some((key) => (params.get(key) ?? '').trim() !== '')

// Only what GET /api/rank understands: the scenario and any weight_<variable>.
export function rankPath(params) {
  const out = new URLSearchParams()
  for (const [key, value] of params) {
    if (API_KEYS.has(key) || key.startsWith('weight_')) out.append(key, value)
  }
  return `/rank?${out}`
}

// The fuel names to suggest for what the visitor has typed: each name that contains the text,
// ignoring case and extra spaces, in the order given (the API's, most rows first).
export function fuelSuggestions(names, typed) {
  const text = String(typed ?? '').trim().toLowerCase().replace(/\s+/g, ' ')
  return text ? names.filter((name) => name.toLowerCase().includes(text)) : names
}
