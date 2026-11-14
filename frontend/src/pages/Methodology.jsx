import { Link } from 'react-router'
import FlameGravity from '../components/FlameGravity.jsx'
import './Sources.css'
import './Methodology.css'

const SECTIONS = [
  ['data', 'Where the data comes from'],
  ['tables', 'How the tables were read'],
  ['tags', 'Investigation tags'],
  ['ranking', 'How ranking works'],
  ['assistant', 'What the assistant may do'],
  ['limits', 'Assumptions and limits'],
]

const REPO = 'https://github.com/gheathwahab/cosmic-shihab/blob/main/'

function File({ path, children }) {
  return (
    <a className="id" href={`${REPO}${path}`} target="_blank" rel="noreferrer">
      {children ?? path}
    </a>
  )
}

export default function Methodology() {
  return (
    <>
      <title>Methodology · FLARE</title>
      <div className="sources method">
        <header className="sources-head">
          <h1>Methodology</h1>
          <p className="sources-lede">
            How FLARE reads NASA's records, compares investigations, ranks them against a scenario and answers
            questions, and where each step stops.
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
              <h2 id="data-title">Where the data comes from</h2>
              <p className="method-lead">
                Everything comes from NASA's Physical Sciences Informatics (PSI) repository, research area Combustion
                Science, retrieved on 14 November 2026. The <Link to="/sources">Sources page</Link> lists the 24
                investigations with their DOIs.
              </p>
              <ul className="facts-list">
                <li>
                  <strong>Records.</strong> Each investigation's PSI record is stored as published: title, objective,
                  hypothesis, approach, hardware, DOI, licence and publications. Contact e-mail addresses and phone
                  numbers are left out.
                </li>
                <li>
                  <strong>File lists.</strong> PSI lists 60,866 files (13.5 TB) for these investigations. FLARE stores the
                  list, not the files, after removing duplicate entries and checking each list against the total size PSI
                  reports. A file opens through a download link requested from PSI at the moment it is needed.
                </li>
                <li>
                  <strong>Experimental tables.</strong> The 22 small tables PSI publishes for 20 investigations, 2,009 rows
                  in all, are downloaded unchanged; <File path="datasets/SOURCES.csv" /> records where each came from and
                  that its size matches PSI's.
                </li>
                <li>
                  <strong>Documents.</strong> 256 of the 352 PSI documents in scope are indexed for search, as 18,036
                  passages of about 150 words. The other 96 could not be read: 72 hold no text (mostly engineering
                  drawings), 15 are in old Word and PowerPoint formats, 7 could not be served by PSI on the day (5 of them
                  Saffire) and 2 are damaged PDFs.
                </li>
              </ul>
            </section>

            <section id="tables" aria-labelledby="tables-title">
              <h2 id="tables-title">How the tables were read</h2>
              <p className="method-lead">
                Every cell keeps PSI's own text. Beside it, FLARE records what it could read from that text, and copies a
                few conditions that mean the same thing everywhere into one unit. Full rules:{' '}
                <File path="backend/data/README.md" />.
              </p>
              <dl className="method-terms">
                <div>
                  <dt>What a cell holds</dt>
                  <dd>
                    A number (with its unit, or marked approximate), a list, a range, text, or missing. A list is never
                    averaged, and a missing value is never read as zero.
                  </dd>
                </div>
                <div>
                  <dt>What a row is</dt>
                  <dd>
                    One test in most tables, but one test day in SLICE and four ACME tables, one session in DAFT, one fuel
                    with ranges of conditions in FLEX-2, and one published figure in PSI-142. Rows are counted as tests
                    only where they are tests: 1,879 tests in 14 tables from 12 investigations.
                  </dd>
                </div>
                <div>
                  <dt>Common fields</dt>
                  <dd>
                    Oxygen as a mole fraction, pressure in atmospheres, flow velocity in cm/s, and fuel, all known before a
                    test; burn time in seconds and how the test ended, measured during it. A converted value is marked as
                    calculated and keeps the original beside it.
                  </dd>
                </div>
                <div>
                  <dt>Suspect values</dt>
                  <dd>
                    Kept as written and flagged: a negative gas reading, a percentage over 100, a chemical formula a
                    spreadsheet counted upwards (CH4, CH5, CH6…), a number with a stray leading zero. A flagged value is
                    never scored.
                  </dd>
                </div>
              </dl>
              <p>
                Three groups follow from the tables. <strong>Rank and compare</strong>: eight investigations with 87 to
                469 runs each. <strong>Show and compare</strong>: twelve with 2 to 32 rows each, shown in full but too few to
                model (PSI-142's rows are published figures, not tests). <strong>Catalogue only</strong>: four ground-based modelling studies with no run table.
              </p>
            </section>

            <section id="tags" aria-labelledby="tags-title">
              <h2 id="tags-title">Investigation tags</h2>
              <p className="method-lead">
                Each investigation carries hand-written tags for its hardware and facility, platform, fuel phase,
                fire-safety role, gravity level and the data FLARE holds. Every tag names the field of the PSI record or
                the table it comes from (<File path="research/investigation_tags.csv" />).
              </p>
              <ul className="facts-list">
                <li>
                  A fire-safety role (prevention, detection or suppression) is tagged only where the record states it as
                  the investigation's aim. That leaves 16 of the 24 as “not stated”, including some whose records mention a
                  role only as an expected benefit.
                </li>
                <li>
                  Comparing flammability with NASA's material screening test is tagged as prevention, because that test
                  decides which materials fly. This is FLARE's reading; the records do not use the word.
                </li>
              </ul>
            </section>

            <section id="ranking" aria-labelledby="ranking-title">
              <h2 id="ranking-title">How ranking works</h2>
              <p className="method-lead">
                The ranking answers “which NASA evidence should I read first for this scenario?”, never “is this scenario
                safe?”. Each test is scored against the conditions you set, and an investigation takes the score of its
                closest test. Design:{' '}
                <File path="docs/superpowers/specs/2026-11-14-ranking-engine-design.md">ranking engine design</File>.
              </p>
              <dl className="method-terms">
                <div>
                  <dt>Numbers</dt>
                  <dd>
                    For oxygen, pressure and flow, a test scores <span className="method-formula">1 − |test − scenario| ÷ tolerance</span>, and never below 0. The tolerance is a quarter of that variable's span across all tests: derived from
                    the data, not from fire science.
                  </dd>
                </div>
                <div>
                  <dt>Fuel, phase and role</dt>
                  <dd>
                    Fuel scores 1 when your fuel names the test's fuel or material, with formula names understood (C2H4 is
                    ethylene); fuel phase and fire-safety role score 1 when the investigation's tag includes them.
                  </dd>
                </div>
                <div>
                  <dt>Missing conditions</dt>
                  <dd>
                    A condition you set that a test did not record scores 0 and is listed as unavailable. It is never
                    skipped, so measuring less can never rank an investigation higher.
                  </dd>
                </div>
                <div>
                  <dt>Weights</dt>
                  <dd>
                    All equal by default, because FLARE claims no condition matters more for fire safety. Any weight can be
                    changed per request.
                  </dd>
                </div>
                <div>
                  <dt>The score</dt>
                  <dd>
                    0 to 100, from the investigation's best test. Next to it, not mixed in: how many of its tests score 0.8
                    or more, so the depth of evidence stays visible.
                  </dd>
                </div>
                <div>
                  <dt>Not ranked</dt>
                  <dd>
                    Investigations with no experimental table, PSI-142's index of figures, and any whose rows record no
                    fuel or condition. They are listed with the reason.
                  </dd>
                </div>
              </dl>
              <p>
                No investigation here ran in lunar or Martian gravity. For a partial-gravity scenario every result names
                the gravity its own tests ran in, microgravity or normal gravity, and says it is not partial gravity.
                Gravity is left out of the score, because nothing could match it.
              </p>
              <FlameGravity />
            </section>

            <section id="assistant" aria-labelledby="assistant-title">
              <h2 id="assistant-title">What the assistant may do</h2>
              <p className="method-lead">
                The <Link to="/assistant">assistant</Link> answers one question at a time from the PSI records and the
                indexed document passages that match it. It runs on Claude Opus 5.5 (Anthropic).
              </p>
              <dl className="method-terms">
                <div>
                  <dt>It does</dt>
                  <dd>
                    Cite the exact source passage for every statement it bases on NASA's text, mark its own explanation
                    apart from what the sources say, and say plainly when no source answers.
                  </dd>
                </div>
                <div>
                  <dt>It does not</dt>
                  <dd>
                    Invent or estimate results, conditions, materials or numbers; fill gaps from general knowledge; give
                    safety recommendations; or change the ranking, which it never reads.
                  </dd>
                </div>
                <div>
                  <dt>Without a key</dt>
                  <dd>
                    When no AI key is configured, or the model declines or fails, it shows only the matching sources and
                    says why, with no generated text.
                  </dd>
                </div>
                <div>
                  <dt>Stored summaries</dt>
                  <dd>
                    Per-investigation summaries are generated once from the same sources and labelled as AI-generated. A
                    summary counts as reviewed only after a team member has checked it against its citations.
                  </dd>
                </div>
              </dl>
            </section>

            <section id="limits" aria-labelledby="limits-title">
              <h2 id="limits-title">Assumptions and limits</h2>
              <ul className="facts-list">
                <li>
                  A relevance score measures how closely an investigation's tested conditions match a scenario. It is not
                  a safety assessment, and FLARE never predicts whether a real fire will start or spread.
                </li>
                <li>
                  Every flight investigation here ran in microgravity; one ground study ran in normal gravity. None
                  tested lunar or Martian gravity, so for a partial-gravity scenario FLARE names the gravity the evidence
                  comes from and says it is not partial gravity.
                </li>
                <li>
                  A condition an investigation did not record is shown as not recorded, never estimated. Of the 14 test
                  tables, 13 give the fuel, 9 the oxygen, 6 the pressure and 6 the flow velocity; no investigation records
                  all three of oxygen, pressure and flow.
                </li>
                <li>Values keep their original units; any conversion is shown beside the original value.</li>
                <li>
                  The Saffire experiments matter most for spacecraft fires but have 2 to 15 runs each, and 5 of their
                  documents could not be fetched from PSI. FLARE shows them in full and says how few runs there are.
                </li>
                <li>
                  PSI's tables contain errors FLARE keeps rather than corrects: impossible formulas, mis-formatted
                  percentages, spreadsheet error cells and swapped dimensions. They are listed in{' '}
                  <File path="research/data_limitations.md" />.
                </li>
                <li>
                  PSI-10 (ACME Flame Design) states no licence; the other 23 investigations are released under CC0-1.0.
                </li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </>
  )
}
