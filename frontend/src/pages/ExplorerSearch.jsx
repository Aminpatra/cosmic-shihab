import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { ExternalLink, Search } from 'lucide-react'
import { getJSON } from '../api.js'
import { nameOf } from '../catalogue.js'
import { LoadError, Loading } from '../components/ApiState.jsx'
import { splitSnippet } from './ExplorerFilters.js'

const PAGE = 10

function searchPath(q, offset, accession) {
  const p = new URLSearchParams({ q, limit: String(PAGE), offset: String(offset) })
  if (accession) p.set('accession', accession)
  return `/search?${p}`
}

// Search inside PSI's documents (GET /api/search, #18). The query lives in the link as `q`.
export default function ExplorerSearch({ accession }) {
  const [params, setParams] = useSearchParams()
  const q = (params.get('q') ?? '').trim()
  const [draft, setDraft] = useState(q)
  // moreError: the last "Show more" failed; the passages already loaded stay on screen.
  const [state, setState] = useState({ status: 'idle', items: [], total: 0, error: null, moreError: null })
  const [attempt, setAttempt] = useState(0)
  const moreRequest = useRef(null)

  useEffect(() => setDraft(q), [q])

  useEffect(() => {
    if (!q) {
      setState({ status: 'idle', items: [], total: 0, error: null, moreError: null })
      return
    }
    const controller = new AbortController()
    setState({ status: 'loading', items: [], total: 0, error: null, moreError: null })
    getJSON(searchPath(q, 0, accession), { signal: controller.signal })
      .then((data) => setState({ status: 'ready', items: data.items, total: data.total, error: null, moreError: null }))
      .catch((error) => {
        if (error.name !== 'AbortError') setState({ status: 'error', items: [], total: 0, error, moreError: null })
      })
    return () => {
      controller.abort()
      // A "Show more" still on its way belongs to this query: it must not land in the next one.
      moreRequest.current?.abort()
    }
  }, [q, accession, attempt])

  const more = () => {
    const controller = new AbortController()
    moreRequest.current = controller
    setState((s) => ({ ...s, status: 'more', moreError: null }))
    getJSON(searchPath(q, state.items.length, accession), { signal: controller.signal })
      .then((data) => setState((s) => ({ ...s, status: 'ready', items: [...s.items, ...data.items] })))
      .catch((error) => {
        if (error.name !== 'AbortError') setState((s) => ({ ...s, status: 'ready', moreError: error }))
      })
  }

  const submit = (e) => {
    e.preventDefault()
    setParams(
      (prev) => {
        const p = new URLSearchParams(prev)
        if (draft.trim()) p.set('q', draft.trim())
        else p.delete('q')
        return p
      },
      { preventScrollReset: true },
    )
  }

  // The status code itself: the message also holds the query, so a search for "503" would match.
  const status = state.error?.status
  return (
    <section className="ex-search" aria-labelledby="search-title">
      <h2 id="search-title" className="ex-h2">
        {accession ? 'Search its documents' : "Search inside NASA's documents"}
      </h2>
      <form className="ex-search-form" role="search" onSubmit={submit}>
        <label className="visually-hidden" htmlFor="ex-q">
          Words to find in PSI documents
        </label>
        <input
          id="ex-q"
          className="ex-search-input"
          type="search"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="e.g. extinction oxygen"
          autoComplete="off"
        />
        <button type="submit" className="button">
          <Search size={18} aria-hidden="true" />
          Search
        </button>
      </form>
      <p className="ex-note">
        Finds passages in the PDFs, slides and Word files PSI publishes{accession ? ' for this investigation' : ''}.
        A passage matches when it holds any of your words; the closest come first.
      </p>

      {state.status === 'loading' && <Loading label="Searching NASA's documents…" />}
      {state.status === 'error' &&
        (status === 503 ? (
          <p className="ex-message">Document search is not available: the search index has not been built.</p>
        ) : status === 422 ? (
          <p className="ex-message">Enter at least one word to search for.</p>
        ) : (
          <LoadError what="Document search" retry={() => setAttempt((n) => n + 1)} error={state.error} />
        ))}
      {(state.status === 'ready' || state.status === 'more') && (
        <div className="ex-results">
          <p className="ex-count" aria-live="polite">
            {state.total === 0
              ? `No passage holds any of “${q}”.`
              : `${state.total.toLocaleString('en-US')} ${state.total === 1 ? 'passage' : 'passages'} for “${q}”. “Open file” fetches NASA's copy, which takes a moment.`}
          </p>
          <ol className="hits">
            {state.items.map((hit) => (
              <li key={`${hit.file_id}-${hit.page}-${hit.snippet}`} className="hit">
                <p className="hit-snippet">
                  {splitSnippet(hit.snippet).map((part, i) => (part.match ? <mark key={i}>{part.text}</mark> : part.text))}
                </p>
                <p className="hit-meta">
                  {!accession && (
                    <>
                      <Link to={`/explorer/${hit.accession}`}>{nameOf(hit)}</Link>{' '}
                    </>
                  )}
                  <span className="id hit-file">{hit.file_name}</span>
                  {hit.page != null && <span>page {hit.page}</span>}
                  <a href={`/api/files/${hit.file_id}/download`} className="hit-open">
                    Open file
                    <ExternalLink size={14} aria-hidden="true" />
                  </a>
                </p>
              </li>
            ))}
          </ol>
          {state.items.length < state.total && (
            <button type="button" className="button-quiet" onClick={more} disabled={state.status === 'more'}>
              {state.status === 'more' ? 'Loading…' : `Show ${Math.min(PAGE, state.total - state.items.length)} more`}
            </button>
          )}
          {state.moreError && (
            <p className="ex-message" role="alert">
              The next passages could not load:{' '}
              {state.moreError.status
                ? `the FLARE API answered with an error (${state.moreError.status})`
                : 'the FLARE API did not answer'}
              . The passages above are unchanged; Show more tries again.
            </p>
          )}
        </div>
      )}
    </section>
  )
}
