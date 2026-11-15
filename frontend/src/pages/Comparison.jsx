import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { ArrowRight, CircleDashed, Equal, EqualNot, Orbit, RotateCcw } from 'lucide-react'
import { getJSON, useApi } from '../api.js'
import { nameOf } from '../catalogue.js'
import AiSummary from '../components/AiSummary.jsx'
import ConditionLanes from '../components/ConditionLanes.jsx'
import { LoadError, Loading } from '../components/ApiState.jsx'
import { PLACES, formatValue, hasScenario, paramsToForm, rankPath } from './ScenarioParams.js'
import { LANE_VARIABLES, countsOf, figuresFor, formatCell, parsePicks, weightVariables } from './ComparisonLanes.js'
import { presetForm, presetLink, readingFor } from './ComparisonReading.js'
import './Comparison.css'

const MAX_PICKS = 3
const SHOWN = 6 // ranked rows shown before "Show all"; picked rows always show

// "test_day" -> "test days", "fuel_summary" -> "fuel summaries"
function unitWord(unit, n) {
  const word = String(unit ?? 'row').replace(/_/g, ' ')
  if (n === 1) return word
  return /[^aeiou]y$/.test(word) ? `${word.slice(0, -1)}ies` : `${word}s`
}
const WEIGHT_DELAY = 300 // ms after the last slider move before re-ranking

// Like useApi, but keeps the last answer on screen while a re-rank loads, so moving a weight
// never blanks the page.
function useRanking(path) {
  const [state, setState] = useState({ status: 'loading', data: null, error: null })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    setState((s) => ({ ...s, status: s.data ? 'refreshing' : 'loading', error: null }))
    getJSON(path, { signal: controller.signal })
      .then((data) => setState({ status: 'ready', data, error: null }))
      .catch((error) => {
        if (error.name !== 'AbortError') setState({ status: 'error', data: null, error })
      })
    return () => controller.abort()
  }, [path, attempt])
  return { ...state, retry: () => setAttempt((n) => n + 1) }
}

// What the visitor entered, in the units they entered it.
function describe(params) {
  const form = paramsToForm(params)
  const place = PLACES.find((p) => p.id === form.place)
  const rows = []
  if (place) rows.push(['Environment', form.place === 'custom' && form.gravity ? `Custom, ${form.gravity} g` : place.label])
  if (form.oxygen) rows.push(['Oxygen', `${form.oxygen} %`])
  if (form.pressure) {
    const atm = Number(params.get('pressure'))
    rows.push(['Pressure', form.pUnit === 'atm' ? `${form.pressure} atm` : `${form.pressure} ${form.pUnit} (${formatValue(atm)} atm)`])
  }
  if (form.flow) rows.push(['Airflow', `${form.flow} cm/s`])
  if (form.fuelPhase) rows.push(['Fuel phase', form.fuelPhase])
  if (form.fuel) rows.push(['Fuel', form.fuel])
  if (form.concern) rows.push(['Concern', form.concern])
  return rows
}

function Counts({ item }) {
  const c = countsOf(item)
  return (
    <span className="counts">
      <span className="count count-match">
        <Equal size={14} strokeWidth={2.5} aria-hidden="true" />
        {c.match} match
      </span>
      <span className="count count-differs">
        <EqualNot size={14} strokeWidth={2.5} aria-hidden="true" />
        {c.differs} differs
      </span>
      <span className="count count-missing">
        <CircleDashed size={14} strokeWidth={2.5} aria-hidden="true" />
        {c.missing} not recorded
      </span>
    </span>
  )
}

function Weights({ method, variables, params, setParams }) {
  const fromUrl = () =>
    Object.fromEntries(variables.map((v) => [v, Number(params.get(`weight_${v}`) ?? method.weights?.[v] ?? 1)]))
  const [weights, setWeights] = useState(fromUrl)
  const timer = useRef(null)
  useEffect(() => () => clearTimeout(timer.current), [])

  const write = (next) => {
    setWeights(next)
    clearTimeout(timer.current)
    timer.current = setTimeout(() => {
      setParams(
        (prev) => {
          const p = new URLSearchParams(prev)
          for (const [v, w] of Object.entries(next)) {
            if (w === 1) p.delete(`weight_${v}`)
            else p.set(`weight_${v}`, String(w))
          }
          return p
        },
        { replace: true, preventScrollReset: true },
      )
    }, WEIGHT_DELAY)
  }
  const equal = variables.every((v) => weights[v] === 1)

  return (
    <fieldset className="cmp-weights">
      <legend className="cmp-label">Weights</legend>
      <div className="weight-list">
        {variables.map((v) => (
          <label key={v} className="weight">
            <span className="weight-name">{LANE_VARIABLES[v].label}</span>
            <input
              type="range"
              min="0"
              max="10"
              step="1"
              value={weights[v] ?? 1}
              onChange={(e) => write({ ...weights, [v]: Number(e.target.value) })}
            />
            <output className="weight-value">{weights[v] ?? 1}</output>
          </label>
        ))}
      </div>
      <div className="weight-foot">
        <p>{method.weights_reason}</p>
        <button
          type="button"
          className="button-quiet"
          disabled={equal}
          onClick={() => write(Object.fromEntries(variables.map((v) => [v, 1])))}
        >
          <RotateCcw size={16} aria-hidden="true" />
          Equal weights
        </button>
      </div>
    </fieldset>
  )
}

function Ranked({ items, notRanked, picks, toggle, notice }) {
  const [showAll, setShowAll] = useState(false)
  const full = picks.length >= MAX_PICKS
  const shown = showAll ? items : items.filter((item, i) => i < SHOWN || picks.includes(item.accession))
  return (
    <section className="cmp-ranked" aria-labelledby="ranked-title">
      <h2 id="ranked-title" className="cmp-h2">
        Ranked <span className="cmp-count">{items.length}</span>
      </h2>
      <p className="cmp-notice">{notice}</p>
      <p className="cmp-pick-note" aria-live="polite">
        {full
          ? 'Three picked, the most that fit side by side. Unpick one to compare another.'
          : `Pick up to ${MAX_PICKS} to compare below.`}
      </p>
      <ol className="ranked">
        {shown.map((item) => {
          const i = items.indexOf(item)
          const picked = picks.includes(item.accession)
          return (
            <li key={item.accession} className="ranked-row" data-picked={picked || undefined}>
              <label className="ranked-pick">
                <input
                  type="checkbox"
                  checked={picked}
                  disabled={!picked && full}
                  onChange={() => toggle(item.accession)}
                />
                <span className="visually-hidden">Compare {nameOf(item)}</span>
              </label>
              <span className="ranked-rank">{i + 1}</span>
              <div className="ranked-main">
                <p className="ranked-name">
                  <Link to={`/explorer/${item.accession}`}>{nameOf(item)}</Link>{' '}
                  <span className="id">{item.accession}</span>
                </p>
                <p className="ranked-title">{item.title}</p>
                <Counts item={item} />
                <p className="ranked-close">
                  {item.close_tests} of {item.rows_scored.toLocaleString('en-US')}{' '}
                  {unitWord(item.row_unit, item.rows_scored)} close to your scenario
                </p>
                {item.gravity_note && (
                  <p className="ranked-gravity">
                    <Orbit size={14} strokeWidth={2.5} aria-hidden="true" />
                    {item.gravity_note}
                  </p>
                )}
              </div>
              <p className="ranked-score">
                <span className="visually-hidden">Relevance score </span>
                {item.score}
              </p>
            </li>
          )
        })}
      </ol>
      {items.length > shown.length && (
        <button type="button" className="button-quiet ranked-more" onClick={() => setShowAll(true)}>
          Show all {items.length} ranked
        </button>
      )}
      {notRanked.length > 0 && (
        <div className="not-ranked">
          <h3 className="cmp-label">Not ranked ({notRanked.length})</h3>
          <ul>
            {notRanked.map((item) => (
              <li key={item.accession}>
                <Link to={`/explorer/${item.accession}`}>{nameOf(item)}</Link>{' '}
                <span className="id">{item.accession}</span>
                <span className="not-ranked-reason">{item.reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}

function ClosestTests({ items }) {
  return (
    <section className="cmp-tests" aria-labelledby="tests-title">
      <h2 id="tests-title" className="cmp-h2">
        Closest tests
      </h2>
      <p className="cmp-intro">
        The runs that scored best for each picked investigation, with NASA's own column names and units. FLARE's
        conversions are marked.
      </p>
      {items.map((item) => (
        <div key={item.accession} className="tests-group">
          <h3 className="tests-head">
            {nameOf(item)} <span className="id">{item.accession}</span>
            {item.doi && (
              <a href={`https://doi.org/${item.doi}`} target="_blank" rel="noreferrer" className="tests-doi">
                doi:<span className="id">{item.doi}</span>
              </a>
            )}
          </h3>
          {item.best_tests?.length ? (
            <ol className="tests">
              {item.best_tests.map((t) => (
                <li key={`${t.file}-${t.line}`} className="test">
                  <p className="test-head">
                    {t.run_id && <span>Run {t.run_id}</span>}
                    <span>
                      <span className="id">{t.file}</span>, line {t.line}
                    </span>
                    <span>score {t.score}</span>
                  </p>
                  <dl className="test-values">
                    {Object.entries(t.values).map(([variable, v]) => (
                      <div key={variable}>
                        <dt>{v.column}</dt>
                        <dd>{formatCell(v)}</dd>
                      </div>
                    ))}
                  </dl>
                </li>
              ))}
            </ol>
          ) : (
            <p className="cmp-intro">No single test carries the conditions you set.</p>
          )}
        </div>
      ))}
    </section>
  )
}

// The stored AI reading of this ranking (#28), when the scenario is one a reading was written for.
function Reading({ match }) {
  const { reading } = match
  if (!match.shown) {
    return (
      <p className="cmp-message">
        An AI reading was written for “{reading.label}”, but the ranking has changed since, so it is not shown: it would
        explain an order this page no longer displays.
      </p>
    )
  }
  return (
    <div className="cmp-reading">
      <AiSummary
        id="reading"
        title="Reading of this ranking"
        data={reading}
        intro={
          <>
            Written for “{reading.label}”, a scenario whose values the Flame in Freefall challenge page states. It explains
            the ranking below and does not change it.
          </>
        }
      />
    </div>
  )
}

// The scenarios a reading was written for, as links, so the empty page offers a start.
function PresetLinks() {
  const readings = useApi('/assistant/readings')
  if (readings.status !== 'ready' || readings.data.length === 0) return null
  return (
    <div className="cmp-presets">
      <p>Or start from a scenario the challenge page gives values for, with an AI reading of its ranking:</p>
      <ul>
        {readings.data.map((reading) => {
          const form = presetForm(reading.scenario)
          return (
            <li key={reading.preset}>
              <Link to={presetLink(reading)}>
                {reading.label}
                <ArrowRight size={16} aria-hidden="true" />
              </Link>
              <span>
                {form.oxygen} % oxygen, {form.pressure} psi
              </span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

function Results({ params, setParams }) {
  const ranking = useRanking(rankPath(params))
  const options = useApi('/rank/options')
  const readings = useApi('/assistant/readings')
  const data = ranking.data
  // The lanes draw in once, when the first figures appear; later picks and re-ranks just update.
  const ready = Boolean(data) && options.status !== 'loading'
  const [settled, setSettled] = useState(false)
  useEffect(() => {
    if (!ready || settled) return
    const timer = setTimeout(() => setSettled(true), 1800)
    return () => clearTimeout(timer)
  }, [ready, settled])

  // An error leaves no data, so it is checked before the loading line or it would never show.
  if (ranking.status === 'error') {
    return ranking.error?.status === 422 ? (
      <p className="cmp-message">
        The ranking refused a value in this scenario as out of range. <Link to={`/scenario?${params}`}>Edit the scenario</Link>.
      </p>
    ) : (
      <LoadError what="The ranking" retry={ranking.retry} error={ranking.error} />
    )
  }
  if (!ready) return <Loading label="Ranking NASA's tests against your scenario…" />
  const sliders = weightVariables(data.method, params)
  // When the sliders caused the message (every weight at 0), they stay below so it can be undone.
  if (data.message && sliders.length === 0) return <p className="cmp-message">{data.message}</p>

  const picks = parsePicks(params.get('pick'), data.items)
  const toggle = (accession) => {
    const next = picks.includes(accession) ? picks.filter((a) => a !== accession) : [...picks, accession]
    setParams(
      (prev) => {
        const p = new URLSearchParams(prev)
        p.set('pick', next.join(','))
        return p
      },
      { replace: true, preventScrollReset: true },
    )
  }
  const pickedItems = data.items.filter((item) => picks.includes(item.accession))
  const figures = figuresFor(data, picks, options.data)
  // A reading is extra: while it loads or if it fails, the ranking shows without it.
  const reading = readings.status === 'ready' ? readingFor(params, readings.data, data.items) : null
  const source = (
    <>
      Source: the experimental tables of{' '}
      {pickedItems.map((item, i) => (
        <span key={item.accession}>
          {i > 0 && (i === pickedItems.length - 1 ? ' and ' : ', ')}
          {nameOf(item)} (<span className="id">{item.accession}</span>)
        </span>
      ))}
      , ranked with method version {data.method.version}. Point at a row to see its source column.
    </>
  )

  return (
    <>
      {data.gravity_note && (
        <p className="cmp-gravity">
          <Orbit size={18} aria-hidden="true" />
          {data.gravity_note}
        </p>
      )}
      {reading && <Reading match={reading} />}
      <Weights method={data.method} variables={sliders} params={params} setParams={setParams} />

      {data.message ? (
        <p className="cmp-message">{data.message}</p>
      ) : data.items.length === 0 ? (
        <div className="cmp-body">
          <p className="cmp-message">No investigation could be ranked on these conditions.</p>
          <Ranked items={[]} notRanked={data.not_ranked} picks={[]} toggle={() => {}} notice={data.notice} />
        </div>
      ) : (
        <div className="cmp-body" data-refreshing={ranking.status === 'refreshing' || undefined}>
          <Ranked items={data.items} notRanked={data.not_ranked} picks={picks} toggle={toggle} notice={data.notice} />
          <div className="cmp-detail">
            <section className="cmp-figures" aria-labelledby="figures-title">
              <h2 id="figures-title" className="cmp-h2">
                Condition by condition
              </h2>
              {pickedItems.length === 0 ? (
                <p className="cmp-intro">Pick an investigation from the ranking to lay it against your scenario.</p>
              ) : (
                <>
                  <p className="cmp-intro">
                    Every row in a figure shares one axis, so your scenario sits at the same place on each.
                  </p>
                  {figures.map((f) => (
                    <ConditionLanes
                      key={f.variable}
                      caption={f.caption}
                      summary={f.summary}
                      theirsLabel="Tested range"
                      lanes={f.lanes}
                      source={source}
                      animate={!settled}
                    />
                  ))}
                </>
              )}
            </section>
            {pickedItems.length > 0 && <ClosestTests items={pickedItems} />}
          </div>
        </div>
      )}
    </>
  )
}

export default function Comparison() {
  const [params, setParams] = useSearchParams()
  const scenario = hasScenario(params)

  return (
    <div className="comparison">
      <header className="cmp-head">
        <h1>Investigation Comparison</h1>
        <p className="cmp-lede">
          NASA's tests ranked against your scenario. Pick up to three investigations to lay them on the same axes,
          condition by condition.
        </p>
      </header>

      {scenario ? (
        <>
          <section className="cmp-scenario" aria-label="Your scenario">
            <h2 className="cmp-label">Your scenario</h2>
            <dl className="cmp-conditions">
              {describe(params).map(([label, value]) => (
                <div key={label}>
                  <dt>{label}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
            <Link className="button-quiet" to={`/scenario?${params}`}>
              Edit scenario
            </Link>
          </section>
          <Results params={params} setParams={setParams} />
        </>
      ) : (
        <div className="cmp-empty">
          <span className="cmp-empty-lane" aria-hidden="true" />
          <p>
            No scenario yet. The comparison ranks NASA's tests against the conditions you set, and only those.
          </p>
          <Link className="button" to="/scenario">
            Set a scenario
            <ArrowRight size={18} aria-hidden="true" />
          </Link>
          <PresetLinks />
        </div>
      )}
    </div>
  )
}
