import { PLACES } from '../pages/ScenarioParams.js'
import { FlameGlyph } from './FlameGravity.jsx'
import './GravityScale.css'

// A Scenario row that shows where NASA's combustion evidence sits on the gravity axis. It reuses the
// page's own span lane (span-lane, span-band, span-tick, span-scale, span-words in Scenario.css):
// tested gravity as bands, the untested gap hatched, the visitor's gravity as the Neon Yellow tick.
// The flames are the pitch opening's. SI use: made with Claude Code and reviewed by the team.

const TESTED = 0.025 // width of each tested end on the 0 to 1 g axis; 0 g and 1 g are points
const NAMES = { lunar: 'Moon', mars: 'Mars' }

const at = (g) => `${g * 100}%`
const fmt = (g) => `${Number(g.toFixed(3))} g`

function gravityOf(place, customGravity, environments) {
  const chosen = PLACES.find((pl) => pl.id === place)
  if (!chosen) return null
  if (chosen.environment === 'custom') {
    const g = Number.parseFloat(customGravity)
    return Number.isFinite(g) && g >= 0 && g <= 1 ? g : null
  }
  const g = environments[chosen.environment]
  return typeof g === 'number' ? g : null
}

function status(g) {
  if (g == null) return { words: 'Not set', outside: false }
  if (g <= TESTED) return { words: 'Microgravity: NASA tested this', outside: false }
  if (g >= 1 - TESTED) return { words: 'Earth gravity: NASA tested this', outside: false }
  return { words: `Not tested: no NASA test at ${fmt(g)}`, outside: true }
}

export default function GravityScale({ place, customGravity, environments = {} }) {
  const g = gravityOf(place, customGravity, environments)
  const { words, outside } = status(g)
  const marks = Object.entries(NAMES)
    .filter(([env]) => typeof environments[env] === 'number')
    .map(([env, name]) => ({ name, g: environments[env] }))
    .sort((a, b) => a.g - b.g)

  return (
    <div className="row gs" role="group" aria-labelledby="gs-name">
      <div className="row-label">
        <span className="row-name" id="gs-name">
          Gravity tested
        </span>
        <span className="row-unit">g, 0 to 1</span>
      </div>

      <div className="row-field gs-flames">
        <figure className="gs-flame">
          <FlameGlyph gravity="micro" className="gs-art" />
          <figcaption>0 g, microgravity</figcaption>
        </figure>
        <figure className="gs-flame">
          <FlameGlyph gravity="earth" className="gs-art" />
          <figcaption>1 g, Earth</figcaption>
        </figure>
      </div>

      <div className="row-span">
        <div className="span">
          <div className="span-lane" aria-hidden="true">
            {[0, ...marks.map((m) => m.g), 1].map((t) => (
              <span key={t} className="span-unit" style={{ left: at(t) }} />
            ))}
            <span className="gs-gap" style={{ left: at(TESTED), right: at(TESTED) }} />
            <span className="span-band" style={{ left: 0, width: at(TESTED) }} />
            <span className="span-band" style={{ left: at(1 - TESTED), width: at(TESTED) }} />
            {g != null && <span className="span-tick" style={{ left: at(g) }} />}
          </div>
          <div className="span-scale" aria-hidden="true">
            <span style={{ left: 0 }}>0 g</span>
            {marks.map((m) => (
              <span key={m.name} style={{ left: at(m.g) }}>
                {m.name}
              </span>
            ))}
            <span style={{ left: '100%' }}>1 g</span>
          </div>
          <p className="span-words">
            <span className={outside ? 'span-outside' : undefined}>{words}</span>
            <span>NASA tested microgravity and Earth gravity only</span>
          </p>
        </div>
        <p className="gs-credit">
          Source: each investigation's gravity tag. Moon and Mars as FLARE's ranking sets them. Illustration made with
          SI.
        </p>
      </div>
    </div>
  )
}
