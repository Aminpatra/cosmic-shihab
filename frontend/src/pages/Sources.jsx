import { Link } from 'react-router'
import { useApi } from '../api.js'
import {
  TIERS,
  byAccession,
  formatDate,
  formatNumber,
  formatTB,
  nameOf,
  runsOf,
  summarise,
  tierOf,
} from '../catalogue.js'
import { LoadError, Loading } from '../components/ApiState.jsx'
import logo from '../assets/cosmic-shihab-logo.jpg'
import './Sources.css'

const SECTIONS = [
  ['data', 'NASA data'],
  ['team', 'Team and credits'],
  ['references', 'References'],
]

// In the order PRODUCT.md gives.
const TEAM = [
  'Amin Mohamed Amin',
  'Gheath Wahab',
  'Mohammed Al-julandani',
  'Samin Rezaei',
  'Rahaf Abubaker Mustafa Mubarak',
  'Ruayma Khair Mohammed Albalushi',
]

function InvestigationTable({ investigations }) {
  const rows = [...investigations].sort(byAccession)
  const tierLabel = Object.fromEntries(TIERS.map((t) => [t.id, t.label]))
  return (
    <div className="inv-table-wrap">
      <table className="inv-table">
        <caption className="visually-hidden">The 24 NASA PSI combustion investigations FLARE uses</caption>
        <thead>
          <tr>
            <th scope="col">Accession</th>
            <th scope="col">Investigation</th>
            <th scope="col">Flown on</th>
            <th scope="col" className="num">
              Runs
            </th>
            <th scope="col">FLARE use</th>
            <th scope="col">Licence</th>
            <th scope="col">DOI</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((inv) => {
            const runs = runsOf(inv)
            const flown = inv.flightProgram?.trim()
            return (
              <tr key={inv.accession}>
                <td data-label="Accession">
                  <a className="id" href={inv.derived?.page_url} target="_blank" rel="noreferrer">
                    {inv.accession}
                  </a>
                </td>
                <th scope="row" data-label="Investigation">
                  {nameOf(inv) !== inv.accession && <span className="inv-acronym">{nameOf(inv)}</span>}
                  <span className="inv-full">{inv.title}</span>
                </th>
                <td data-label="Flown on">
                  {!flown ? (
                    <span className="absent">Not stated</span>
                  ) : flown === 'Not Applicable' ? (
                    <span className="absent">Not applicable</span>
                  ) : (
                    flown
                  )}
                </td>
                <td data-label="Runs" className="num">
                  {runs > 0 ? (
                    <>
                      {formatNumber(runs)}
                      <span className="runs-unit"> runs</span>
                    </>
                  ) : (
                    <span className="absent">No table</span>
                  )}
                </td>
                <td data-label="FLARE use">{tierLabel[tierOf(inv)]}</td>
                <td data-label="Licence">
                  {inv.licenseIdentifier?.trim() || <span className="absent">Not stated</span>}
                </td>
                <td data-label="DOI">
                  <a className="id" href={inv.derived?.doi_url ?? `https://doi.org/${inv.doi}`} target="_blank" rel="noreferrer">
                    {inv.doi}
                  </a>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default function Sources() {
  const catalogue = useApi('/investigations')
  const facts = catalogue.status === 'ready' ? summarise(catalogue.data) : null

  return (
    <>
      <title>Sources · FLARE</title>
      <div className="sources">
        <header className="sources-head">
          <h1>Sources</h1>
          <p className="sources-lede">
            The NASA investigations FLARE uses, who built it, and every outside resource it relies on. How the data is
            read, ranked and limited is on the <Link to="/methodology">Methodology</Link> page.
          </p>
        </header>

        <div className="sources-body">
          <nav className="toc" aria-label="On this page">
            <ul>
              {SECTIONS.map(([id, label]) => (
                <li key={id}>
                  <a href={`#${id}`}>{label}</a>
                </li>
              ))}
            </ul>
          </nav>

          <div className="sources-content">
            <section id="data" aria-labelledby="data-title">
              <h2 id="data-title">NASA data</h2>
              <p>
                Every investigation comes from NASA's{' '}
                <a href="https://psi.nasa.gov" target="_blank" rel="noreferrer">
                  Physical Sciences Informatics
                </a>{' '}
                (PSI) repository, research area Combustion Science.
                {facts && (
                  <>
                    {' '}
                    It lists {facts.count} investigations and {formatNumber(facts.files)} files ({formatTB(facts.bytes)}),
                    retrieved on {formatDate(facts.retrieved)}. Cite each one by its DOI.
                  </>
                )}
              </p>
              {catalogue.status === 'loading' && <Loading label="Loading the 24 investigations…" />}
              {catalogue.status === 'error' && <LoadError what="The investigation list" retry={catalogue.retry} />}
              {catalogue.status === 'ready' && <InvestigationTable investigations={catalogue.data} />}
              {catalogue.status === 'ready' && (
                <p className="sources-note">
                  How the three groups in the FLARE use column were set:{' '}
                  <Link to="/methodology#tables">Methodology</Link>.
                </p>
              )}
            </section>

            <section id="team" aria-labelledby="team-title" className="team">
              <h2 id="team-title">Team and credits</h2>
              <div className="team-body">
                <img
                  className="team-logo"
                  src={logo}
                  width="1446"
                  height="1087"
                  alt="Cosmic Shihab logo: a shooting star crossing a ring, with the words COSMIC SHIHAB"
                />
                <div>
                  <p>
                    FLARE was built by <strong>Cosmic Shihab</strong> for the NASA Space Apps Challenge 2026, challenge
                    “Flame in Freefall”.
                  </p>
                  <ol className="team-list">
                    {TEAM.map((name) => (
                      <li key={name}>{name}</li>
                    ))}
                  </ol>
                  <p className="ai-note">
                    FLARE's code and data scripts were written with help from Claude Code (Anthropic's Claude Opus 5.5)
                    and reviewed by the team. The NASA data is shown as NASA published it; none of it is generated.
                  </p>
                </div>
              </div>
            </section>

            <section id="references" aria-labelledby="references-title">
              <h2 id="references-title">References</h2>
              <ul className="ref-list">
                <li>
                  NASA Physical Sciences Informatics (PSI), <a href="https://psi.nasa.gov">psi.nasa.gov</a>: investigation
                  records, file lists and experimental tables. Each investigation is cited by its DOI above.
                </li>
                <li>
                  NASA Space Apps Challenge brand guidelines, updated 25 June 2026,{' '}
                  <a href="https://www.spaceappschallenge.org/brand/">spaceappschallenge.org/brand</a>: palette and
                  typefaces.
                </li>
                <li>
                  Typefaces: Fira Sans and Fira Code (Mozilla) and Overpass (Red Hat), SIL Open Font License 1.1, served
                  through Fontsource.
                </li>
                <li>
                  Software: React, React Router and Vite (MIT), Lucide icons (ISC), FastAPI (MIT). Development assistance:
                  Claude Code by Anthropic.
                </li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </>
  )
}
