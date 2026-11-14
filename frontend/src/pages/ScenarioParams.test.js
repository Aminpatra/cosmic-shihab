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
} from './ScenarioParams.js'

test('parseNumber reads trimmed numbers and a decimal comma', () => {
  assert.equal(parseNumber(' 10,2 '), 10.2)
  assert.equal(parseNumber('4.3'), 4.3)
  assert.equal(parseNumber(''), null)
  assert.equal(parseNumber('abc'), null)
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
  assert.equal(p.get('pressure'), '0.694071')
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

test('hasScenario and rankPath', () => {
  assert.equal(hasScenario(new URLSearchParams('place=rover&environment=lunar')), false)
  assert.equal(hasScenario(new URLSearchParams('oxygen=0.3')), true)
  const p = new URLSearchParams('environment=lunar&oxygen=0.3&place=rover&p_unit=psi&pick=PSI-69&weight_oxygen=3')
  assert.equal(rankPath(p), '/rank?environment=lunar&oxygen=0.3&weight_oxygen=3')
})
