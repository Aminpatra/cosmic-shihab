import { test } from 'node:test'
import assert from 'node:assert/strict'
import { tagValues, readFilters, matchesFilters, optionsFor, splitSnippet } from './ExplorerFilters.js'

// Synthetic records shaped like GET /api/investigations items.
const tags = (values) => ({ derived: { tags: { values } } })
const A = { accession: 'A', ...tags({ platform: 'ISS', fuel_phase: 'liquid', gravity_level: 'microgravity' }) }
const B = {
  accession: 'B',
  ...tags({ platform: 'computation', fuel_phase: 'gas; liquid', gravity_level: 'microgravity; normal gravity' }),
}
const C = { accession: 'C', derived: {} }

test('tag values split on semicolons', () => {
  assert.deepEqual(tagValues(B, 'fuel_phase'), ['gas', 'liquid'])
  assert.deepEqual(tagValues(C, 'fuel_phase'), [])
})

test('filters are OR within a group and AND across groups', () => {
  const sel = readFilters(new URLSearchParams('fuel_phase=gas&fuel_phase=liquid&platform=ISS'))
  assert.deepEqual([...sel.fuel_phase], ['gas', 'liquid'])
  assert.equal(matchesFilters(A, sel), true)
  assert.equal(matchesFilters(B, sel), false)
  assert.equal(matchesFilters(C, sel), false)
  assert.equal(matchesFilters(C, readFilters(new URLSearchParams(''))), true)
})

test('options are counted', () => {
  assert.deepEqual(optionsFor([A, B, C], 'fuel_phase'), [
    { value: 'liquid', count: 2 },
    { value: 'gas', count: 1 },
  ])
})

test('snippets split into plain and matched text, and broken markers stay text', () => {
  assert.deepEqual(splitSnippet('droplet [[extinction]] (high [[Oxygen]])'), [
    { text: 'droplet ', match: false },
    { text: 'extinction', match: true },
    { text: ' (high ', match: false },
    { text: 'Oxygen', match: true },
    { text: ')', match: false },
  ])
  assert.deepEqual(splitSnippet('open [[ only'), [{ text: 'open [[ only', match: false }])
  assert.deepEqual(splitSnippet('<b>x</b>'), [{ text: '<b>x</b>', match: false }])
})
