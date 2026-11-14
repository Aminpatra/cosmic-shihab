// Which stored reading (GET /api/assistant/readings, #28) explains the ranking on screen, and the
// links that open each reading's scenario. Plain JS with no React, so Node can test it.

import { EMPTY_FORM, PLACES, formToParams, fromAtm, rankPath } from './ScenarioParams.js'

// Relative. A pressure typed on the Scenario page reaches the link with eight figures
// (10.2 psi = 0.69407113 atm); a reading stores the challenge page's value as 0.6941 atm.
const TOLERANCE = 1e-3

// The GET /api/rank parameters a link sets, without empty ones.
function rankParams(params) {
  const asked = new URLSearchParams(rankPath(params).slice('/rank?'.length))
  return Object.fromEntries([...asked].filter(([, value]) => value.trim() !== ''))
}

function sameValue(asked, stored) {
  if (typeof stored !== 'number') return asked === String(stored)
  const n = Number(asked)
  return Number.isFinite(n) && Math.abs(n - stored) <= TOLERANCE * Math.abs(stored)
}

// The same conditions and nothing else: a weight or an extra condition is another ranking.
export function sameScenario(params, scenario) {
  const asked = rankParams(params)
  const keys = Object.keys(scenario)
  return Object.keys(asked).length === keys.length && keys.every((key) => key in asked && sameValue(asked[key], scenario[key]))
}

// The ranking on screen still has the order and scores the reading was written about.
export function sameOrder(reading, items) {
  return reading.top.every(
    (top, i) => items[i]?.accession === top.accession && Math.round(items[i].score) === Math.round(top.score),
  )
}

// The reading written for this scenario as { reading, shown }, or null when there is none. A reading
// whose ranking has moved is not shown, since it would explain an order the page no longer displays.
export function readingFor(params, readings, items) {
  const reading = readings.find((r) => sameScenario(params, r.scenario))
  if (!reading) return null
  return { reading, shown: reading.current !== false && sameOrder(reading, items) }
}

// The Scenario form a reading's values fill: oxygen in %, pressure in psi to three figures, the
// way the challenge page states them (10.2, 4.3 and 14.7 psi).
export function presetForm(scenario) {
  const text = (value) => (value == null ? '' : String(value))
  return {
    ...EMPTY_FORM,
    place: PLACES.some((p) => p.id === scenario.environment) ? scenario.environment : '',
    gravity: text(scenario.gravity_g),
    oxygen: scenario.oxygen == null ? '' : String(Number((scenario.oxygen * 100).toPrecision(6))),
    pressure: scenario.pressure == null ? '' : String(Number(fromAtm(scenario.pressure, 'psi').toPrecision(3))),
    flow: text(scenario.flow_velocity),
    fuel: text(scenario.fuel),
    fuelPhase: text(scenario.fuel_phase),
    concern: text(scenario.concern),
  }
}

export const presetLink = (reading) => `/comparison?${formToParams(presetForm(reading.scenario))}`
