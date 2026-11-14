import { useId } from 'react'
import { FlameGlyph } from './FlameGravity.jsx'
import './Astronaut.css'

// FLARE's astronaut: floating in microgravity, reaching toward the spherical flame the challenge
// describes, so the one illustration on Home carries the product's subject.
// AI use: drawn in SVG by Claude Code and reviewed by the team; shown with the visible
// "Illustration made with AI" the Space Apps rules ask for.

// The flame's glow, reflected in the visor (the same warm colour FlameGlyph uses).
const FIRE_GLOW = '#FFB25B'

function AstronautArt({ className }) {
  const id = useId().replace(/:/g, '')
  return (
    <svg className={className} viewBox="0 0 200 200" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id={`${id}-visor`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#0042A6" />
          <stop offset="0.65" stopColor="#0A1D4D" />
          <stop offset="1" stopColor="#07173F" />
        </linearGradient>
        <linearGradient id={`${id}-suit`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#B9C6E4" />
          <stop offset="0.35" stopColor="#E6ECF8" />
          <stop offset="1" stopColor="#FFFFFF" />
        </linearGradient>
      </defs>
      <g className="astro-body">
        <g transform="rotate(-12 100 104)">
          {/* Life-support pack, behind the body */}
          <rect x="58" y="80" width="24" height="54" rx="6" fill="#B9C6E4" stroke="#5C77AE" />
          <rect x="62" y="90" width="5" height="30" rx="2" fill="#5C77AE" />

          {/* Legs, loose in microgravity, with boots */}
          <path d="M90 134 C 88 152, 82 162, 74 172" fill="none" stroke="#E6ECF8" strokeWidth="18" strokeLinecap="round" />
          <path d="M106 134 C 114 150, 124 156, 132 166" fill="none" stroke="#E6ECF8" strokeWidth="18" strokeLinecap="round" />
          <path d="M77 168 L 71 177" fill="none" stroke="#B9C6E4" strokeWidth="19" strokeLinecap="round" />
          <path d="M129 163 L 136 170" fill="none" stroke="#B9C6E4" strokeWidth="19" strokeLinecap="round" />

          {/* Back arm, relaxed */}
          <path d="M82 94 C 70 106, 66 120, 72 131" fill="none" stroke="#B9C6E4" strokeWidth="13" strokeLinecap="round" />
          <circle cx="73" cy="133" r="7" fill="#5C77AE" />

          {/* Torso */}
          <rect x="76" y="80" width="44" height="60" rx="15" fill={`url(#${id}-suit)`} stroke="#5C77AE" />
          <rect x="87" y="99" width="22" height="14" rx="2" fill="#28467F" />
          <circle cx="93" cy="106" r="2.2" fill="#2E96F5" />
          <circle cx="100" cy="106" r="2.2" fill="#B9C6E4" />
          <rect x="104" y="104" width="2.5" height="4" fill="#B9C6E4" />
          <path d="M78 128 H 118" stroke="#B9C6E4" strokeWidth="3" />

          {/* Front arm, reaching toward the flame */}
          <path d="M113 93 C 128 90, 141 82, 152 70" fill="none" stroke="#FFFFFF" strokeWidth="13" strokeLinecap="round" />
          <circle cx="155" cy="66" r="7.5" fill="#B9C6E4" stroke="#5C77AE" />

          {/* Neck ring and helmet */}
          <ellipse cx="98" cy="86" rx="19" ry="5.5" fill="#B9C6E4" stroke="#5C77AE" />
          <circle cx="98" cy="60" r="28" fill="#FFFFFF" stroke="#5C77AE" />
          <rect x="70.5" y="54" width="5" height="12" rx="1.5" fill="#B9C6E4" />
          <ellipse cx="105" cy="60" rx="19" ry="15" fill={`url(#${id}-visor)`} stroke="#28467F" strokeWidth="1.5" />
          {/* The flame, reflected in the visor */}
          <ellipse cx="114" cy="64" rx="5" ry="4.5" fill={FIRE_GLOW} opacity="0.4" />
          <path d="M92 52 Q 99 46 110 48" fill="none" stroke="#E6ECF8" strokeWidth="3" strokeLinecap="round" opacity="0.75" />
          <circle cx="115" cy="53" r="1.8" fill="#E6ECF8" opacity="0.7" />
        </g>
      </g>
    </svg>
  )
}

/** The Home figure: the astronaut beside a microgravity flame, with its source and AI mark. */
export default function Astronaut() {
  return (
    <figure className="astro" aria-labelledby="astro-caption">
      <div className="astro-scene" role="img" aria-label="Illustration: an astronaut floating beside a round flame">
        <AstronautArt className="astro-art" />
        <FlameGlyph gravity="micro" animate className="astro-flame" />
      </div>
      <figcaption id="astro-caption" className="astro-caption">
        <span>
          In orbit a candle flame becomes a “ghostly blue sphere”: with no buoyancy, hot gas does not rise.
        </span>
        <span className="astro-source">
          Quote: NASA Space Apps 2026 challenge “Flame in Freefall”. Illustration made with AI.
        </span>
      </figcaption>
    </figure>
  )
}
