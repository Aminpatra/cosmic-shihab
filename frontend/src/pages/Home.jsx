import { Link } from 'react-router'
import { ArrowRight } from 'lucide-react'
import { useApi } from '../api.js'
import { formatDate, formatNumber, formatTB, summarise } from '../catalogue.js'
import { FLEX_EXAMPLE } from '../content/flexExample.js'
import ConditionLanes from '../components/ConditionLanes.jsx'
import CatalogueLane from '../components/CatalogueLane.jsx'
import { LoadError, Loading } from '../components/ApiState.jsx'
import './Home.css'

export default function Home() {
  const catalogue = useApi('/investigations')
  const facts = catalogue.status === 'ready' ? summarise(catalogue.data) : null

  return (
    <>
      <title>FLARE · Fire Learning, Analysis &amp; Research Explorer</title>

      <section className="home-hero">
        <div className="home-intro">
          <h1>Which NASA fire experiments match your mission?</h1>
          <p className="home-lede">
            FLARE ranks NASA's 24 microgravity combustion investigations against the scenario you describe, and shows
            why: what matches, what differs, and what was never recorded.
          </p>
          <div className="home-actions">
            <Link className="button" to="/scenario">
              Start from a scenario
              <ArrowRight size={18} strokeWidth={2.5} aria-hidden="true" />
            </Link>
            <Link className="home-browse" to="/explorer">
              Browse all 24 investigations
            </Link>
          </div>
          <p className="home-note">
            A relevance score says how closely an investigation's tested conditions match yours. It is not a safety
            assessment.
          </p>
        </div>

        <div className="home-record">
          <ConditionLanes
            caption="Example: FLEX (PSI-69) against a spacecraft cabin"
            summary="3 match, 1 differs, 1 not recorded"
            theirsLabel={`FLEX tested range, ${FLEX_EXAMPLE.runs} runs`}
            lanes={FLEX_EXAMPLE.lanes}
            animate
          />
          <p className="provenance">
            Source: <span className="id">{FLEX_EXAMPLE.accession}</span> experimental table, {FLEX_EXAMPLE.runs} runs,{' '}
            <a href={`https://doi.org/${FLEX_EXAMPLE.doi}`} target="_blank" rel="noreferrer">
              doi:{FLEX_EXAMPLE.doi}
            </a>
            , retrieved {FLEX_EXAMPLE.retrieved}. One run records 0 mmHg and is left out of the pressure range. The cabin
            values are an example, not NASA data.
          </p>
        </div>
      </section>

      <section className="home-catalogue" aria-labelledby="catalogue-title">
        <div className="home-section-head">
          <h2 id="catalogue-title">What NASA PSI holds, and how far FLARE can use it</h2>
          {facts && (
            <p>
              PSI lists {formatNumber(facts.files)} files ({formatTB(facts.bytes)}) for these {facts.count}{' '}
              investigations. FLARE ranks only on their small experimental tables; everything else is linked back to
              NASA, never copied.
            </p>
          )}
        </div>

        {catalogue.status === 'loading' && <Loading label="Loading the PSI catalogue…" />}
        {catalogue.status === 'error' && <LoadError what="The PSI catalogue" retry={catalogue.retry} />}
        {catalogue.status === 'ready' && <CatalogueLane investigations={catalogue.data} />}

        {facts && (
          <p className="provenance">
            Source: NASA Physical Sciences Informatics, retrieved {formatDate(facts.retrieved)}. How the tiers were set:{' '}
            <Link to="/sources#reading">Sources and methodology</Link>.
          </p>
        )}
      </section>

      <section className="home-close" aria-labelledby="close-title">
        <h2 id="close-title">Every number shows where it came from</h2>
        <p>
          Each investigation links to its NASA record and DOI. Read how FLARE gathered the data, what it assumes, and what
          it cannot tell you.
        </p>
        <Link className="home-close-link" to="/sources">
          Sources and methodology
          <ArrowRight size={18} aria-hidden="true" />
        </Link>
      </section>
    </>
  )
}
