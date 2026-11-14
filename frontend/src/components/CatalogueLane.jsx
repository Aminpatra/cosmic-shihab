import { useState } from 'react'
import { ExternalLink } from 'lucide-react'
import { TIERS, nameOf, runsOf, tierOf } from '../catalogue.js'
import './CatalogueLane.css'

// The 24 investigations as one lane of cells, grouped by how far FLARE can use their data.
// Pointing at an investigation in the lists lights its cell.
export default function CatalogueLane({ investigations }) {
  const [hot, setHot] = useState(null)

  const groups = TIERS.map((tier) => {
    const items = investigations
      .filter((inv) => tierOf(inv) === tier.id)
      .sort((a, b) => runsOf(b) - runsOf(a) || nameOf(a).localeCompare(nameOf(b)))
    const runs = items.reduce((sum, inv) => sum + runsOf(inv), 0)
    return { ...tier, items, runs }
  }).filter((group) => group.items.length > 0)

  return (
    <div className="catalogue">
      <div className="catalogue-track" aria-hidden="true">
        {groups.map((group) => (
          <div key={group.id} className="catalogue-segment">
            {group.items.map((inv) => (
              <span
                key={inv.accession}
                className={`cell cell-${group.id}`}
                data-hot={hot === inv.accession || undefined}
              />
            ))}
          </div>
        ))}
      </div>

      <div className="catalogue-groups">
        {groups.map((group) => (
          <section key={group.id} className="catalogue-group" aria-labelledby={`tier-${group.id}`}>
            <h3 id={`tier-${group.id}`}>
              <span className={`group-key cell-${group.id}`} aria-hidden="true" />
              {group.label}
              <span className="group-count">{group.items.length}</span>
            </h3>
            <p className="group-note">
              {group.note}
              {group.runs > 0 && ` ${group.runs.toLocaleString('en-US')} runs in all.`}
            </p>
            <ul>
              {group.items.map((inv) => {
                const runs = runsOf(inv)
                return (
                  <li key={inv.accession}>
                    <a
                      href={inv.derived?.page_url?.trim() || `https://psi.nasa.gov/physci/repo/data/investigations/${inv.accession}`}
                      target="_blank"
                      rel="noreferrer"
                      onMouseEnter={() => setHot(inv.accession)}
                      onMouseLeave={() => setHot(null)}
                      onFocus={() => setHot(inv.accession)}
                      onBlur={() => setHot(null)}
                    >
                      <span className="inv-name">{nameOf(inv)}</span>
                      <span className="inv-runs">{runs > 0 ? `${runs.toLocaleString('en-US')} runs` : 'no table'}</span>
                      {!inv.investigationAcronym?.trim() && <span className="inv-title">{inv.title}</span>}
                      <ExternalLink className="inv-out" size={14} aria-hidden="true" />
                      <span className="visually-hidden"> (NASA PSI record, opens in a new tab)</span>
                    </a>
                  </li>
                )
              })}
            </ul>
          </section>
        ))}
      </div>
    </div>
  )
}
