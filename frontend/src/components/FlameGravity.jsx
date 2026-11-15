import { useId } from 'react'
import './FlameGravity.css'

// The two flames of the pitch opening (submission/pitch/FlareOpening.jsx, `Flame` and `Defs`):
// the same paths, gradients and flicker, so the app and the pitch draw fire the same way.
// SI use: illustration and code made with Claude Code and reviewed by the team; every place that
// shows it carries the visible "Illustration made with SI" the Space Apps rules ask for.

// Colours of the opening's fire, used for the illustration only, never for text or data.
const FIRE = '#FF8A3D'
const FIRE_GLOW = '#FFB25B'
const FLAME_CORE = '#6FA8FF'

const EARTH_PATH =
  'M0 -134 C 10 -104, 34 -76, 32 -42 C 30 -14, 16 0, 0 0 C -16 0, -30 -14, -32 -42 C -34 -76, -10 -104, 0 -134 Z'

/** One flame: `earth` (a teardrop, hot gas rising) or `micro` (a near-sphere, no buoyancy). */
export function FlameGlyph({ gravity = 'micro', animate = false, arrows = false, className }) {
  // useId gives ":r1:"; colons are awkward inside url(#…), so drop them.
  const id = useId().replace(/:/g, '')
  const amb = (name, d, delay) => ({
    className: animate ? `fg-amb ${name}` : undefined,
    style: animate ? { '--d': d, ...(delay ? { '--delay': delay } : {}) } : undefined,
  })

  return (
    <svg className={className} viewBox="-90 -150 180 180" aria-hidden="true" focusable="false">
      <defs>
        <radialGradient id={`${id}-glow`}>
          <stop offset="0" stopColor={FIRE_GLOW} stopOpacity="0.55" />
          <stop offset="0.45" stopColor={FIRE} stopOpacity="0.22" />
          <stop offset="1" stopColor={FIRE} stopOpacity="0" />
        </radialGradient>
        <radialGradient id={`${id}-shell`}>
          <stop offset="0" stopColor={FIRE_GLOW} stopOpacity="0.15" />
          <stop offset="0.6" stopColor={FIRE_GLOW} stopOpacity="0.6" />
          <stop offset="0.86" stopColor={FIRE} stopOpacity="0.85" />
          <stop offset="1" stopColor={FIRE} stopOpacity="0" />
        </radialGradient>
        <radialGradient id={`${id}-core`}>
          <stop offset="0" stopColor="#E3EEFF" />
          <stop offset="0.45" stopColor="#9CC3FF" />
          <stop offset="0.8" stopColor={FLAME_CORE} />
          <stop offset="1" stopColor={FLAME_CORE} stopOpacity="0" />
        </radialGradient>
        <linearGradient id={`${id}-earth`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#FFE7B0" />
          <stop offset="0.5" stopColor={FIRE_GLOW} />
          <stop offset="1" stopColor={FIRE} />
        </linearGradient>
      </defs>

      {gravity === 'earth' ? (
        <g>
          <circle cy="-52" r="78" fill={`url(#${id}-glow)`} opacity=".6" />
          <g {...amb('fg-tall', '1.8s')}>
            <path d={EARTH_PATH} fill={`url(#${id}-earth)`} />
            <ellipse cy="-16" rx="20" ry="13" fill={`url(#${id}-core)`} opacity=".9" />
          </g>
          {arrows && (
            <path
              className="fg-arrow"
              d="M66 -30 V -118 M54 -104 L66 -120 L78 -104"
              fill="none"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}
        </g>
      ) : (
        <g transform="translate(0 -60)">
          <g {...amb('fg-glow', '4.6s')}>
            <circle r="74" fill={`url(#${id}-glow)`} />
          </g>
          <g {...amb('fg-flick-a', '3.2s')}>
            <ellipse rx="34" ry="30" fill={`url(#${id}-shell)`} />
          </g>
          <g {...amb('fg-flick-b', '4.4s', '-1.3s')}>
            <ellipse cx="3" cy="-3" rx="30" ry="33" fill={`url(#${id}-shell)`} opacity=".75" />
          </g>
          <g {...amb('fg-flick-c', '5.8s', '-2.6s')}>
            <ellipse cx="-3" cy="2" rx="32" ry="28" fill={`url(#${id}-shell)`} opacity=".65" />
          </g>
          <g {...amb('fg-core', '3.7s', '-0.8s')}>
            <ellipse rx="21" ry="20" fill={`url(#${id}-core)`} />
          </g>
          {arrows && (
            <path
              className="fg-arrow"
              d="M-84 0 H -50 M-60 -9 L-48 0 L-60 9 M84 0 H 50 M60 -9 L48 0 L60 9"
              fill="none"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}
        </g>
      )}
    </svg>
  )
}

/** Methodology: why gravity matters, drawn as the opening draws it. */
export default function FlameGravity() {
  return (
    <figure className="fg" aria-labelledby="fg-caption">
      <figcaption id="fg-caption" className="fg-caption">
        One flame, two gravities
      </figcaption>
      <div className="fg-panels">
        <div className="fg-panel">
          <FlameGlyph gravity="earth" arrows animate className="fg-art" />
          <p className="fg-name">On Earth, 1 g</p>
          <p className="fg-note">Hot gas rises, so the flame stretches into a teardrop.</p>
        </div>
        <div className="fg-panel">
          <FlameGlyph gravity="micro" arrows animate className="fg-art" />
          <p className="fg-name">In microgravity, about 0 g</p>
          <p className="fg-note">No buoyancy: the flame rounds into a sphere, fed by air drifting in.</p>
        </div>
      </div>
      <div className="fg-source">
        <p>
          Source: NASA Space Apps 2026 challenge “Flame in Freefall”: “Instead of a flickering teardrop, a candle
          flame becomes a ghostly blue sphere reliant on diffusion for its oxygen.” Lunar (0.17 g) and Martian
          (0.38 g) gravity lie between the two, and no investigation here tested them.
        </p>
        <p>Illustration made with SI.</p>
      </div>
    </figure>
  )
}
