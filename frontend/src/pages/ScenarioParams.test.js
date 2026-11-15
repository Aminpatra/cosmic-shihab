import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  EMPTY_FORM,
  parseNumber,
  toAtm,
  formToParams,
  paramsToForm,
  validate,
  hasScenario,
  rankPath,
  niceAxis,
  fuelSuggestions,
} from './ScenarioParams.js'

test('parseNumber reads trimmed numbers and a decimal comma', () => {
  assert.equal(parseNumber(' 10,2 '), 10.2)
  assert.equal(parseNumber('4.3'), 4.3)
  assert.equal(parseNumber(''), null)
  assert.equal(parseNumber('abc'), null)
  // Number() alone reads these as 16, 5 and 7; nobody types them meaning that.
  assert.equal(parseNumber('0x10'), null)
  assert.equal(parseNumber('0b101'), null)
  assert.equal(parseNumber('0o7'), null)
  // Exponents stay: the page's own links write a tiny gravity as 1e-7.
  assert.equal(parseNumber(String(1e-7)), 1e-7)
  assert.equal(parseNumber('.5'), 0.5)
  assert.equal(parseNumber('1e999'), null)
})

test('pressure converts to atm', () => {
  assert.ok(Math.abs(toAtm(14.6959, 'psi') - 1) < 1e-9)
  assert.ok(Math.abs(toAtm(101.325, 'kPa') - 1) < 1e-9)
  assert.equal(toAtm(0.7, 'atm'), 0.7)
})

test('a rover scenario becomes API parameters, leaving empty fields out', () => {
  const p = formToParams({ ...EMPTY_FORM, place: 'rover', oxygen: '30', pressure: '10.2', fuelPhase: 'solid' })
  assert.equal(p.get('environment'), 'lunar')
  assert.equal(p.get('place'), 'rover')
  assert.equal(p.get('oxygen'), '0.3')
  assert.equal(p.get('pressure'), '0.69407114')
  assert.equal(p.get('p_unit'), 'psi')
  assert.equal(p.get('fuel_phase'), 'solid')
  assert.equal(p.has('flow_velocity'), false)
  assert.equal(p.has('gravity_g'), false)
})

test('the form survives a round trip through the URL', () => {
  const form = {
    ...EMPTY_FORM,
    place: 'custom',
    gravity: '0.38',
    oxygen: '21',
    pressure: '101.325',
    pUnit: 'kPa',
    flow: '5',
    fuel: 'PMMA',
    concern: 'suppression',
  }
  assert.deepEqual(paramsToForm(formToParams(form)), form)
  assert.equal(paramsToForm(formToParams({ ...EMPTY_FORM, pressure: '10.2' })).pressure, '10.2')
  assert.equal(paramsToForm(formToParams({ ...EMPTY_FORM, pressure: '4.3' })).pressure, '4.3')
})

test('a hand-edited URL falls back instead of breaking', () => {
  const form = paramsToForm(new URLSearchParams('oxygen=abc&p_unit=bar&pressure=1&place=moon'))
  assert.equal(form.oxygen, '')
  assert.equal(form.pUnit, 'psi')
  assert.equal(form.pressure, '14.6959')
  assert.equal(form.place, '')
})

test('validate catches what the API would reject, and hints at a fraction typed as percent', () => {
  assert.equal(validate({ ...EMPTY_FORM, oxygen: '120' }).errors.oxygen, 'Oxygen must be between 0 and 100 %.')
  assert.equal(validate({ ...EMPTY_FORM, oxygen: 'abc' }).errors.oxygen, 'Enter a number.')
  assert.equal(validate({ ...EMPTY_FORM, pressure: '-1' }).errors.pressure, 'Pressure cannot be negative.')
  assert.equal(validate({ ...EMPTY_FORM, flow: '-2' }).errors.flow, 'Airflow cannot be negative.')
  assert.equal(
    validate({ ...EMPTY_FORM, place: 'custom', gravity: '2', oxygen: '21' }).errors.gravity,
    'Gravity must be between 0 and 1 g.',
  )
  assert.match(validate({ ...EMPTY_FORM, oxygen: '0.3' }).hints.oxygen, /30 %/)
  assert.equal(
    validate({ ...EMPTY_FORM, place: 'lunar' }).errors.form,
    'Enter at least one condition. FLARE ranks only on what you set.',
  )
  assert.deepEqual(validate({ ...EMPTY_FORM, fuelPhase: 'gas' }).errors, {})
})

test("validate holds to GET /api/rank's upper limits, in the visitor's unit", () => {
  const errors = (form) => validate({ ...EMPTY_FORM, ...form }).errors
  assert.equal(errors({ pressure: '200', pUnit: 'psi' }).pressure, 'Pressure must be at most 146.959 psi (10 atm), the most the ranking accepts.')
  assert.equal(errors({ pressure: '1100', pUnit: 'kPa' }).pressure, 'Pressure must be at most 1013.25 kPa (10 atm), the most the ranking accepts.')
  assert.equal(errors({ pressure: '10.5', pUnit: 'atm' }).pressure, 'Pressure must be at most 10 atm, the most the ranking accepts.')
  // The limit itself passes in every unit, and is sent as no more than 10 atm.
  for (const [pressure, pUnit] of [['146.959', 'psi'], ['1013.25', 'kPa'], ['10', 'atm']]) {
    assert.equal(errors({ pressure, pUnit }).pressure, undefined, `${pressure} ${pUnit}`)
    assert.ok(Number(formToParams({ ...EMPTY_FORM, pressure, pUnit }).get('pressure')) <= 10, `${pressure} ${pUnit}`)
  }
  assert.equal(errors({ flow: '5000' }).flow, 'Airflow must be at most 1000 cm/s, the most the ranking accepts.')
  assert.equal(errors({ flow: '1000' }).flow, undefined)
  assert.equal(errors({ fuel: 'x'.repeat(101) }).fuel, 'Fuel must be at most 100 characters.')
  assert.equal(errors({ fuel: ` ${'x'.repeat(100)} ` }).fuel, undefined)
  // The ranking reads a fuel by its words of two or more letters or digits, so "a" would be dropped.
  for (const fuel of ['a', 'a b', '-', 'メタン']) {
    assert.match(errors({ fuel }).fuel ?? '', /can't read a fuel name/, fuel)
  }
  for (const fuel of ['ethylene', 'C2H4', 'n-heptane', '75 % propylene']) {
    assert.equal(errors({ fuel }).fuel, undefined, fuel)
  }
})

test('niceAxis covers the range with round ticks', () => {
  assert.deepEqual(niceAxis(0, 100).ticks, [0, 25, 50, 75, 100])
  assert.deepEqual(niceAxis(0, 73.5).ticks, [0, 20, 40, 60, 80])
  const flow = niceAxis(-5.92, 85.28)
  assert.ok(flow.min <= -5.92 && flow.max >= 85.28)
  const one = niceAxis(20, 20)
  assert.ok(one.min < 20 && one.max > 20)
})

test('hasScenario and rankPath', () => {
  assert.equal(hasScenario(new URLSearchParams('place=rover&environment=lunar')), false)
  assert.equal(hasScenario(new URLSearchParams('oxygen=0.3')), true)
  const p = new URLSearchParams('environment=lunar&oxygen=0.3&place=rover&p_unit=psi&pick=PSI-69&weight_oxygen=3')
  assert.equal(rankPath(p), '/rank?environment=lunar&oxygen=0.3&weight_oxygen=3')
})

test('fuel suggestions keep every name that contains the typed text, in the given order', () => {
  const names = ['propylene', 'methanol', 'ethane', 'pmma', 'dodecane iso dodecane', 'methane', 'dodecane']
  assert.deepEqual(fuelSuggestions(names, ''), names)
  assert.deepEqual(fuelSuggestions(names, '   '), names)
  assert.deepEqual(fuelSuggestions(names, 'ethan'), ['methanol', 'ethane', 'methane'])
  assert.deepEqual(fuelSuggestions(names, ' PMMA '), ['pmma'])
  assert.deepEqual(fuelSuggestions(names, 'dodecane  iso'), ['dodecane iso dodecane'])
  assert.deepEqual(fuelSuggestions(names, 'water'), [])
})
