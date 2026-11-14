import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { presetForm, presetLink, readingFor, sameScenario } from './ComparisonReading.js'

// The three stored readings, as GET /api/assistant/readings serves them (`current` added).
const DIR = new URL('../../../backend/data/summaries/readings/', import.meta.url)
const READINGS = readdirSync(DIR)
  .filter((name) => name.endsWith('.json'))
  .map((name) => ({ ...JSON.parse(readFileSync(new URL(name, DIR), 'utf-8')), current: true }))
const byPreset = Object.fromEntries(READINGS.map((r) => [r.preset, r]))
const paramsOf = (link) => new URLSearchParams(link.split('?')[1])
const itemsOf = (reading) => reading.top.map(({ accession, score }) => ({ accession, score }))

test('each preset link opens the scenario its reading was written for, and only that one', () => {
  assert.deepEqual(Object.keys(byPreset).sort(), ['lunar-base', 'sea-level-air', 'spacesuit'])
  for (const reading of READINGS) {
    const params = paramsOf(presetLink(reading))
    const match = readingFor(params, READINGS, itemsOf(reading))
    assert.equal(match.reading.preset, reading.preset)
    assert.equal(match.shown, true)
    for (const other of READINGS.filter((r) => r !== reading)) assert.equal(sameScenario(params, other.scenario), false)
  }
})

test('the links state the challenge page values in psi, with the place for the Moon base', () => {
  assert.deepEqual(presetForm(byPreset['lunar-base'].scenario).pressure, '10.2')
  assert.deepEqual(presetForm(byPreset.spacesuit.scenario).pressure, '4.3')
  assert.deepEqual(presetForm(byPreset['sea-level-air'].scenario).pressure, '14.7')
  const lunar = paramsOf(presetLink(byPreset['lunar-base']))
  assert.equal(lunar.get('environment'), 'lunar')
  assert.equal(lunar.get('place'), 'lunar')
  assert.equal(lunar.get('p_unit'), 'psi')
  assert.equal(lunar.get('oxygen'), '0.3')
  assert.equal(paramsOf(presetLink(byPreset.spacesuit)).get('environment'), null)
})

test('a weight, an extra condition or another value is another ranking, so no reading', () => {
  const base = presetLink(byPreset['lunar-base'])
  const items = itemsOf(byPreset['lunar-base'])
  for (const extra of ['weight_oxygen=2', 'fuel=n-heptane', 'flow_velocity=5']) {
    assert.equal(readingFor(paramsOf(`${base}&${extra}`), READINGS, items), null, extra)
  }
  const suit = paramsOf(presetLink(byPreset.spacesuit))
  suit.set('pressure', String(5 / 14.6959))
  assert.equal(readingFor(suit, READINGS, items), null)
  suit.delete('pressure')
  assert.equal(readingFor(suit, READINGS, items), null)
})

test('the page only adds what the Scenario form adds; picks and the unit do not change the match', () => {
  const params = paramsOf(presetLink(byPreset['sea-level-air']))
  params.set('pick', 'PSI-69,PSI-10')
  params.set('p_unit', 'kPa')
  assert.equal(readingFor(params, READINGS, itemsOf(byPreset['sea-level-air'])).shown, true)
})

test('a reading whose ranking has moved is matched but not shown', () => {
  const reading = byPreset['lunar-base']
  const params = paramsOf(presetLink(reading))
  const swapped = itemsOf(reading)
  ;[swapped[0], swapped[1]] = [swapped[1], swapped[0]]
  assert.equal(readingFor(params, READINGS, swapped).shown, false)
  const rescored = itemsOf(reading).map((item, i) => (i === 2 ? { ...item, score: item.score - 1 } : item))
  assert.equal(readingFor(params, READINGS, rescored).shown, false)
  assert.equal(readingFor(params, READINGS, itemsOf(reading).slice(0, 2)).shown, false)
  const stale = READINGS.map((r) => (r === reading ? { ...r, current: false } : r))
  assert.equal(readingFor(params, stale, itemsOf(reading)).shown, false)
})
