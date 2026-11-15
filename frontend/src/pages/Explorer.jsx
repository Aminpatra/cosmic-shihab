import { Link, useSearchParams } from 'react-router'
import { useApi } from '../api.js'
import { byAccession, countOf, formatNumber, nameOf } from '../catalogue.js'
import { Empty, LoadError, Loading } from '../components/ApiState.jsx'
import ExplorerSearch from './ExplorerSearch.jsx'
import { FILTERS, matchesFilters, optionsFor, readFilters, tagValues } from './ExplorerFilters.js'
import './Explorer.css'

const COLUMNS = [
  ['platform', 'Platform'],
  ['fuel_phase', 'Fuel phase'],
  ['gravity_level', 'Gravity'],
  ['flare_data', 'Data in FLARE'],
]

function Tags({ inv, field }) {
  const values = tagValues(inv, field)
  return values.length ? values.join(', ') : <span className="absent">Not stated</span>
}

function Investigations({ investigations, params, setParams }) {
  const selected = readFilters(params)
  const active = Object.keys(selected).length > 0
  const rows = investigations.filter((inv) => matchesFilters(inv, selected)).sort(byAccession)

  const update = (change) =>
    setParams(
      (prev) => {
        const p = new URLSearchParams(prev)
        change(p)
        return p
      },
      { replace: true, preventScrollReset: true },
    )
  const toggle = (key, value) =>
    update((p) => {
      const values = p.getAll(key)
      p.delete(key)
      const next = values.includes(value) ? values.filter((v) => v !== value) : [...values, value]
      next.forEach((v) => p.append(key, v))
    })
  const clear = () => update((p) => FILTERS.forEach(({ key }) => p.delete(key)))

  return (
    <section className="ex-list" aria-labelledby="list-title">
      <h2 id="list-title" className="ex-h2">
        Investigations
      </h2>
      <div className="ex-filters">
        {FILTERS.map(({ key, label }) => (
          <fieldset key={key} className="ex-filter">
            <legend className="ex-filter-label">{label}</legend>
            <div className="ex-chips">
              {optionsFor(investigations, key).map(({ value, count }) => {
                const on = selected[key]?.has(value) ?? false
                return (
                  <button
                    key={value}
                    type="button"
                    className="ex-chip"
                    aria-pressed={on}
                    onClick={() => toggle(key, value)}
                  >
                    {value}
                    <span className="ex-chip-count">{count}</span>
                  </button>
                )
              })}
            </div>
          </fieldset>
        ))}
      </div>

      <div className="ex-showing">
        <p aria-live="polite">
          Showing {rows.length} of {investigations.length}
          {active && ' that match every group you chose (any choice within a group)'}
        </p>
        {active && (
          <button type="button" className="button-quiet" onClick={clear}>
            Clear filters
          </button>
        )}
      </div>

      {rows.length === 0 ? (
        <p className="ex-message">No investigation carries all of those tags. Clear a filter to widen the list.</p>
      ) : (
        <div className="ex-table-wrap">
          <table className="ex-table">
            <caption className="visually-hidden">NASA PSI combustion investigations, filtered</caption>
            <thead>
              <tr>
                <th scope="col">Investigation</th>
                {COLUMNS.map(([, label]) => (
                  <th key={label} scope="col">
                    {label}
                  </th>
                ))}
                <th scope="col" className="num">
                  PSI files
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((inv) => (
                <tr key={inv.accession}>
                  <th scope="row" data-label="Investigation">
                    <Link className="ex-name" to={`/explorer/${inv.accession}`}>
                      {nameOf(inv)}
                    </Link>{' '}
                    {nameOf(inv) !== inv.accession && <span className="id ex-acc">{inv.accession}</span>}
                    <span className="ex-title">{inv.title}</span>
                  </th>
                  {COLUMNS.map(([field, label]) => (
                    <td key={field} data-label={label}>
                      <Tags inv={inv} field={field} />
                    </td>
                  ))}
                  <td data-label="PSI files" className="num">
                    {inv.derived?.file_count != null ? formatNumber(inv.derived.file_count) : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="ex-source">
        {investigations.find((inv) => inv.derived?.tags?.note)?.derived.tags.note} “Not stated” means the tag is
        empty for that investigation.
      </p>
    </section>
  )
}

export default function Explorer() {
  const [params, setParams] = useSearchParams()
  const list = useApi('/investigations')
  // The count comes from the API, never the copy: PSI adds investigations over time (#47).
  const count = list.status === 'ready' ? list.data.length : 0

  return (
    <div className="explorer">
      <header className="ex-head">
        <h1>NASA Research Explorer</h1>
        <p className="ex-lede">
          The {count > 0 ? countOf(count, 'NASA combustion investigation') : 'NASA combustion investigations'} in PSI.
          Search inside their documents, filter them by what they tested, and open any one for its record and its NASA
          files.
        </p>
      </header>

      <ExplorerSearch />

      {list.status === 'loading' && <Loading label="Loading the PSI catalogue…" />}
      {list.status === 'error' && <LoadError what="The PSI catalogue" retry={list.retry} error={list.error} />}
      {list.status === 'ready' && count === 0 && <Empty what="The PSI catalogue" retry={list.retry} />}
      {list.status === 'ready' && count > 0 && (
        <Investigations investigations={list.data} params={params} setParams={setParams} />
      )}
    </div>
  )
}
