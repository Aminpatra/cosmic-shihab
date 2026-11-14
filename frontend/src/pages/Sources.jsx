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
  ['reading', 'How FLARE read PSI'],
  ['ranking', 'Ranking method'],
  ['limits', 'Assumptions and limits'],
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
                  <span className="inv-acronym">{nameOf(inv) !== inv.accession ? nameOf(inv) : ''}</span>
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
                  {runs > 0 ? formatNumber(runs) : <span className="absent">No table</span>}
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
      <title>Sources and methodology · FLARE</title>
      <div className="sources">
        <header className="sources-head">
          <h1>Sources and methodology</h1>
          <p className="sources-lede">
            Where FLARE's data comes from, how it was read, what FLARE assumes, and what it cannot tell you.
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
            </section>

            <section id="reading" aria-labelledby="reading-title">
              <h2 id="reading-title">How FLARE read PSI</h2>
              <ul className="facts-list">
                <li>
                  For each investigation FLARE stores PSI's record as published: title, objective, hypothesis, approach,
                  hardware, DOI, licence and publications. Contact e-mail addresses and phone numbers are left out.
                </li>
                <li>
                  The full file list of each investigation is stored as a list, not as files. Duplicate entries are removed
                  by file id, and each list is checked for completeness against the total size PSI reports.
                </li>
                <li>
                  Only the 22 small experimental tables, one row per test or test day, are downloaded, unchanged. Every
                  other file stays at NASA and is linked; download links are requested from PSI when needed.
                </li>
                <li>
                  <strong>Rank and compare</strong> covers the eight investigations whose tables have 87 to 469 runs.{' '}
                  <strong>Show and compare</strong> covers the twelve with 2 to 32 runs: shown in full, too few to model.{' '}
                  <strong>Catalogue only</strong> covers four ground-based modelling studies with no run table.
                </li>
                <li>
                  Table columns differ between investigations: FLEX records pressure and gas fractions, BASS records the
                  sample and its material. Columns are compared across investigations only when they mean the same thing.
                </li>
              </ul>
            </section>

            <section id="ranking" aria-labelledby="ranking-title">
              <h2 id="ranking-title">Ranking method</h2>
              <p>
                Not published yet. FLARE shows no relevance score until this section lists the variables it uses, their
                weights, and how a missing value counts. The ranking engine is being built now.
              </p>
            </section>

            <section id="limits" aria-labelledby="limits-title">
              <h2 id="limits-title">Assumptions and limits</h2>
              <ul className="facts-list">
                <li>
                  A relevance score measures how closely an investigation's tested conditions match a scenario. It is not
                  a safety assessment, and FLARE never predicts whether a real fire will start or spread.
                </li>
                <li>
                  Every flight investigation here ran in microgravity. None tested lunar or Martian gravity, so for a
                  partial-gravity scenario FLARE says the evidence comes from microgravity.
                </li>
                <li>A condition an investigation did not record is shown as not recorded, never estimated.</li>
                <li>Values keep their original units; any conversion is shown beside the original value.</li>
                <li>
                  The Saffire experiments matter most for spacecraft fires but have 2 to 15 runs each. FLARE shows them in
                  full and says how few runs there are.
                </li>
                <li>
                  PSI-142 is an index of published figures, not a table of tests. PSI-10 (ACME Flame Design) states no
                  licence; the other 23 investigations are released under CC0-1.0.
                </li>
              </ul>
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
