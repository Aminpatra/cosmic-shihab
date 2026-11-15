import { useDeferredValue, useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router'
import { ArrowRight, CircleDashed } from 'lucide-react'
import { getJSON } from '../api.js'
import { LoadError, Loading } from '../components/ApiState.jsx'
import FlexModel from '../components/FlexModel.jsx'
import { ScenarioProbeBar, comparisonLink, nearness, probeIsSet, useScenarioProbe } from '../components/ScenarioProbe.jsx'
import './Visualization.css'

// Charts follow research/analysis/README.md (#32): only tables whose rows are tests, suspect values
// left out (pressure at or below 0, negative flow velocity; the pipeline's flags never fall on a
// standard field of a test table), values written with ~, < or > left out of the FLEX panels.

const FIELDS = [
  { id: 'fuel', label: 'Fuel', short: 'Fuel', kind: 'text' },
  { id: 'oxygen', label: 'Oxygen', short: 'O₂', unit: 'mole fraction', kind: 'number' },
  { id: 'pressure', label: 'Pressure', short: 'Press.', unit: 'atm', kind: 'number' },
  { id: 'flow_velocity', label: 'Flow', short: 'Flow', full: 'Flow velocity', unit: 'cm/s', kind: 'number' },
  { id: 'burn_time', label: 'Burn time', short: 'Burn', unit: 's', kind: 'number' },
  { id: 'test_end', label: 'Test end', short: 'End', full: 'How the test ended', kind: 'text' },
]
const FLEX_FILE = 'PSI-69_Experimental table_FLEX.csv'
const FLEX = {
  oxygen: 'O initial ambient composition; mole fraction',
  helium: 'He initial ambient composition; mole fraction',
  rate: 'Burning rate; mm',
}

// --- data -----------------------------------------------------------------------------------

async function loadRuns(signal) {
  const tables = await getJSON('/runs', { signal })
  const rows = []
  for (let offset = 0; ; offset += 500) {
    const page = await getJSON(`/runs/rows?cells=false&limit=500&offset=${offset}`, { signal })
    rows.push(...page.items)
    if (offset + 500 >= page.total) break
  }
  const flex = await getJSON(`/runs/rows?table=${encodeURIComponent(FLEX_FILE)}&limit=500`, { signal })
  return { tables, rows, flexRows: flex.items }
}

function useRuns() {
  const [state, setState] = useState({ status: 'loading' })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    setState({ status: 'loading' })
    loadRuns(controller.signal)
      .then((data) => setState({ status: 'ready', data }))
      .catch((error) => error.name !== 'AbortError' && setState({ status: 'error', error }))
    return () => controller.abort()
  }, [attempt])
  return { ...state, retry: () => setAttempt((n) => n + 1) }
}

// In inverse-flame tables the oxygen is the burner stream's, not the gas around the flame.
const isInverse = (table) => /inverse/i.test(table.file)

const shortName = (table) =>
  `${table.accession} ${table.file.replace(/^PSI-\d+_Experimental table_/, '').replace(/\.csv$/, '').replace(/_/g, ' ')}`

// A standard field's single usable number, or null (absent, a list or range, or suspect).
function usableNumber(row, field) {
  const value = row.standard?.[field]?.value
  if (typeof value !== 'number') return null
  if (field === 'pressure' && value <= 0) return null
  if (field === 'flow_velocity' && value < 0) return null
  if (field === 'oxygen' && (value < 0 || value > 1)) return null
  return value
}

const usableText = (row, field) => row.standard?.[field]?.text?.trim() || null

function build({ tables, rows }) {
  const tests = tables.filter((t) => t.row_is === 'test')
  const byTable = Object.fromEntries(tests.map((t) => [t.file, []]))
  for (const row of rows) if (byTable[row.table]) byTable[row.table].push(row)
  const coverage = tests.map((table) => {
    const own = byTable[table.file]
    const cells = Object.fromEntries(
      FIELDS.map((f) => {
        if (!(f.id in table.standard_columns)) return [f.id, { recorded: false }]
        const n = own.filter((r) => (f.kind === 'number' ? usableNumber(r, f.id) !== null : usableText(r, f.id))).length
        return [f.id, { recorded: true, n, share: own.length ? n / own.length : 0, column: table.standard_columns[f.id] }]
      }),
    )
    return { table, rows: own, cells }
  })
  return { tests, coverage, byTable }
}

// --- scale helpers --------------------------------------------------------------------------

function niceTicks(min, max, count = 5) {
  if (min === max) return [min]
  const step0 = (max - min) / count
  const mag = 10 ** Math.floor(Math.log10(step0))
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= step0)
  // From the round number at or below min to the one at or above max, so an axis built on the
  // first and last tick always holds every value.
  const ticks = []
  const last = Math.ceil(max / step - 1e-9) * step
  for (let v = Math.floor(min / step + 1e-9) * step; v <= last + step * 1e-9; v += step) ticks.push(+v.toFixed(10))
  return ticks
}

const scale = (d0, d1, r0, r1) => (v) => r0 + ((v - d0) / (d1 - d0 || 1)) * (r1 - r0)
const fmt = (v) => (Math.abs(v) >= 100 ? v.toFixed(0) : Math.abs(v) >= 10 ? v.toFixed(1) : +v.toPrecision(3)).toString()
const jitter = (i) => (((i * 9301 + 49297) % 233280) / 233280) * 2 - 1

function median(values) {
  const s = [...values].sort((a, b) => a - b)
  const m = s.length >> 1
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2
}

// --- the coverage matrix ----------------------------------------------------------------------

function CoverageMatrix({ coverage, chosen, onChoose }) {
  return (
    <div className="matrix-wrap">
      <table className="matrix">
        <caption className="visually-hidden">
          Share of each test table's rows with one usable value, by field. Choose a cell to see its values.
        </caption>
        <thead>
          <tr>
            <th scope="col">Test table</th>
            {FIELDS.map((f) => (
              <th key={f.id} scope="col">
                {f.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {coverage.map(({ table, rows, cells }) => (
            <tr key={table.file}>
              <th scope="row">
                <span className="matrix-name">{shortName(table)}</span>
                <span className="matrix-n">{rows.length} tests</span>
              </th>
              {FIELDS.map((f) => {
                const cell = cells[f.id]
                if (!cell.recorded)
                  return (
                    <td key={f.id} className="matrix-absent">
                      <span className="matrix-field" aria-hidden="true">{f.short}</span>
                      <span className="visually-hidden">No {f.label.toLowerCase()} column</span>
                    </td>
                  )
                const on = chosen.table === table.file && chosen.field === f.id
                const pct = Math.round(cell.share * 100)
                return (
                  <td key={f.id}>
                    <button
                      type="button"
                      className="matrix-cell"
                      aria-pressed={on}
                      style={{ '--share': cell.share }}
                      onClick={() => onChoose({ table: table.file, field: f.id })}
                    >
                      <span className="matrix-field" aria-hidden="true">{f.short}</span>
                      {pct}%<span className="visually-hidden"> of {shortName(table)} has a usable {f.label.toLowerCase()}; show its values</span>
                    </button>
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// --- the chosen cell ---------------------------------------------------------------------------

// The rendered width of an element, so the strip is drawn at its real size (text stays legible).
function useWidth() {
  const ref = useRef(null)
  const [width, setWidth] = useState(720)
  useEffect(() => {
    const el = ref.current
    if (!el) return undefined
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(280, Math.round(entry.contentRect.width))))
    observer.observe(el)
    return () => observer.disconnect()
  }, [])
  return [ref, width]
}

function NumberStrip({ field, lanes, probe }) {
  const [ref, W] = useWidth()
  const all = lanes.flatMap((lane) => lane.points.map((p) => p.v))
  const lo = Math.min(...all)
  const hi = Math.max(...all)
  const ticks = niceTicks(lo, hi, W < 480 ? 4 : 5)
  const d0 = Math.min(lo, ticks[0])
  const d1 = Math.max(hi, ticks[ticks.length - 1])
  const x = scale(d0, d1, 24, W - 24)
  const step = 66
  const axisY = 34 + lanes.length * step - 10
  // The scenario on this field: a tick at its value (dashed at the edge when off this scale), the
  // ranking's window around it, and every value outside the window dimmed.
  // Lanes marked compare: false (burner-stream oxygen) get neither: their values are not the same quantity.
  const mark = probe ? { at: Math.min(W - 24, Math.max(24, x(probe.v))), off: probe.v < d0 || probe.v > d1 } : null
  const box = probe?.t != null ? [Math.max(24, x(probe.v - probe.t)), Math.min(W - 24, x(probe.v + probe.t))] : null
  const far = (lane, v) => lane.compare !== false && probe?.t != null && Math.abs(v - probe.v) > probe.t
  return (
    <div ref={ref} className="strip-box">
      <svg className="strip" viewBox={`0 0 ${W} ${axisY + 26}`} width={W} height={axisY + 26} role="img"
        aria-label={`${field.full ?? field.label} values`}>
        {lanes.map((lane, k) => {
          const cy = 40 + k * step
          return (
            <g key={lane.key}>
              <rect x="24" y={cy - 20} width={W - 48} height="40" className="strip-track" />
              {lane.compare !== false && box && box[1] > box[0] && (
                <rect x="0" y="0" width="1" height="1" className="probe-box"
                  style={{ transform: `translate(${box[0]}px, ${cy - 20}px) scale(${box[1] - box[0]}, 40)` }} />
              )}
              <text x="24" y={cy - 26} className="strip-label">
                {typeof lane.label === 'function' ? lane.label(W) : lane.label} ({lane.points.length})
              </text>
              {lane.points.map((p, i) => (
                <circle key={i} cx={x(p.v)} cy={cy + jitter(i) * 13} r={lane.own ? 4.5 : 3.5} className={`${lane.own ? 'dot-own' : lane.ring ? 'dot-other-ring' : 'dot-other'}${far(lane, p.v) ? ' is-far' : ''}`}>
                  <title>{`${fmt(p.v)} ${field.unit}${p.label ? ` · ${p.label}` : ''}`}</title>
                </circle>
              ))}
              {lane.compare !== false && mark && (
                <line x1="0" x2="0" y1={cy - 23} y2={cy + 23} className={`probe-tick${mark.off ? ' is-off' : ''}`}
                  style={{ transform: `translateX(${mark.at}px)` }} />
              )}
            </g>
          )
        })}
        {ticks.map((t) => (
          <g key={t}>
            <line x1={x(t)} x2={x(t)} y1={axisY} y2={axisY + 5} className="axis-tick" />
            <text x={x(t)} y={axisY + 21} className="axis-label" textAnchor="middle">
              {fmt(t)}
            </text>
          </g>
        ))}
        <line x1="24" x2={W - 24} y1={axisY} y2={axisY} className="axis-line" />
      </svg>
    </div>
  )
}

function TextCounts({ values }) {
  const counts = Object.entries(
    values.reduce((acc, v) => ((acc[v] = (acc[v] ?? 0) + 1), acc), {}),
  ).sort((a, b) => b[1] - a[1])
  const shown = counts.slice(0, 10)
  const rest = counts.slice(10).reduce((s, [, n]) => s + n, 0)
  const max = Math.max(...counts.map(([, n]) => n))
  return (
    <ul className="counts">
      {shown.map(([label, n]) => (
        <li key={label}>
          <span className="counts-label">{label}</span>
          <span className="counts-bar" style={{ '--w': n / max }} aria-hidden="true" />
          <span className="counts-n">{n}</span>
        </li>
      ))}
      {rest > 0 && (
        <li className="counts-rest">
          {counts.length - 10} other values written in PSI's table: {rest} tests
        </li>
      )}
    </ul>
  )
}

function ChosenCell({ model, chosen, figureRef, probe, tolerance }) {
  const field = FIELDS.find((f) => f.id === chosen.field)
  const entry = model.coverage.find((c) => c.table.file === chosen.table)
  const { table, rows, cells } = entry
  const cell = cells[field.id]
  const name = field.full ?? field.label
  const title = `${shortName(table)}, ${name.toLowerCase()}${field.unit ? ` (${field.unit})` : ''}`

  let figure
  let stats = null
  if (field.kind === 'number') {
    const own = rows.map((r) => ({ v: usableNumber(r, field.id), label: r.run_id })).filter((p) => p.v !== null)
    const pointsOf = (list) =>
      list.flatMap((c) => c.rows.map((r) => ({ v: usableNumber(r, field.id), label: shortName(c.table) }))).filter((p) => p.v !== null)
    const rest = model.coverage.filter((c) => c.table.file !== table.file && c.cells[field.id].recorded)
    const ownInverse = field.id === 'oxygen' && isInverse(table)
    const lanes = [{ key: 'own', own: true, compare: !ownInverse, label: ownInverse ? (W => (W < 400 ? 'This table, burner stream' : 'This table, burner-stream oxygen')) : 'This table', points: own }]
    if (field.id === 'oxygen') {
      // Burner-stream oxygen (inverse flames) is not the gas around the flame: never one lane with it.
      lanes.push({ key: 'ambient', label: W => (W < 400 ? 'Others, around the flame' : 'Other tables, oxygen around the flame'), points: pointsOf(rest.filter((c) => !isInverse(c.table))) })
      lanes.push({ key: 'burner', ring: true, compare: false, label: W => (W < 400 ? 'Inverse flames, burner stream' : 'Inverse flames, burner-stream oxygen'), points: pointsOf(rest.filter((c) => isInverse(c.table))) })
    } else {
      lanes.push({ key: 'others', label: 'All other test tables', points: pointsOf(rest) })
    }
    const mark = probe?.[field.id] != null ? { v: probe[field.id], t: tolerance?.[field.id] ?? null } : null
    figure = own.length ? <NumberStrip field={field} lanes={lanes.filter((l) => l.points.length)} probe={mark} /> : null
    if (own.length) {
      const v = own.map((p) => p.v)
      stats = `${own.length} values from ${fmt(Math.min(...v))} to ${fmt(Math.max(...v))} ${field.unit}, median ${fmt(median(v))}.`
    }
  } else {
    const values = rows.map((r) => usableText(r, field.id)).filter(Boolean)
    figure = values.length ? <TextCounts values={values} /> : null
    stats = 'Values are shown as PSI wrote them, spelling included.'
  }

  return (
    <figure className="chosen" aria-live="polite" ref={figureRef}>
      <figcaption>
        <h3>{title}</h3>
        <p>
          {cell.n} of {rows.length} tests have one usable value. {stats}
        </p>
      </figcaption>
      {figure ?? <p className="chosen-empty">No usable value to draw.</p>}
      <p className="footnote">
        Source: PSI column “{cell.column}” in <span className="id">{table.file}</span>. Suspect values left out.
        {field.kind === 'number' && ' All lanes share one scale.'}
        {field.id === 'oxygen' && ' Burner-stream oxygen from inverse flames is kept in its own lane: it does not describe the gas around the flame.'}
        {probe?.[field.id] != null && ' The yellow tick is your scenario; values outside the ranking’s window around it are dimmed.'}
      </p>
    </figure>
  )
}

// --- fixed figures -----------------------------------------------------------------------------

function Scatter({ points, context, x, y, xTicks, yTicks, ringed, label, xTitle, yTitle, probe, isFar }) {
  const [ref, W] = useWidth()
  const H = Math.round(W * 0.74)
  const L = 58
  const B = 52
  const sx = scale(x[0], x[1], L, W - 10)
  const sy = scale(y[0], y[1], H - B, 10)
  // The context layer never changes with the scenario: drawn once per size, not on every slider step.
  const contextDots = useMemo(
    () => context?.map((p, i) => <circle key={`c${i}`} cx={sx(p.x)} cy={sy(p.y)} r="2.5" className="dot-other" />),
    // sx and sy follow from these.
    [context, W, H, x[0], x[1], y[0], y[1]],
  )
  const clampX = (v) => Math.min(W - 10, Math.max(L, v))
  const clampY = (v) => Math.min(H - B, Math.max(10, v))
  // The scenario's window on whichever axes carry a variable it sets; full span on the other axis.
  const onX = probe?.x != null
  const onY = probe?.y != null
  const box =
    (onX && probe.tx != null) || (onY && probe.ty != null)
      ? {
          x0: onX && probe.tx != null ? clampX(sx(probe.x - probe.tx)) : L,
          x1: onX && probe.tx != null ? clampX(sx(probe.x + probe.tx)) : W - 10,
          y0: onY && probe.ty != null ? clampY(sy(probe.y + probe.ty)) : 10,
          y1: onY && probe.ty != null ? clampY(sy(probe.y - probe.ty)) : H - B,
        }
      : null
  return (
    <div ref={ref}>
      <svg className="scatter" viewBox={`0 0 ${W} ${H}`} width={W} height={H} role="img" aria-label={label}>
        <rect x={L} y="10" width={W - L - 10} height={H - B - 10} className="plot-bg" />
        {xTicks.map((t) => (
          <g key={`x${t}`}>
            <line x1={sx(t)} x2={sx(t)} y1="10" y2={H - B} className="grid" />
            <text x={sx(t)} y={H - B + 18} textAnchor="middle" className="axis-label">
              {fmt(t)}
            </text>
          </g>
        ))}
        {yTicks.map((t) => (
          <g key={`y${t}`}>
            <line x1={L} x2={W - 10} y1={sy(t)} y2={sy(t)} className="grid" />
            <text x={L - 8} y={sy(t) + 5} textAnchor="end" className="axis-label">
              {fmt(t)}
            </text>
          </g>
        ))}
        <text x={(L + W - 10) / 2} y={H - 8} textAnchor="middle" className="axis-title">
          {xTitle}
        </text>
        <text transform={`translate(15 ${(10 + H - B) / 2}) rotate(-90)`} textAnchor="middle" className="axis-title">
          {yTitle}
        </text>
        {contextDots}
        {box && box.x1 > box.x0 && box.y1 > box.y0 && (
          <rect x="0" y="0" width="1" height="1" className="probe-box"
            style={{ transform: `translate(${box.x0}px, ${box.y0}px) scale(${box.x1 - box.x0}, ${box.y1 - box.y0})` }} />
        )}
        {points.map((p, i) => (
          <circle key={i} cx={sx(p.x)} cy={sy(p.y)} r="4.5"
            className={`${ringed?.(p) ? 'dot-ring' : 'dot-own'}${isFar?.(p) ? ' is-far' : ''}`}>
            <title>{p.title}</title>
          </circle>
        ))}
        {onX && (
          <line x1="0" x2="0" y1="10" y2={H - B}
            className={`probe-tick${probe.x < x[0] || probe.x > x[1] ? ' is-off' : ''}`}
            style={{ transform: `translateX(${clampX(sx(probe.x))}px)` }} />
        )}
        {onY && (
          <line x1={L} x2={W - 10} y1="0" y2="0"
            className={`probe-tick${probe.y < y[0] || probe.y > y[1] ? ' is-off' : ''}`}
            style={{ transform: `translateY(${clampY(sy(probe.y))}px)` }} />
        )}
      </svg>
    </div>
  )
}

function ConditionSpace({ model, probe, tolerance, near }) {
  // Everything that does not depend on the scenario is built once, so moving a slider only
  // re-styles the dots and moves the marks.
  const layout = useMemo(() => {
    const panels = model.coverage.filter((c) => c.cells.oxygen.recorded && c.cells.pressure.recorded)
    const pts = (c) =>
      c.rows
        .map((r) => ({ x: usableNumber(r, 'oxygen'), y: usableNumber(r, 'pressure'), run: r.run_id }))
        .filter((p) => p.x !== null && p.y !== null)
    const own = new Map(panels.map((c) => [c, pts(c)]))
    const every = panels.flatMap((c) => own.get(c))
    const xTicks = niceTicks(0, Math.max(...every.map((p) => p.x)), 4)
    const yTicks = niceTicks(0, Math.max(...every.map((p) => p.y)), 4)
    return {
      xTicks,
      yTicks,
      x: [0, xTicks[xTicks.length - 1]],
      y: [0, yTicks[yTicks.length - 1]],
      panels: panels.map((c) => ({
        c,
        own: own.get(c).map((p) => ({ ...p, title: `${fmt(p.x)} O₂, ${fmt(p.y)} atm · ${p.run}` })),
        context: panels.filter((o) => o !== c).flatMap((o) => own.get(o)),
      })),
    }
  }, [model])
  const { panels, x, y, xTicks, yTicks } = layout
  const mark = probeIsSet(probe)
    ? { x: probe.oxygen, y: probe.pressure, tx: tolerance?.oxygen ?? null, ty: tolerance?.pressure ?? null }
    : null
  const isFar = near ? (p) => !near({ oxygen: p.x, pressure: p.y }) : null
  return (
    <figure className="fixed-figure">
      <figcaption>
        <h3>Where the tests sit in oxygen and pressure</h3>
        <p>
          Each panel: one table's tests over every other table's tests. Empty areas were not tested in these tables. Oxygen as
          a mole fraction, pressure in atm.
        </p>
      </figcaption>
      <Legend items={[['dot-own', 'This table'], ['dot-other', 'Every other table']]} />
      {mark && <ProbeKey dimmed={Boolean(near)} />}
      <div className="multiples">
        {panels.map(({ c, own, context }) => {
          const inverse = /inverse/i.test(c.table.file)
          // Burner-stream oxygen is not the gas around the flame: these panels are not compared with the scenario.
          const nearCount = near && !inverse ? own.filter((p) => near({ oxygen: p.x, pressure: p.y })).length : null
          return (
            <div key={c.table.file} className="multiple">
              <p className="multiple-head">
                <strong>{shortName(c.table)}</strong>
                <span>
                  {own.length} of {c.rows.length} tests
                  {nearCount != null && `, ${nearCount} in the window`}
                </span>
              </p>
              <Scatter
                points={own}
                context={context}
                xTitle="Oxygen (mole fraction)"
                yTitle="Pressure (atm)"
                x={x}
                y={y}
                xTicks={xTicks}
                yTicks={yTicks}
                label={`${shortName(c.table)}: oxygen against pressure`}
                probe={inverse && mark ? { ...mark, tx: null, ty: null } : mark}
                isFar={inverse ? null : isFar}
              />
              {inverse && <p className="multiple-note">Oxygen here is the burner stream's, not the surrounding gas's.</p>}
            </div>
          )
        })}
      </div>
      <p className="footnote">
        Source: the oxygen and pressure columns of each PSI table, converted to common units by FLARE. Suspect values
        left out. In the two inverse-flame tables the oxygen does not describe a cabin atmosphere.
      </p>
    </figure>
  )
}

/** The key for the scenario marks, shown only while a scenario is set. */
function ProbeKey({ dimmed, note }) {
  return (
    <p className="probe-key">
      <svg width="18" height="14" aria-hidden="true">
        <line x1="9" x2="9" y1="0" y2="14" className="probe-tick" />
      </svg>
      Your scenario
      {dimmed && (
        <>
          <svg width="18" height="14" aria-hidden="true">
            <rect x="1.5" y="1.5" width="15" height="11" className="probe-box" />
          </svg>
          The ranking’s window around it; tests outside are dimmed
        </>
      )}
      {note && <span className="probe-key-note">{note}</span>}
    </p>
  )
}

function Legend({ items }) {
  return (
    <ul className="legend">
      {items.map(([cls, label]) => (
        <li key={label}>
          <svg width="14" height="14" aria-hidden="true">
            <circle cx="7" cy="7" r="5" className={cls} />
          </svg>
          {label}
        </li>
      ))}
    </ul>
  )
}

function FlexBurningRate({ flexRows, probe, tolerance, near }) {
  const plain = (c) => c?.kind === 'number' && !c.approx && !c.bound
  const rows = flexRows.filter((r) => plain(r.cells?.[FLEX.oxygen]) && plain(r.cells?.[FLEX.rate]))
  const fuels = [...new Set(rows.map((r) => r.standard?.fuel?.text).filter(Boolean))].sort()
  const points = rows.map((r) => ({
    x: r.cells[FLEX.oxygen].value,
    y: r.cells[FLEX.rate].value,
    helium: (r.cells[FLEX.helium]?.value ?? 0) > 0,
    fuel: r.standard.fuel.text,
    run: r.run_id,
    pressure: usableNumber(r, 'pressure'),
  }))
  // Burning rate is the y axis, so only oxygen can be drawn; pressure still decides what is dimmed.
  const mark = probe?.oxygen != null ? { x: probe.oxygen, y: null, tx: tolerance?.oxygen ?? null, ty: null } : null
  const isFar = near ? (p) => !near({ oxygen: p.x, pressure: p.pressure }) : null
  const xTicks = niceTicks(Math.min(...points.map((p) => p.x)), Math.max(...points.map((p) => p.x)), 4)
  const yTicks = niceTicks(0, Math.max(...points.map((p) => p.y)), 4)
  return (
    <figure className="fixed-figure">
      <figcaption>
        <h3>FLEX: droplet burning rate by oxygen</h3>
        <p>
          One dot per FLEX test that gives both values. Pressure, droplet size and the inert gas also vary across these
          tests, so the panels show a pattern in these tests, not a cause.
        </p>
      </figcaption>
      <Legend items={[['dot-own', 'No helium in the gas'], ['dot-ring', 'With helium']]} />
      {probeIsSet(probe) && (
        <ProbeKey
          dimmed={Boolean(near)}
          note={probe.pressure != null ? 'Pressure is not drawn here but counts toward the window.' : null}
        />
      )}
      <div className="multiples multiples-2">
        {fuels.map((fuel) => {
          const own = points.filter((p) => p.fuel === fuel)
          const he = own.filter((p) => p.helium).length
          return (
            <div key={fuel} className="multiple">
              <p className="multiple-head">
                <strong>{fuel}</strong>
                <span>
                  {own.length} tests, {he} with helium
                  {isFar && `, ${own.filter((p) => !isFar(p)).length} in the window`}
                </span>
              </p>
              <Scatter
                points={own.map((p) => ({
                  ...p,
                  title: `${fmt(p.x)} O₂, burning rate ${fmt(p.y)}${p.helium ? ', with helium' : ''} · test ${p.run}`,
                }))}
                ringed={(p) => p.helium}
                x={[xTicks[0], xTicks[xTicks.length - 1]]}
                y={[0, yTicks[yTicks.length - 1]]}
                xTicks={xTicks}
                yTicks={yTicks}
                label={`FLEX ${fuel}: burning rate against initial oxygen`}
                xTitle="Initial oxygen (mole fraction)"
                yTitle="Burning rate (PSI: mm)"
                probe={mark}
                isFar={isFar}
              />
            </div>
          )
        })}
      </div>
      <p className="footnote">
        Source: <span className="id">{FLEX_FILE}</span>, columns “{FLEX.oxygen}” (x) and “{FLEX.rate}” (y). PSI heads
        the burning-rate column “mm”; a burning-rate constant is usually mm²/s, but PSI does not say so and FLARE does
        not change it. Values written with ~, &lt; or &gt; are left out.
      </p>
    </figure>
  )
}

// --- tests near the scenario ---------------------------------------------------------------------

// Oxygen from inverse-flame tables is the burner stream's: never counted as the gas around a flame.
const comparable = (table, variable) => !(variable === 'oxygen' && isInverse(table))

const VARS = [
  { id: 'oxygen', label: 'Oxygen', unit: 'mole fraction' },
  { id: 'pressure', label: 'Pressure', unit: 'atm' },
]

/** Every comparable test's value of one variable, as a histogram on a lane, with the scenario on it. */
function DensityLane({ variable, values, value, tol }) {
  const [ref, W] = useWidth()
  const ticks = niceTicks(0, Math.max(...values), W < 480 ? 4 : 5)
  const d1 = ticks[ticks.length - 1]
  const x = scale(0, d1, 0, W)
  const BINS = W < 480 ? 20 : 32
  const bins = useMemo(() => {
    const counts = new Array(BINS).fill(0)
    for (const v of values) counts[Math.min(BINS - 1, Math.floor((v / d1) * BINS))] += 1
    return counts
  }, [values, d1, BINS])
  const peak = Math.max(...bins)
  const H = 72
  const bw = W / BINS
  const inWindow = (i) => value != null && tol != null && Math.abs((i + 0.5) * (d1 / BINS) - value) <= tol + d1 / BINS / 2
  const nearN = value != null && tol != null ? values.filter((v) => Math.abs(v - value) <= tol).length : null
  return (
    <div className="density">
      <p className="density-head">
        <strong>{variable.label}</strong> <span className="probe-unit">{variable.unit}</span>
        <span className="density-n">
          {nearN != null
            ? `${nearN.toLocaleString('en-US')} of ${values.length.toLocaleString('en-US')} tests in the window`
            : `${values.length.toLocaleString('en-US')} tests`}
        </span>
      </p>
      <div ref={ref} className="density-box">
        <svg viewBox={`0 0 ${W} ${H + 30}`} width={W} height={H + 30} role="img"
          aria-label={`${variable.label}: how many tests ran at each value${nearN != null ? `; ${nearN} within the window around your scenario` : ''}`}>
          <rect x="0" y="0" width={W} height={H} className="strip-track" />
          {bins.map((n, i) =>
            n ? (
              <rect key={i} x={i * bw + 1} y={H - (n / peak) * (H - 6)} width={Math.max(1, bw - 2)} height={(n / peak) * (H - 6)}
                className={`bin${inWindow(i) ? ' bin-near' : ''}`}>
                <title>{`${n} tests from ${fmt((i * d1) / BINS)} to ${fmt(((i + 1) * d1) / BINS)} ${variable.unit}`}</title>
              </rect>
            ) : null,
          )}
          {value != null && tol != null && (
            <rect x="0" y="0" width="1" height="1" className="probe-box"
              style={{ transform: `translate(${Math.max(0, x(value - tol))}px, 0px) scale(${Math.max(0, Math.min(W, x(value + tol)) - Math.max(0, x(value - tol)))}, ${H})` }} />
          )}
          {value != null && (
            <line x1="0" x2="0" y1="-5" y2={H + 5} className={`probe-tick${value > d1 ? ' is-off' : ''}`}
              style={{ transform: `translateX(${Math.min(W - 1.5, Math.max(1.5, x(value)))}px)` }} />
          )}
          {ticks.map((t) => (
            <g key={t}>
              <line x1={x(t)} x2={x(t)} y1={H} y2={H + 5} className="axis-tick" />
              <text x={Math.min(W - 14, Math.max(10, x(t)))} y={H + 22} className="axis-label" textAnchor="middle">
                {fmt(t)}
              </text>
            </g>
          ))}
        </svg>
      </div>
    </div>
  )
}

function NearScenario({ model, probe, tolerance, near }) {
  const values = useMemo(
    () =>
      Object.fromEntries(
        VARS.map((v) => [
          v.id,
          model.coverage
            .filter((c) => c.cells[v.id].recorded && comparable(c.table, v.id))
            .flatMap((c) => c.rows.map((r) => usableNumber(r, v.id)).filter((n) => n !== null)),
        ]),
      ),
    [model],
  )
  const set = VARS.filter((v) => probe[v.id] != null)
  const words = set.map((v) => v.label.toLowerCase()).join(' and ')

  // Per table: how many tests fall in the window on every set variable, out of those that record them all.
  const rows = near
    ? model.coverage
        .map(({ table, rows: tests, cells }) => {
          const missing = set.find((v) => !cells[v.id].recorded)
          const burner = set.some((v) => !comparable(table, v.id))
          if (missing || burner) return { table, missing, burner, near: 0, compared: 0 }
          const read = tests.map((r) => ({ oxygen: usableNumber(r, 'oxygen'), pressure: usableNumber(r, 'pressure') }))
          const compared = read.filter((t) => set.every((v) => t[v.id] !== null))
          return { table, near: compared.filter(near).length, compared: compared.length }
        })
        .sort((a, b) => b.near - a.near || b.compared - a.compared)
    : []
  const total = rows.reduce((s, r) => s + r.near, 0)
  const tables = rows.filter((r) => r.near > 0).length
  const most = Math.max(1, ...rows.map((r) => r.near))

  return (
    <figure className="fixed-figure near">
      <figcaption>
        <h3>How many NASA tests sit near your scenario</h3>
        <p>
          {near
            ? `${total === 0 ? 'No test falls' : `${total.toLocaleString('en-US')} ${total === 1 ? 'test' : 'tests'} in ${tables} ${tables === 1 ? 'table' : 'tables'} ${total === 1 ? 'falls' : 'fall'}`} inside the window on ${words}. Move a slider or pick a preset and every chart on this page redraws.`
            : 'Each lane counts the tests run at each value. Set oxygen or pressure in the bar above, or pick a preset, to see how many tests sit near it.'}
        </p>
      </figcaption>
      <div className="density-lanes">
        {VARS.map((v) => (
          <DensityLane key={v.id} variable={v} values={values[v.id]} value={probe[v.id]} tol={tolerance?.[v.id] ?? null} />
        ))}
      </div>
      {near && (
        <>
          <ul className="near-list" aria-label={`Tests in the window, by table`}>
            {rows.map((r) => (
              <li key={r.table.file}>
                <span className="near-name">{shortName(r.table)}</span>
                {r.missing || r.burner ? (
                  <>
                    <span className="near-bar near-absent" aria-hidden="true" />
                    <span className="near-n near-missing">
                      <CircleDashed size={16} aria-hidden="true" />
                      {r.missing ? `No ${r.missing.label.toLowerCase()} recorded` : 'Burner-stream oxygen'}
                    </span>
                  </>
                ) : (
                  <>
                    <span className="near-bar" aria-hidden="true">
                      <span style={{ '--w': r.near / most }} />
                    </span>
                    <span className="near-n">
                      {r.near} of {r.compared}
                    </span>
                  </>
                )}
              </li>
            ))}
          </ul>
          <p className="near-action">
            <Link to={comparisonLink(probe)}>
              Rank the investigations for this scenario
              <ArrowRight size={18} aria-hidden="true" />
            </Link>
          </p>
        </>
      )}
      <p className="footnote">
        Window: the ranking’s own tolerance, a quarter of each variable’s span across every scorable test (
        <Link to="/methodology#ranking">How ranking works</Link>). A test that did not record a variable the scenario sets
        is never counted as near, as in the ranking. Oxygen from the two inverse-flame tables is left out: it is the burner
        stream’s. Presets: NASA Space Apps 2026 challenge “Flame in Freefall”, Potential Considerations. A count of nearby
        tests says where NASA has evidence, not how a fire would behave.
      </p>
    </figure>
  )
}

// --- page -------------------------------------------------------------------------------------

export default function Visualization() {
  const runs = useRuns()
  const model = useMemo(() => (runs.status === 'ready' ? build(runs.data) : null), [runs.status, runs.data])
  const [chosen, setChosen] = useState({ table: FLEX_FILE, field: 'oxygen' })
  const figureRef = useRef(null)
  const choose = (next) => {
    setChosen(next)
    // On a phone the figure sits below the whole matrix: bring it into view so the choice shows.
    if (window.matchMedia('(max-width: 44.9375em)').matches) {
      const smooth = !window.matchMedia('(prefers-reduced-motion: reduce)').matches
      requestAnimationFrame(() => figureRef.current?.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto', block: 'start' }))
    }
  }
  const testCount = model?.coverage.reduce((s, c) => s + c.rows.length, 0)
  // One scenario for every chart. The charts read a deferred copy, so the slider never waits on a redraw.
  const scenario = useScenarioProbe()
  const probe = useDeferredValue(scenario.probe)
  const near = useMemo(() => nearness(probe, scenario.tolerance), [probe, scenario.tolerance])

  return (
    <>
      <title>Data Visualization · FLARE</title>
      <section className="viz">
        <header className="viz-head">
          <h1>Data visualization</h1>
          <p className="viz-lede">
            What NASA's experimental tables actually recorded, drawn from their test rows only. Choose a cell to see its
            values among every test that records the same field.
          </p>
        </header>

        <ScenarioProbeBar {...scenario} />

        {runs.status === 'loading' && <Loading label="Loading PSI's test rows…" />}
        {runs.status === 'error' && <LoadError what="The experimental tables" retry={runs.retry} error={runs.error} />}

        {model && (
          <>
            <div className="viz-block">
              <h2>
                What each test table recorded{' '}
                <span className="viz-count">
                  {model.coverage.length} tables, {testCount.toLocaleString('en-US')} tests
                </span>
              </h2>
              <p className="viz-key">
                <span className="key-group">
                  <span className="key-swatch key-full" aria-hidden="true" /> Shade: share of the table's tests with one
                  usable value
                </span>
                <span className="key-group">
                  <span className="key-swatch key-absent" aria-hidden="true" /> Hatched: the table has no such column
                </span>
              </p>
              <CoverageMatrix coverage={model.coverage} chosen={chosen} onChoose={choose} />
              <ChosenCell model={model} chosen={chosen} figureRef={figureRef} probe={probe} tolerance={scenario.tolerance} />
            </div>
            <div className="viz-block">
              <ConditionSpace model={model} probe={probe} tolerance={scenario.tolerance} near={near} />
            </div>
            <div className="viz-block">
              <NearScenario model={model} probe={probe} tolerance={scenario.tolerance} near={near} />
            </div>
            <div className="viz-block">
              <FlexBurningRate flexRows={runs.data.flexRows} probe={probe} tolerance={scenario.tolerance} near={near} />
            </div>
            <div className="viz-block">
              <FlexModel />
            </div>
            <p className="viz-provenance">
              Drawn from NASA PSI's experimental tables, processed by FLARE; only tables whose rows are tests. How the
              tables were read and which values count as suspect: <Link to="/methodology#tables">Methodology</Link>.
            </p>
          </>
        )}
      </section>
    </>
  )
}
