import { test } from 'node:test'
import assert from 'node:assert/strict'
import { axisFor, statusOf, countsOf, laneFor, figuresFor, parsePicks, formatCell, weightVariables } from './ComparisonLanes.js'

// Shaped like GET /api/rank output. FLEX's numbers are its real ranges; TEST-1 is synthetic.
const OPTIONS = {
  variables: {
    oxygen: { unit: 'mole fraction', min: 0.12, max: 0.85 },
    pressure: { unit: 'atm', min: 0, max: 5 },
    flow_velocity: { unit: 'cm/s', min: -5.92, max: 85.28 },
  },
}
const SCENARIO = { oxygen: 0.3, pressure: 0.7, flow_velocity: 10, fuel: 'pmma', fuel_phase: 'solid' }
const FLEX = {
  accession: 'PSI-69',
  investigationAcronym: 'FLEX',
  score: 50,
  matches: [
    { variable: 'oxygen', scenario: 0.3, tested_min: 0.12, tested_max: 0.34, closest: 0.3, unit: 'mole fraction' },
    { variable: 'pressure', scenario: 0.7, tested_min: 0, tested_max: 3.0525, closest: 0.7, unit: 'atm' },
  ],
  differences: [
    { variable: 'fuel_phase', scenario: 'solid', tested: ['liquid'] },
    { variable: 'fuel', scenario: 'pmma', tested: ['Heptane', 'Methanol'] },
  ],
  unavailable: ['flow_velocity'],
  best_tests: [
    {
      file: 'PSI-69_Experimental table_FLEX.csv',
      line: 42,
      run_id: '41',
      score: 67,
      values: { oxygen: { column: 'O initial ambient composition; mole fraction', value: 0.3, unit: 'mole fraction' } },
    },
  ],
}
const TWIN = {
  accession: 'TEST-1',
  investigationAcronym: '',
  score: 40,
  matches: [
    { variable: 'fuel_phase', scenario: 'solid', tested: ['gas', 'solid'] },
    { variable: 'fuel', scenario: 'pmma', tested: ['Cotton-Fiberglass (SIBAL)', 'PMMA', 'PMMA & Nomex', 'Silicone'] },
  ],
  differences: [{ variable: 'flow_velocity', scenario: 10, tested_min: 20, tested_max: 20, closest: 20, unit: 'cm/s' }],
  unavailable: ['oxygen', 'pressure'],
  best_tests: [],
}
const RESULT = {
  scenario: SCENARIO,
  method: { variables: ['oxygen', 'pressure', 'flow_velocity', 'fuel', 'fuel_phase'] },
  items: [FLEX, TWIN],
}

test('statuses and counts come from matches, differences and unavailable', () => {
  assert.equal(statusOf(FLEX, 'oxygen'), 'match')
  assert.equal(statusOf(FLEX, 'fuel_phase'), 'differs')
  assert.equal(statusOf(FLEX, 'flow_velocity'), 'missing')
  assert.deepEqual(countsOf(FLEX), { match: 2, differs: 2, missing: 1 })
})

test('axis widens to keep the scenario on it', () => {
  const a = axisFor('oxygen', OPTIONS, 30)
  assert.ok(a.min <= 12 && a.max >= 85)
  assert.ok(axisFor('oxygen', OPTIONS, 100).max >= 100)
  assert.ok(axisFor('flow_velocity', OPTIONS, 200).max >= 200)
})

test('a range lane shows the tested band in display units', () => {
  const lane = laneFor(FLEX, 'oxygen', SCENARIO, axisFor('oxygen', OPTIONS, 30))
  assert.equal(lane.kind, 'range')
  assert.deepEqual(lane.band, [12, 34])
  assert.equal(lane.value, 30)
  assert.equal(lane.status, 'match')
  assert.equal(lane.readout, 'tested 12–34 %, closest 30 %')
  assert.equal(lane.label, 'FLEX')
  assert.equal(lane.unit, 'PSI-69')
  assert.equal(lane.source, '"O initial ambient composition; mole fraction" in PSI-69_Experimental table_FLEX.csv')
  assert.equal(
    laneFor(FLEX, 'pressure', SCENARIO, axisFor('pressure', OPTIONS, 0.7)).readout,
    'tested 0–3.05 atm, closest 0.7 atm',
  )
})

test('a single-value band stays a band and reads as one value', () => {
  const lane = laneFor(TWIN, 'flow_velocity', SCENARIO, axisFor('flow_velocity', OPTIONS, 10))
  assert.deepEqual(lane.band, [20, 20])
  assert.equal(lane.readout, 'tested 20 cm/s, closest 20 cm/s')
  assert.equal(lane.label, 'TEST-1')
})

test('a missing variable is hatched and says so', () => {
  const lane = laneFor(FLEX, 'flow_velocity', SCENARIO, axisFor('flow_velocity', OPTIONS, 10))
  assert.equal(lane.band, null)
  assert.equal(lane.status, 'missing')
  assert.equal(lane.readout, 'Not recorded')
})

test('stops lanes list every tested stop', () => {
  const lane = laneFor(TWIN, 'fuel_phase', SCENARIO)
  assert.equal(lane.kind, 'stops')
  assert.deepEqual(lane.stops, ['gas', 'liquid', 'solid'])
  assert.deepEqual(lane.band, [0, 2])
  assert.equal(lane.value, 2)
})

test('fuel pair lists matching names first, then a count', () => {
  const lane = laneFor(TWIN, 'fuel', SCENARIO)
  assert.equal(lane.kind, 'pair')
  assert.equal(lane.theirs, 'PMMA, PMMA & Nomex, Cotton-Fiberglass (SIBAL) +1 more')
  assert.equal(lane.yours, 'pmma')
})

test('figures follow the method order, rows follow the rank order', () => {
  const figures = figuresFor(RESULT, ['TEST-1', 'PSI-69'], OPTIONS)
  assert.deepEqual(
    figures.map((f) => f.variable),
    ['oxygen', 'pressure', 'flow_velocity', 'fuel', 'fuel_phase'],
  )
  assert.equal(figures[0].caption, 'Oxygen, %')
  assert.deepEqual(
    figures[0].lanes.map((l) => l.unit),
    ['PSI-69', 'TEST-1'],
  )
})

test('picks ignore unknown accessions and default to the top two', () => {
  assert.deepEqual(parsePicks('PSI-999,TEST-1', RESULT.items), ['TEST-1'])
  assert.deepEqual(parsePicks(null, RESULT.items), ['PSI-69', 'TEST-1'])
  assert.equal(parsePicks('PSI-69,TEST-1,PSI-69', RESULT.items).length, 2)
  assert.deepEqual(parsePicks('', RESULT.items), [])
})

test('best-test cells read every shape the API sends', () => {
  // Shapes from BASS-II (PSI-25), ACME CLD Flame (PSI-21) and FLEX-2 (PSI-68) best tests.
  assert.equal(
    formatCell({ value: 0.222, unit: 'mole fraction', calculated: true, original: { value: 22.2, unit: '% by vol' } }),
    '22.2 % by vol (0.222 mole fraction, converted by FLARE)',
  )
  assert.equal(formatCell({ value: 0.3, unit: 'mole fraction' }), '0.3 mole fraction')
  assert.equal(formatCell({ text: '40% CH4' }), '40% CH4')
  assert.equal(formatCell({ values: [0.17, 0.21, 0.25, 0.3], unit: 'mole fraction' }), '0.17, 0.21, 0.25, 0.3 mole fraction')
  assert.equal(formatCell({ range: [0.1, 5], unit: 'cm/s' }), '0.1–5 cm/s')
  assert.equal(formatCell({ column: 'Fuel Bottle' }), 'not recorded')
})

test('a condition weighted 0 keeps its slider, so it can be weighted back', () => {
  const params = (s) => new URLSearchParams(s)
  // The API drops a 0-weight condition from method.variables, as for oxygen here.
  assert.deepEqual(
    weightVariables({ variables: ['pressure'] }, params('oxygen=0.21&pressure=1&weight_oxygen=0')),
    ['oxygen', 'pressure'],
  )
  // Every weight at 0: the API ranks nothing and lists no variables.
  assert.deepEqual(weightVariables({ variables: [] }, params('oxygen=0.21&weight_oxygen=0')), ['oxygen'])
  // No condition set, or a weight with no condition: no sliders.
  assert.deepEqual(weightVariables({ variables: [] }, params('')), [])
  assert.deepEqual(weightVariables({ variables: [] }, params('weight_oxygen=0')), [])
  // The API's own order, whatever order the link is in.
  assert.deepEqual(
    weightVariables({ variables: ['fuel', 'concern'] }, params('concern=prevention&fuel=ethanol&pressure=1&weight_pressure=0')),
    ['pressure', 'fuel', 'concern'],
  )
})
