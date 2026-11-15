import { Fragment, useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router'
import { ArrowRight, ExternalLink, FileText, Info, RotateCw, TriangleAlert, X } from 'lucide-react'
import { getJSON, useApi } from '../api.js'
import { TIERS, countOf, nameOf, runsOf, tierOf } from '../catalogue.js'
import { LoadError, Loading } from '../components/ApiState.jsx'
import './Assistant.css'

const MAX_SCOPE = 4 // the API answers about at most four investigations at once

const EXAMPLES = [
  'Which gases did FLEX test as fire suppressants?',
  'How do BASS and BASS-II differ in the materials they burned?',
  'What does SAME-R say about smoke detectors in microgravity?',
]

async function ask(question, accessions, signal) {
  const res = await fetch('/api/assistant/ask', {
    method: 'POST',
    signal,
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ question, accessions }),
  })
  if (!res.ok) {
    const error = new Error(`The FLARE API answered ${res.status}.`)
    error.status = res.status
    // 429: this address asked too often (#81); the API says how long to wait.
    if (res.status === 429) error.detail = (await res.json().catch(() => null))?.detail
    throw error
  }
  return res.json()
}

// "[[word]]" marks a matched word in a search snippet; the text itself is plain, never HTML.
function Marked({ text }) {
  return text.split(/(\[\[.*?\]\])/).map((part, i) =>
    part.startsWith('[[') ? <mark key={i}>{part.slice(2, -2)}</mark> : <Fragment key={i}>{part}</Fragment>,
  )
}

// The catalogue lane as a scope control: each cell is a toggle for one investigation.
function ScopeLane({ investigations, chosen, onToggle, onPoint }) {
  const groups = TIERS.map((tier) => ({
    ...tier,
    items: investigations
      .filter((inv) => tierOf(inv) === tier.id)
      .sort((a, b) => runsOf(b) - runsOf(a) || nameOf(a).localeCompare(nameOf(b))),
  })).filter((group) => group.items.length > 0)
  const full = chosen.length >= MAX_SCOPE

  return (
    <>
    <div className="scope-track" role="group" aria-label="Investigations to ask about">
      {groups.map((group) => (
        <div key={group.id} className="scope-segment">
          {group.items.map((inv) => {
            const on = chosen.includes(inv.accession)
            return (
              <button
                key={inv.accession}
                type="button"
                className={`scope-cell cell-${group.id}`}
                aria-pressed={on}
                disabled={full && !on}
                title={`${nameOf(inv)} · ${inv.accession}`}
                onClick={() => onToggle(inv.accession)}
                onMouseEnter={() => onPoint(inv)}
                onMouseLeave={() => onPoint(null)}
                onFocus={() => onPoint(inv)}
                onBlur={() => onPoint(null)}
              >
                <span className="visually-hidden">
                  {nameOf(inv)}, {inv.accession}
                </span>
              </button>
            )
          })}
        </div>
      ))}
    </div>
    <div className="scope-tiers" aria-hidden="true">
      {groups.map((group) => (
        <span key={group.id}>{group.label}</span>
      ))}
    </div>
    </>
  )
}

function Scope({ catalogue, chosen, setChosen }) {
  const [pointed, setPointed] = useState(null)
  if (catalogue.status === 'loading') return <Loading label="Loading the investigations…" />
  if (catalogue.status === 'error') return <LoadError what="The investigation list" retry={catalogue.retry} error={catalogue.error} />

  const byId = Object.fromEntries(catalogue.data.map((inv) => [inv.accession, inv]))
  const toggle = (accession) =>
    setChosen((now) =>
      now.includes(accession)
        ? now.filter((a) => a !== accession)
        : now.length < MAX_SCOPE
          ? [...now, accession]
          : now,
    )
  const options = [...catalogue.data].sort((a, b) => nameOf(a).localeCompare(nameOf(b)))

  return (
    <div className="scope">
      <p className="scope-readout" aria-hidden="true">
        {pointed ? (
          <>
            <strong>{nameOf(pointed)}</strong> <span className="id">{pointed.accession}</span>
            {pointed.investigationAcronym?.trim() && <span className="scope-readout-title">{pointed.title}</span>}
          </>
        ) : (
          <span className="scope-readout-title">Point at a cell to see its investigation.</span>
        )}
        <span className="scope-count">
          {chosen.length} of {MAX_SCOPE} chosen
        </span>
      </p>
      <ScopeLane investigations={catalogue.data} chosen={chosen} onToggle={toggle} onPoint={setPointed} />
      <div className="scope-controls">
        <label className="scope-add">
          <span>Add an investigation</span>
          <select
            value=""
            disabled={chosen.length >= MAX_SCOPE}
            onChange={(event) => event.target.value && toggle(event.target.value)}
          >
            <option value="">Choose…</option>
            {options.map((inv) => (
              <option key={inv.accession} value={inv.accession} disabled={chosen.includes(inv.accession)}>
                {nameOf(inv)} ({inv.accession})
              </option>
            ))}
          </select>
        </label>
        {chosen.length > 0 ? (
          <ul className="scope-chips" aria-label="Chosen investigations">
            {chosen.map((accession) => (
              <li key={accession}>
                <span>{nameOf(byId[accession])}</span>
                <button
                  type="button"
                  onClick={() => toggle(accession)}
                  aria-label={`Remove ${nameOf(byId[accession])} from the question`}
                >
                  <X size={14} aria-hidden="true" />
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="scope-note">
            None chosen: FLARE uses the investigations your question names, or searches all{' '}
            {countOf(catalogue.data.length, 'investigation')}.
          </p>
        )}
      </div>
      {chosen.length >= MAX_SCOPE && <p className="scope-note">Four is the most one question can cover.</p>}
    </div>
  )
}

function SourceList({ sources, quotes, pointed }) {
  return (
    <ol className="answer-sources">
      {sources.map((source, i) => {
        const cited = quotes[source.id] ?? []
        const where = source.kind === 'record' ? 'PSI record' : source.page ? `Document, page ${source.page}` : 'Document'
        return (
          <li key={source.id} id={`src-${i + 1}`} className={pointed === i + 1 ? 'source is-pointed' : 'source'} tabIndex={-1}>
            <span className="source-n">{i + 1}</span>
            <div className="source-body">
              <p className="source-head">
                <strong>{source.label}</strong>
                <span className="source-kind">{where}</span>
                <a href={source.url} target="_blank" rel="noreferrer" className="source-link">
                  <span className="id">{source.kind === 'record' ? source.accession : source.file_name}</span>
                  <ExternalLink size={14} aria-hidden="true" />
                  <span className="visually-hidden">
                    {source.kind === 'record' ? ' (NASA PSI page' : ' (download from NASA PSI'}, opens in a new tab)
                  </span>
                </a>
              </p>
              {cited.length > 0 ? (
                <ul className="source-quotes" aria-label="Words the answer cites">
                  {cited.map((quote, j) => (
                    <li key={j}>“{quote.trim()}”</li>
                  ))}
                </ul>
              ) : source.snippet ? (
                <p className="source-snippet">
                  <Marked text={source.snippet} />
                </p>
              ) : (
                <p className="source-snippet">{source.title.replace(/^PSI record [^:]+: /, '')}</p>
              )}
              <details className="source-full">
                <summary>
                  <FileText size={14} aria-hidden="true" />
                  {source.kind === 'record' ? 'Record text FLARE sent' : 'Whole passage'}
                </summary>
                <p>{source.text}</p>
              </details>
            </div>
          </li>
        )
      })}
    </ol>
  )
}

// Paragraphs from the answer's blocks. A block may end one paragraph and start the next.
function paragraphs(blocks) {
  const out = [[]]
  blocks.forEach((block, b) => {
    block.text.split(/\n{2,}/).forEach((piece, k) => {
      if (k > 0) out.push([])
      if (piece) out[out.length - 1].push({ ...block, text: piece, key: `${b}-${k}` })
    })
  })
  // Punctuation that opens an uncited piece belongs to the cited sentence before it, so it
  // goes before that sentence's citation number rather than after it.
  for (const para of out)
    for (let i = 1; i < para.length; i++) {
      const lead = para[i].text.match(/^[.,;:!?)]+/)
      if (lead && para[i - 1].kind === 'source') {
        para[i - 1] = { ...para[i - 1], text: para[i - 1].text + lead[0] }
        para[i] = { ...para[i], text: para[i].text.slice(lead[0].length) }
      }
    }
  return out.map((p) => p.filter((piece) => piece.text)).filter((p) => p.length > 0)
}

function Result({ result, retry }) {
  const index = useMemo(() => Object.fromEntries(result.sources.map((s, i) => [s.id, i + 1])), [result])
  const quotes = useMemo(() => {
    const q = {}
    for (const block of result.blocks)
      for (const c of block.citations) (q[c.source_id] ??= []).includes(c.cited_text) || q[c.source_id].push(c.cited_text)
    return q
  }, [result])
  const [pointed, setPointed] = useState(null)
  useEffect(() => setPointed(null), [result])
  // A citation brings its source into view here, not through the #hash: the router's scroll
  // restoration would put a hash jump straight back (#101, as AiSummary does since #67).
  const goTo = (event, n) => {
    event.preventDefault()
    const item = document.getElementById(`src-${n}`)
    if (!item) return
    item.scrollIntoView({ block: 'start' })
    item.focus({ preventScroll: true })
    setPointed(n)
  }

  if (result.mode === 'retrieval_only') {
    return (
      <>
        <div className="answer-notice" role="note">
          <Info size={18} aria-hidden="true" />
          <p>{result.reason}</p>
        </div>
        {result.sources.length > 0 ? (
          <>
            <h2 className="answer-h">
              {result.sources.every((s) => s.kind === 'record')
                ? 'Records of the investigations asked about'
                : 'Matching NASA sources'}{' '}
              <span className="answer-count">{result.sources.length}</span>
            </h2>
            <SourceList sources={result.sources} quotes={{}} />
          </>
        ) : (
          <p className="answer-empty">
            Try other words, or choose investigations above. FLARE answers only from PSI records and the documents it
            has indexed.
          </p>
        )}
      </>
    )
  }

  return (
    <>
      <div className="answer-meta">
        <h2 className="answer-h">Answer</h2>
        <p>
          AI-generated by <span className="id">{result.model}</span> from the {result.sources.length} sources below.
        </p>
      </div>
      <p className="answer-legend">
        <span className="legend-source">White underlined text</span> is stated in a cited NASA source; the number after
        it opens the source. <span className="legend-own">Lighter text without an underline</span> is the assistant's own
        explanation.
      </p>
      <div className="answer-text">
        {paragraphs(result.blocks).map((para, p) => (
          <p key={p}>
            {para.map((piece) =>
              piece.kind === 'source' ? (
                <Fragment key={piece.key}>
                  <span className="said">{piece.text}</span>
                  {[...new Set(piece.citations.map((c) => index[c.source_id]))].map((n) => (
                    <a key={n} href={`#src-${n}`} className="cite" aria-label={`Source ${n}`} onClick={(event) => goTo(event, n)}>
                      {n}
                    </a>
                  ))}
                </Fragment>
              ) : (
                <span key={piece.key} className="own">
                  {piece.text}
                </span>
              ),
            )}
          </p>
        ))}
      </div>
      <button type="button" className="button-quiet answer-again" onClick={retry}>
        <RotateCw size={16} aria-hidden="true" />
        Ask again
      </button>
      <h2 className="answer-h">
        Sources <span className="answer-count">{result.sources.length}</span>
      </h2>
      <SourceList sources={result.sources} quotes={quotes} pointed={pointed} />
    </>
  )
}

export default function Assistant() {
  const catalogue = useApi('/investigations')
  const [question, setQuestion] = useState('')
  const [chosen, setChosen] = useState([])
  const [state, setState] = useState({ status: 'idle' })
  const [mode, setMode] = useState(null)
  const pending = useRef(null)

  useEffect(() => {
    const controller = new AbortController()
    getJSON('/assistant/status', { signal: controller.signal })
      .then((s) => setMode(s.mode))
      .catch(() => {})
    return () => controller.abort()
  }, [])

  const submit = (text = question) => {
    const q = text.trim()
    if (q.length < 3) return
    pending.current?.abort()
    const controller = new AbortController()
    pending.current = controller
    setState({ status: 'asking', question: q })
    ask(q, chosen, controller.signal)
      .then((result) => setState({ status: 'ready', result }))
      .catch((error) => error.name !== 'AbortError' && setState({ status: 'error', question: q, error }))
  }

  return (
    <>
      <title>AI Research Assistant · FLARE</title>
      <section className="assistant">
        <header className="assistant-head">
          <h1>AI Research Assistant</h1>
          <p className="assistant-lede">
            Ask about the{' '}
            {catalogue.status === 'ready' && catalogue.data.length > 0
              ? countOf(catalogue.data.length, 'NASA combustion investigation')
              : 'NASA combustion investigations'}
            . Answers come only from their PSI records and documents,
            cite each source, and say so when no source answers.
          </p>
        </header>

        <form
          className="ask"
          onSubmit={(event) => {
            event.preventDefault()
            submit()
          }}
        >
          <label htmlFor="question" className="ask-label">
            Your question
          </label>
          <div className="ask-row">
            <textarea
              id="question"
              rows={2}
              maxLength={1000}
              value={question}
              placeholder="For example: which gases did FLEX test as fire suppressants?"
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault()
                  // One question at a time: a held or repeated Enter must not start another request.
                  if (event.repeat || state.status === 'asking') return
                  submit()
                }
              }}
            />
            <button type="submit" className="button" disabled={question.trim().length < 3 || state.status === 'asking'}>
              Ask
              <ArrowRight size={18} aria-hidden="true" />
            </button>
          </div>
          {mode === 'retrieval_only' && state.status !== 'ready' && (
            <p className="ask-mode">
              <Info size={16} aria-hidden="true" />
              No AI key is configured here, so answers show the matching NASA sources without generated text.
            </p>
          )}
        </form>

        <div className="scope-block">
          <h2 className="scope-h">Scope</h2>
          <Scope catalogue={catalogue} chosen={chosen} setChosen={setChosen} />
        </div>
      </section>

      <section className="answer" aria-live="polite" aria-busy={state.status === 'asking'}>
        {state.status === 'idle' && (
          <div className="answer-idle">
            <p>Questions to start from:</p>
            <ul>
              {EXAMPLES.map((example) => (
                <li key={example}>
                  <button
                    type="button"
                    className="example"
                    onClick={() => {
                      setQuestion(example)
                      submit(example)
                    }}
                  >
                    {example}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
        {state.status === 'asking' && <Loading label="Reading the NASA sources…" />}
        {state.status === 'error' && (
          <div className="api-error" role="alert">
            <TriangleAlert size={20} aria-hidden="true" />
            <div>
              {state.error?.status === 429 ? (
                <p>
                  <strong>Too many questions from this address.</strong>{' '}
                  {state.error.detail ?? 'Wait a minute, then try again.'}
                </p>
              ) : (
                <p>
                  <strong>The question could not be answered.</strong> The FLARE API did not respond, so no answer is
                  shown rather than a guess.
                </p>
              )}
              <button type="button" className="button-quiet" onClick={() => submit(state.question)}>
                <RotateCw size={16} aria-hidden="true" />
                Try again
              </button>
            </div>
          </div>
        )}
        {state.status === 'ready' && <Result result={state.result} retry={() => submit(state.result.question)} />}

        <p className="provenance">
          The assistant reads FLARE's copies of NASA PSI records and documents and never changes the{' '}
          <Link to="/methodology#ranking">relevance ranking</Link>. It reports what the investigations recorded; it is not a
          fire-safety assessment.
        </p>
      </section>
    </>
  )
}
