import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router'
import { useApi } from '../api.js'
import './ScenarioProbe.css'

// One scenario (oxygen as a mole fraction, pressure in atm) that every chart on a page redraws
// against. The link keeps it under /api/rank's own parameter names, so it can be shared and
// handed straight to /comparison (docs/DECISIONS.md, #13).

const PSI_PER_ATM = 14.6959

// The only scenarios the challenge page gives values for (backend/data/summaries/readings/).
export const PRESETS = [
  { id: 'lunar-base', label: 'Moon base', oxygen: 0.3, pressure: 0.6941, place: 'lunar', says: '30% oxygen at 10.2 psi' },
  { id: 'spacesuit', label: 'Spacesuit', oxygen: 1, pressure: 0.2926, says: '100% oxygen at 4.3 psi' },
  { id: 'sea-level-air', label: 'Sea-level air', oxygen: 0.21, pressure: 1, says: '21% oxygen at 1 atm' },
]

const VARIABLES = ['oxygen', 'pressure']
const round = (v, digits) => +v.toFixed(digits)

function fromParams(params) {
  const read = (key, max) => {
    if (!params.has(key)) return null
    const v = Number(params.get(key))
    return Number.isFinite(v) && v >= 0 && v <= max ? v : null
  }
  return { oxygen: read('oxygen', 1), pressure: read('pressure', 10) }
}

/**
 * The page's scenario, kept in the link. `tolerance` is the ranking's own window for each
 * variable: a quarter of its span across every scorable test (backend/app/ranking.py), read from
 * /api/rank/options so the charts and the ranking never disagree. Null while it loads or if it fails.
 */
export function useScenarioProbe() {
  const [params, setParams] = useSearchParams()
  const [probe, setProbe] = useState(() => fromParams(params))
  const options = useApi('/rank/options')

  // Write the link a moment after the last change, so dragging a slider is not one history step per pixel.
  useEffect(() => {
    const timer = setTimeout(() => {
      setParams(
        (prev) => {
          const next = new URLSearchParams(prev)
          for (const key of VARIABLES) {
            if (probe[key] == null) next.delete(key)
            else next.set(key, String(round(probe[key], 4)))
          }
          return next
        },
        { replace: true, preventScrollReset: true },
      )
    }, 250)
    return () => clearTimeout(timer)
  }, [probe, setParams])

  const ranges = options.status === 'ready' ? options.data.variables : null
  const tolerance = useMemo(
    () => (ranges ? Object.fromEntries(VARIABLES.map((k) => [k, (ranges[k].max - ranges[k].min) / 4])) : null),
    [ranges],
  )
  const set = (patch) => setProbe((prev) => ({ ...prev, ...patch }))
  return { probe, set, tolerance, pressureMax: ranges?.pressure.max ?? 5 }
}

export const probeIsSet = (probe) => probe.oxygen != null || probe.pressure != null

/**
 * Whether one test sits inside the window on every variable the scenario sets. A test that did
 * not record a set variable is not near, as in the ranking, where it scores 0 (Methodology).
 * Null when the scenario sets nothing or the window is unknown: then nothing is dimmed.
 */
export function nearness(probe, tolerance) {
  if (!tolerance || !probeIsSet(probe)) return null
  const set = VARIABLES.filter((k) => probe[k] != null)
  return (values) => set.every((k) => values[k] != null && Math.abs(values[k] - probe[k]) <= tolerance[k])
}

/** The link to the ranked comparison for this scenario. */
export function comparisonLink(probe) {
  const p = new URLSearchParams()
  const preset = PRESETS.find((s) => s.oxygen === probe.oxygen && s.pressure === probe.pressure)
  if (preset?.place) {
    p.set('environment', preset.place)
    p.set('place', preset.place)
  }
  if (probe.oxygen != null) p.set('oxygen', String(round(probe.oxygen, 4)))
  if (probe.pressure != null) {
    p.set('pressure', String(round(probe.pressure, 4)))
    p.set('p_unit', 'atm')
  }
  return `/comparison?${p}`
}

const fmtOxygen = (v) => `${v.toFixed(2)} (${Math.round(v * 100)}%)`
const fmtPressure = (v) => `${v.toFixed(v < 1 ? 3 : 2)} atm (${(v * PSI_PER_ATM).toFixed(1)} psi)`

function Slider({ id, label, unit, value, fallback, max, step, format, tolerance, onChange }) {
  const unset = value == null
  return (
    <div className={`probe-var${unset ? ' is-unset' : ''}`}>
      <label htmlFor={id}>
        <span className="probe-name">{label}</span> <span className="probe-unit">{unit}</span>
      </label>
      <input
        id={id}
        type="range"
        min="0"
        max={max}
        step={step}
        value={unset ? fallback : value}
        aria-valuetext={unset ? 'Not set' : format(value)}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <output htmlFor={id} className="probe-readout">
        {unset ? 'Not set' : format(value)}
        {!unset && tolerance != null && (
          <span className="probe-window">
            window ±{tolerance.toFixed(2)}
            {unit === 'atm' ? ' atm' : ''}
          </span>
        )}
      </output>
    </div>
  )
}

/** The control bar: presets, two sliders and a clear button, all writing the one scenario. */
export function ScenarioProbeBar({ probe, set, tolerance, pressureMax }) {
  const active = PRESETS.find((s) => s.oxygen === probe.oxygen && s.pressure === probe.pressure)
  return (
    <section className="probe" aria-labelledby="probe-title">
      <div className="probe-head">
        <h2 id="probe-title" className="probe-title">
          Your scenario
        </h2>
        <div className="probe-presets" role="group" aria-label="Scenarios from the challenge page">
          {PRESETS.map((s) => (
            <button
              key={s.id}
              type="button"
              className="button-quiet probe-preset"
              aria-pressed={active?.id === s.id}
              title={s.says}
              onClick={() => set({ oxygen: s.oxygen, pressure: s.pressure })}
            >
              {s.label}
            </button>
          ))}
          <button
            type="button"
            className="probe-clear"
            disabled={!probeIsSet(probe)}
            onClick={() => set({ oxygen: null, pressure: null })}
          >
            Clear
          </button>
        </div>
      </div>
      <div className="probe-vars">
        <Slider
          id="probe-oxygen"
          label="Oxygen"
          unit="mole fraction"
          value={probe.oxygen}
          fallback={0.21}
          max={1}
          step={0.01}
          format={fmtOxygen}
          tolerance={tolerance?.oxygen}
          onChange={(v) => set({ oxygen: v })}
        />
        <Slider
          id="probe-pressure"
          label="Pressure"
          unit="atm"
          value={probe.pressure}
          fallback={1}
          max={pressureMax}
          step={0.01}
          format={fmtPressure}
          tolerance={tolerance?.pressure}
          onChange={(v) => set({ pressure: v })}
        />
      </div>
    </section>
  )
}
