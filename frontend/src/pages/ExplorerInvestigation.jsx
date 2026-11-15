import { useEffect, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router'
import { ArrowLeft, ArrowRight } from 'lucide-react'
import { useApi } from '../api.js'
import { formatDate, formatNumber, nameOf } from '../catalogue.js'
import { LoadError, Loading } from '../components/ApiState.jsx'
import AiSummary from '../components/AiSummary.jsx'
import ExplorerSearch from './ExplorerSearch.jsx'
import { FILTERS, tagValues } from './ExplorerFilters.js'
import './Explorer.css'

const FILE_PAGE = 25
const PUBLICATIONS_SHOWN = 10
const TEXT_FIELDS = [
  ['objective', 'Objective'],
  ['hypothesis', 'Hypothesis'],
  ['approach', 'Approach'],
  ['researchImpacts', 'Research impacts'],
  ['description', 'Description'],
]
const TAG_FIELDS = [{ key: 'hardware_facility', label: 'Hardware' }, ...FILTERS]

function formatBytes(bytes) {
  if (bytes == null) return '—'
  const units = ['B', 'kB', 'MB', 'GB', 'TB']
  let i = 0
  let n = bytes
  while (n >= 1000 && i < units.length - 1) {
    n /= 1000
    i += 1
  }
  return `${i === 0 ? n : n.toLocaleString('en-US', { maximumSignificantDigits: 3 })} ${units[i]}`
}

const kindLabel = (kind) => kind.replace(/_/g, ' ')

// PSI writes dates as MM-DD-YYYY; anything else is shown as PSI wrote it.
function psiDate(text) {
  const m = /^(\d{2})-(\d{2})-(\d{4})$/.exec(String(text ?? '').trim())
  return m ? formatDate(`${m[3]}-${m[1]}-${m[2]}`) : text
}
const paragraphs = (text) =>
  String(text)
    .split(/\n\s*\n|\n/)
    .map((p) => p.trim())
    .filter(Boolean)

// The record is fetched directly so a 404 (unknown accession) is told apart from a failure.
function useRecord(accession) {
  const [state, setState] = useState({ status: 'loading', data: null })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    setState({ status: 'loading', data: null })
    fetch(`/api/investigations/${encodeURIComponent(accession)}`, {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
    })
      .then(async (res) => {
        if (res.status === 404) return setState({ status: 'missing', data: null })
        if (!res.ok) {
          // Like getJSON's errors, so LoadError can say the API answered rather than that it did not.
          const error = new Error(`The FLARE API answered ${res.status}.`)
          error.status = res.status
          throw error
        }
        setState({ status: 'ready', data: await res.json() })
      })
      .catch((error) => {
        if (error.name !== 'AbortError') setState({ status: 'error', data: null, error })
      })
    return () => controller.abort()
  }, [accession, attempt])
  return { ...state, retry: () => setAttempt((n) => n + 1) }
}

function Facts({ rec }) {
  const d = rec.derived ?? {}
  const tags = d.tags ?? {}
  const hardwareLinks = String(rec.experimentHardwareLink ?? '')
    .split(',')
    .map((u) => u.trim())
    .filter((u) => u.startsWith('http'))
  const start = rec.investigationStartDate
  const end = rec.investigationEndDate
  const facts = [
    ['Accession', <span className="id">{rec.accession}</span>],
    rec.doi && [
      'DOI',
      <a href={d.doi_url ?? `https://doi.org/${rec.doi}`} target="_blank" rel="noreferrer" className="id">
        {rec.doi}
      </a>,
    ],
    d.page_url && [
      'PSI page',
      <a href={d.page_url} target="_blank" rel="noreferrer">
        Open on NASA PSI
      </a>,
    ],
    (start || end) && ['Dates', `${start ? psiDate(start) : 'not stated'} to ${end ? psiDate(end) : 'not stated'}`],
    rec.flightProgram && ['Flight program', rec.flightProgram],
    rec.experimentHardware && [
      'Hardware',
      <>
        {rec.experimentHardware}
        {hardwareLinks.map((url) => (
          <a key={url} href={url} target="_blank" rel="noreferrer" className="rec-link-line">
            {new URL(url).hostname}
          </a>
        ))}
      </>,
    ],
    rec.managingNasaCenter && ['NASA center', rec.managingNasaCenter],
    rec.licenseName && [
      'Licence',
      rec.licenseLink ? (
        <a href={rec.licenseLink} target="_blank" rel="noreferrer">
          {rec.licenseName}
        </a>
      ) : (
        rec.licenseName
      ),
    ],
  ].filter(Boolean)

  return (
    <aside className="rec-facts" aria-label="Record facts">
      <dl className="rec-dl">
        {facts.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>

      <h2 className="rec-h3">What FLARE holds</h2>
      {d.experimental_tables?.length ? (
        <ul className="rec-tables">
          {d.experimental_tables.map((t) => (
            <li key={t.file_name}>
              <span className="id">{t.file_name}</span>
              <span className="rec-muted">
                {formatNumber(t.rows)} rows, {t.columns} columns
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="rec-muted">No experimental table: catalogue only.</p>
      )}
      <Link className="button-quiet rec-compare" to="/scenario">
        Compare against a scenario
        <ArrowRight size={16} aria-hidden="true" />
      </Link>

      <h2 className="rec-h3">Tags</h2>
      <dl className="rec-dl rec-tags">
        {TAG_FIELDS.map(({ key, label }) => {
          const values = tagValues(rec, key)
          return (
            <div key={key}>
              <dt>{label}</dt>
              <dd>
                {values.length ? values.join(', ') : <span className="rec-muted">Not stated</span>}
                {tags.sources?.[key] && <span className="rec-cite">from {tags.sources[key]}</span>}
              </dd>
            </div>
          )
        })}
      </dl>
      {tags.note && <p className="rec-footnote">{tags.note}</p>}
    </aside>
  )
}

function Files({ rec }) {
  const [params, setParams] = useSearchParams()
  const byKind = rec.derived?.files_by_kind ?? {}
  const kinds = Object.entries(byKind).sort((a, b) => b[1].files - a[1].files)
  // Opens on the readable documents when there are any; "All" is one click away.
  const fallback = byKind.document ? 'document' : 'all'
  const asked = params.get('kind')
  const kind = asked === 'all' || byKind[asked] ? asked : fallback
  const [offset, setOffset] = useState(0)
  useEffect(() => setOffset(0), [kind])
  const query = new URLSearchParams({ accession: rec.accession, limit: String(FILE_PAGE), offset: String(offset) })
  if (kind !== 'all') query.set('kind', kind)
  const files = useApi(`/files?${query}`)
  const total = files.data?.total ?? 0

  const choose = (k) =>
    setParams(
      (prev) => {
        const p = new URLSearchParams(prev)
        p.set('kind', k)
        return p
      },
      { replace: true, preventScrollReset: true },
    )

  return (
    <section className="rec-section" aria-labelledby="files-title">
      <h2 id="files-title" className="ex-h2">
        NASA files <span className="rec-count">{formatNumber(rec.derived?.file_count ?? 0)}</span>
      </h2>
      <p className="ex-note">
        PSI lists these files for {nameOf(rec)}. FLARE links to them and never copies them; a download asks PSI for a
        fresh link, which takes a moment.
      </p>
      <div className="ex-chips rec-kinds" role="group" aria-label="File kind">
        <button type="button" className="ex-chip" aria-pressed={kind === 'all'} onClick={() => choose('all')}>
          All<span className="ex-chip-count">{formatNumber(rec.derived?.file_count ?? 0)}</span>
        </button>
        {kinds.map(([k, v]) => (
          <button key={k} type="button" className="ex-chip" aria-pressed={kind === k} onClick={() => choose(k)}>
            <span className="rec-kind">{kindLabel(k)}</span>
            <span className="ex-chip-count">{formatNumber(v.files)}</span>
          </button>
        ))}
      </div>

      {files.status === 'loading' && <Loading label="Loading the file list…" />}
      {files.status === 'error' && <LoadError what="The file list" retry={files.retry} error={files.error} />}
      {files.status === 'ready' && (
        <>
          <div className="ex-table-wrap">
            <table className="ex-table rec-files">
              <caption className="visually-hidden">Files PSI lists for {nameOf(rec)}</caption>
              <thead>
                <tr>
                  <th scope="col">File</th>
                  <th scope="col">Category</th>
                  <th scope="col" className="num">
                    Size
                  </th>
                </tr>
              </thead>
              <tbody>
                {files.data.items.map((f) => (
                  <tr key={f.file_id}>
                    <th scope="row" data-label="File">
                      <a href={`/api/files/${f.file_id}/download`} className="id rec-file">
                        {f.file_name}
                      </a>
                    </th>
                    <td data-label="Category">
                      {f.category}
                      {f.subcategory && <span className="rec-muted"> / {f.subcategory}</span>}
                    </td>
                    <td data-label="Size" className="num">
                      {formatBytes(f.bytes)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="rec-pager">
            <p>
              {total === 0
                ? 'No files of this kind.'
                : `${formatNumber(offset + 1)}–${formatNumber(Math.min(offset + FILE_PAGE, total))} of ${formatNumber(total)}`}
            </p>
            <button
              type="button"
              className="button-quiet"
              disabled={offset === 0}
              onClick={() => setOffset((o) => Math.max(0, o - FILE_PAGE))}
            >
              Previous
            </button>
            <button
              type="button"
              className="button-quiet"
              disabled={offset + FILE_PAGE >= total}
              onClick={() => setOffset((o) => o + FILE_PAGE)}
            >
              Next
            </button>
          </div>
        </>
      )}
    </section>
  )
}

function People({ rec }) {
  const [all, setAll] = useState(false)
  const pubs = rec.publications ?? []
  const shown = all ? pubs : pubs.slice(0, PUBLICATIONS_SHOWN)
  const contacts = rec.contacts ?? []
  return (
    <div className="rec-people">
      <section className="rec-section" aria-labelledby="pubs-title">
        <h2 id="pubs-title" className="ex-h2">
          Publications <span className="rec-count">{pubs.length}</span>
        </h2>
        {pubs.length === 0 ? (
          <p className="ex-note">The PSI record lists no publications.</p>
        ) : (
          <>
            <ol className="rec-list">
              {shown.map((p, i) => (
                <li key={`${p.title}-${i}`}>
                  <span className="rec-pub-title">{p.title}</span>
                  <span className="rec-muted">
                    {p.authorList || 'Authors not listed'}
                    {p.status ? `, ${p.status}` : ''}
                  </span>
                  {p.doi && (
                    <a href={`https://doi.org/${p.doi}`} target="_blank" rel="noreferrer" className="id">
                      doi:{p.doi}
                    </a>
                  )}
                </li>
              ))}
            </ol>
            {pubs.length > shown.length && (
              <button type="button" className="button-quiet" onClick={() => setAll(true)}>
                Show all {pubs.length}
              </button>
            )}
          </>
        )}
      </section>
      <section className="rec-section" aria-labelledby="people-title">
        <h2 id="people-title" className="ex-h2">
          People <span className="rec-count">{contacts.length}</span>
        </h2>
        {contacts.length === 0 ? (
          <p className="ex-note">The PSI record lists no contacts.</p>
        ) : (
          <ul className="rec-list">
            {contacts.map((c, i) => (
              <li key={`${c.lastName}-${i}`}>
                <span className="rec-pub-title">
                  {[c.firstName, c.midInitials, c.lastName].filter(Boolean).join(' ')}
                </span>
                <span className="rec-muted">
                  {[...(c.roles ?? []), c.affiliation].filter(Boolean).join(', ')}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}

// The stored AI summary (#28). An investigation without one shows nothing in its place.
function StoredSummary({ accession }) {
  const summary = useApi(`/assistant/summaries/${encodeURIComponent(accession)}`)
  if (summary.status === 'error' && summary.error?.status === 404) return null
  return (
    <div className="rec-summary">
      {summary.status === 'loading' && <Loading label="Loading the AI summary…" />}
      {summary.status === 'error' && <LoadError what="The AI summary" retry={summary.retry} error={summary.error} />}
      {summary.status === 'ready' && <AiSummary id="summary" title="AI summary" data={summary.data} />}
    </div>
  )
}

export default function ExplorerInvestigation() {
  const { accession } = useParams()
  const rec = useRecord(accession)

  return (
    <div className="rec-page">
      <p className="rec-back">
        <Link to="/explorer">
          <ArrowLeft size={16} aria-hidden="true" />
          All investigations
        </Link>
      </p>

      {rec.status === 'loading' && <Loading label="Loading the PSI record…" />}
      {rec.status === 'error' && <LoadError what="This PSI record" retry={rec.retry} error={rec.error} />}
      {rec.status === 'missing' && (
        <div className="ex-message">
          <p>
            No investigation <span className="id">{accession}</span> is in FLARE's catalogue of NASA PSI combustion
            investigations.
          </p>
        </div>
      )}
      {rec.status === 'ready' && (
        <>
          <header className="rec-head">
            <h1>{nameOf(rec.data)}</h1>
            <p className="ex-lede">{rec.data.title}</p>
          </header>
          <div className="rec-body">
            <Facts rec={rec.data} />
            <div className="rec-text">
              <StoredSummary accession={rec.data.accession} />
              <h2 className="ex-h2">From the PSI record</h2>
              <p className="ex-note">NASA's own text for this investigation, unchanged.</p>
              {TEXT_FIELDS.filter(([field]) => rec.data[field]?.trim()).map(([field, label]) => (
                <section key={field} className="rec-field">
                  <h3>{label}</h3>
                  {paragraphs(rec.data[field]).map((p, i) => (
                    <p key={i}>{p}</p>
                  ))}
                </section>
              ))}
            </div>
          </div>
          <Files rec={rec.data} />
          <div className="rec-section">
            <ExplorerSearch accession={rec.data.accession} />
          </div>
          <People rec={rec.data} />
        </>
      )}
    </div>
  )
}
