import { Link } from 'react-router'
import { Construction } from 'lucide-react'
import './InProgress.css'

const ISSUES = 'https://github.com/gheathwahab/cosmic-shihab/issues/'

// The slot a teammate's page drops into. It says plainly that nothing here is built yet.
export default function InProgress({ page }) {
  return (
    <>
      <title>{`${page.title} · FLARE`}</title>
      <section className="slot">
        <h1>{page.title}</h1>
        <p className="slot-lede">{page.summary}</p>
        <div className="slot-status">
          <span className="slot-track" aria-hidden="true">
            <span>Not built yet</span>
          </span>
          <p>
            <Construction className="slot-icon" size={16} strokeWidth={2} aria-hidden="true" />
            This page is being built
            {page.issue && (
              <>
                {' ('}
                <a href={`${ISSUES}${page.issue}`} target="_blank" rel="noreferrer">
                  issue #{page.issue}
                </a>
                {')'}
              </>
            )}
            . Until it lands it shows no data and no results.
          </p>
        </div>
        <p className="slot-next">
          Meanwhile, the <Link to="/">Home page</Link> shows a real investigation against an example scenario, and{' '}
          <Link to="/sources">Sources and methodology</Link> lists every investigation.
        </p>
      </section>
    </>
  )
}
