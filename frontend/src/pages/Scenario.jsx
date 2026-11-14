import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router'
import { ArrowRight, TriangleAlert } from 'lucide-react'
import { useApi } from '../api.js'
import { LoadError } from '../components/ApiState.jsx'
import GravityScale from '../components/GravityScale.jsx'
import {
  PLACES,
  PRESSURE_UNITS,
  REFERENCES,
  REFERENCE_SOURCE,
  formToParams,
  formatValue,
  fromAtm,
  niceAxis,
  paramsToForm,
  parseNumber,
  toAtm,
  validate,
} from './ScenarioParams.js'
import './Scenario.css'

const FUEL_PHASES = ['gas', 'liquid', 'solid']
const CONCERNS = ['prevention', 'detection', 'suppression']
const MIN_FUEL_ROWS = 10 // fewer rows than this are mostly table-parsing leftovers

// How a numeric field is shown against NASA's tested span: the API's range in display units.
const SPAN = {
  oxygen: (v) => ({ min: v.min * 100, max: v.max * 100, unit: '%' }),
  pressure: (v, pUnit) => ({ min: fromAtm(v.min, pUnit), max: fromAtm(v.max, pUnit), unit: pUnit }),
  flow_velocity: (v) => ({ min: v.min, max: v.max, unit: 'cm/s' }),
}

// A thin lane under the field on a measured axis: NASA's tested span as a band, the visitor's
// value as the tick. `bounds` widens the axis to a natural scale (oxygen runs 0 to 100 %).
function SpanLane({ span, rows, value, bounds = [] }) {
  if (!span) return <div className="span-lane" aria-hidden="true" />
  const axis = niceAxis(
    Math.min(span.min, value ?? span.min, bounds[0] ?? span.min),
    Math.max(span.max, value ?? span.max, bounds[1] ?? span.max),
  )
  const at = (x) => `${((x - axis.min) / (axis.max - axis.min)) * 100}%`
  const outside = value != null && (value < span.min || value > span.max)
  return (
    <div className="span">
      <div className="span-lane" aria-hidden="true">
        {axis.ticks.map((t) => (
          <span key={t} className="span-unit" style={{ left: at(t) }} />
        ))}
        <span className="span-band" style={{ left: at(span.min), width: `calc(${at(span.max)} - ${at(span.min)})` }} />
        {value != null && <span className="span-tick" style={{ left: at(value) }} />}
      </div>
      <div className="span-scale" aria-hidden="true">
        {axis.ticks.map((t) => (
          <span key={t} style={{ left: at(t) }}>
            {formatValue(t)}
          </span>
        ))}
      </div>
      <p className="span-words">
        <span className={outside ? 'span-outside' : undefined}>
          {value == null
            ? 'Not set'
            : outside
              ? value > span.max
                ? 'Higher than any NASA test'
                : 'Lower than any NASA test'
              : 'Within the span NASA tested'}
        </span>
        <span>
          NASA tested {formatValue(span.min)}–{formatValue(span.max)} {span.unit}, {rows.toLocaleString('en-US')} rows
        </span>
      </p>
    </div>
  )
}

function Stops({ name, legend, note, options, value, onChange }) {
  return (
    <fieldset className="row">
      <legend className="row-label">
        <span className="row-name">{legend}</span>
        {note && <span className="row-unit">{note}</span>}
      </legend>
      <div className="stops" style={{ '--n': options.length + 1 }}>
        {[{ id: '', label: 'Not set' }, ...options].map((opt) => (
          <label
            key={opt.id || 'none'}
            className="stop-choice"
            data-checked={value === opt.id || undefined}
            data-empty={opt.id === '' || undefined}
          >
            <input
              type="radio"
              name={name}
              value={opt.id}
              checked={value === opt.id}
              onChange={() => onChange(opt.id)}
              className="visually-hidden"
            />
            <span className="stop-name">{opt.label}</span>
            {opt.detail && <span className="stop-detail">{opt.detail}</span>}
          </label>
        ))}
      </div>
    </fieldset>
  )
}

function NumberRow({ id, label, unit, unitControl, value, onChange, converted, error, hint, refs, applied, span }) {
  const describedBy = [error && `${id}-error`, hint && `${id}-hint`, applied?.bound && `${id}-bound`]
    .filter(Boolean)
    .join(' ')
  return (
    <div className="row">
      <label className="row-label" htmlFor={id}>
        <span className="row-name">{label}</span>
        <span className="row-unit">{unit}</span>
      </label>
      <div className="row-field">
        <div className="field-line">
          <input
            id={id}
            className="field-input"
            inputMode="decimal"
            autoComplete="off"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            aria-invalid={error ? true : undefined}
            aria-describedby={describedBy || undefined}
          />
          {unitControl ?? <span className="field-unit">{unit}</span>}
        </div>
        {converted && <p className="field-note">{converted}</p>}
        {error && (
          <p id={`${id}-error`} className="field-error">
            <TriangleAlert size={16} aria-hidden="true" />
            {error}
          </p>
        )}
        {hint && (
          <p id={`${id}-hint`} className="field-note field-hint">
            {hint}
          </p>
        )}
        {applied?.bound && (
          <p id={`${id}-bound`} className="field-note">
            The challenge states {applied.bound} {formatValue(applied.value)} {applied.unit} ({applied.note}); FLARE ranks
            it as one value.
          </p>
        )}
        {refs.length > 0 && (
          <ul className="refs" aria-label={`${label} reference values`}>
            {refs.map((ref) => (
              <li key={ref.label}>
                <button type="button" className="ref" onClick={() => ref.apply()}>
                  {ref.label} {ref.bound === 'at least' ? '≥ ' : ref.bound === 'at most' ? '≤ ' : ''}
                  {formatValue(ref.value)} {ref.unit}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="row-span">{span}</div>
    </div>
  )
}

export default function Scenario() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const options = useApi('/rank/options')
  const [form, setForm] = useState(() => paramsToForm(params))
  const [applied, setApplied] = useState({}) // the reference value last clicked into a field
  const { errors, hints } = validate(form)

  const set = (field) => (value) => {
    setForm((f) => ({ ...f, [field]: value }))
    setApplied((a) => ({ ...a, [field]: undefined }))
  }

  const vars = options.data?.variables
  const spanFor = (key, display) => {
    const v = vars?.[key]
    return v ? { span: SPAN[key](v, form.pUnit), rows: v.rows, value: display } : { span: null }
  }

  const oxygen = parseNumber(form.oxygen)
  const pressure = parseNumber(form.pressure)
  const flow = parseNumber(form.flow)

  const changeUnit = (unit) => {
    setForm((f) => {
      const n = parseNumber(f.pressure)
      const next = n == null ? f.pressure : String(Number(fromAtm(toAtm(n, f.pUnit), unit).toPrecision(6)))
      return { ...f, pUnit: unit, pressure: next }
    })
  }

  const oxygenRefs = REFERENCES.oxygen.map((ref) => ({
    ...ref,
    unit: '%',
    apply: () => {
      setForm((f) => ({ ...f, oxygen: String(ref.value) }))
      setApplied((a) => ({ ...a, oxygen: { ...ref, unit: '%' } }))
    },
  }))
  const pressureRefs = REFERENCES.pressure.map((ref) => ({
    ...ref,
    unit: 'psi',
    apply: () => {
      const inUnit = Number(fromAtm(toAtm(ref.value, 'psi'), form.pUnit).toPrecision(6))
      setForm((f) => ({ ...f, pressure: String(inUnit) }))
      setApplied((a) => ({ ...a, pressure: { ...ref, unit: 'psi' } }))
    },
  }))

  const gravityOf = options.data?.environments ?? {}
  const places = PLACES.map((pl) => ({
    id: pl.id,
    label: pl.label,
    detail: pl.id === 'custom' ? 'you set g' : gravityOf[pl.environment] != null ? `${gravityOf[pl.environment]} g` : null,
  }))

  const fuels = (options.data?.fuels ?? []).filter((f) => f.rows >= MIN_FUEL_ROWS).map((f) => f.name)
  const blocked = Object.keys(errors).length > 0

  const submit = (e) => {
    e.preventDefault()
    if (!blocked) navigate(`/comparison?${formToParams(form)}`)
  }

  return (
    <div className="scenario">
      <header className="scenario-head">
        <h1>Scenario Explorer</h1>
        <p className="scenario-lede">
          Describe the fire scenario you care about. Enter only what you know: an empty field stays empty, and FLARE
          ranks NASA's tests only on what you set.
        </p>
      </header>

      {options.status === 'error' && <LoadError what="NASA's tested ranges" retry={options.retry} />}

      <form className="scenario-form" onSubmit={submit} noValidate>
        <Stops
          name="place"
          legend="Environment"
          note="sets gravity"
          options={places}
          value={form.place}
          onChange={set('place')}
        />

        {form.place === 'custom' && (
          <div className="row">
            <label className="row-label" htmlFor="gravity">
              <span className="row-name">Gravity</span>
              <span className="row-unit">g, 0 to 1</span>
            </label>
            <div className="row-field">
              <div className="field-line">
                <input
                  id="gravity"
                  className="field-input"
                  inputMode="decimal"
                  autoComplete="off"
                  value={form.gravity}
                  onChange={(e) => set('gravity')(e.target.value)}
                  aria-invalid={errors.gravity ? true : undefined}
                  aria-describedby={errors.gravity ? 'gravity-error' : undefined}
                />
                <span className="field-unit">g</span>
              </div>
              {errors.gravity && (
                <p id="gravity-error" className="field-error">
                  <TriangleAlert size={16} aria-hidden="true" />
                  {errors.gravity}
                </p>
              )}
            </div>
            <div className="row-span">
              <p className="span-words">
                <span>PSI holds microgravity and normal-gravity tests only.</span>
              </p>
            </div>
          </div>
        )}

        <GravityScale place={form.place} customGravity={form.gravity} environments={gravityOf} />

        <NumberRow
          id="oxygen"
          label="Oxygen"
          unit="%"
          value={form.oxygen}
          onChange={set('oxygen')}
          converted={oxygen != null && !errors.oxygen ? `= ${formatValue(oxygen / 100)} mole fraction` : null}
          error={errors.oxygen}
          hint={hints.oxygen}
          refs={oxygenRefs}
          applied={applied.oxygen}
          span={<SpanLane {...spanFor('oxygen', errors.oxygen ? null : oxygen)} bounds={[0, 100]} />}
        />

        <NumberRow
          id="pressure"
          label="Pressure"
          unit={form.pUnit}
          unitControl={
            <select
              className="field-select"
              aria-label="Pressure unit"
              value={form.pUnit}
              onChange={(e) => changeUnit(e.target.value)}
            >
              {PRESSURE_UNITS.map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </select>
          }
          value={form.pressure}
          onChange={set('pressure')}
          converted={
            pressure != null && !errors.pressure && form.pUnit !== 'atm'
              ? `= ${formatValue(toAtm(pressure, form.pUnit))} atm`
              : null
          }
          error={errors.pressure}
          refs={pressureRefs}
          applied={applied.pressure}
          span={<SpanLane {...spanFor('pressure', errors.pressure ? null : pressure)} />}
        />

        <NumberRow
          id="flow"
          label="Airflow"
          unit="cm/s"
          value={form.flow}
          onChange={set('flow')}
          error={errors.flow}
          refs={[]}
          span={<SpanLane {...spanFor('flow_velocity', errors.flow ? null : flow)} />}
        />

        <Stops
          name="fuel_phase"
          legend="Fuel phase"
          options={FUEL_PHASES.map((p) => ({ id: p, label: p }))}
          value={form.fuelPhase}
          onChange={set('fuelPhase')}
        />

        <div className="row">
          <label className="row-label" htmlFor="fuel">
            <span className="row-name">Fuel</span>
            <span className="row-unit">or material</span>
          </label>
          <div className="row-field">
            <input
              id="fuel"
              className="field-input field-text"
              list="fuel-names"
              autoComplete="off"
              value={form.fuel}
              onChange={(e) => set('fuel')(e.target.value)}
            />
            <datalist id="fuel-names">
              {fuels.map((name) => (
                <option key={name} value={name} />
              ))}
            </datalist>
          </div>
          <div className="row-span">
            <p className="span-words">
              <span>Matched against the fuel names in NASA's tables</span>
              {fuels.length > 0 && <span>Suggestions: the {fuels.length} fuels with at least {MIN_FUEL_ROWS} rows</span>}
            </p>
          </div>
        </div>

        <Stops
          name="concern"
          legend="Concern"
          options={CONCERNS.map((c) => ({ id: c, label: c }))}
          value={form.concern}
          onChange={set('concern')}
        />

        <div className="scenario-submit">
          <button type="submit" className="button" disabled={blocked}>
            Compare investigations
            <ArrowRight size={18} aria-hidden="true" />
          </button>
          <p className="submit-note">
            {errors.form ??
              (blocked
                ? 'Fix the fields marked above first.'
                : 'Opens the ranked comparison. Its link keeps this scenario, so you can share it.')}
          </p>
        </div>

        <p className="scenario-source">
          Reference values come from the{' '}
          <a href={REFERENCE_SOURCE.url} target="_blank" rel="noreferrer">
            {REFERENCE_SOURCE.label}
          </a>
          . NASA states none for a spacecraft, a space station or a Mars habitat, so FLARE offers none.
        </p>
      </form>
    </div>
  )
}
