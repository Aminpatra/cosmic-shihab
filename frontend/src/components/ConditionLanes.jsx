import { useState } from 'react'
import { CircleDashed, Equal, EqualNot } from 'lucide-react'
import './ConditionLanes.css'

// One lane per condition, read like a microgravity test record: the visitor's scenario is a
// Neon Yellow tick, an investigation's tested range is a Blue Yonder band, and a condition the
// investigation never recorded is hatched. Every lane states its result in words as well.
// Pointing at or focusing a lane lifts it and shows where its values come from.
//
// lanes: [{
//   id, label, unit, status: 'match' | 'differs' | 'missing', statusLabel?, readout, source,
//   kind: 'range'  -> axis: { min, max, ticks: [numbers] }, band: [lo, hi] | null, value: number | null, missingNote?
//   kind: 'stops'  -> stops: [labels], band: index | [indexes] (none: hatched), value: index
//   kind: 'pair'   -> theirs: text | null (null: hatched), yours: text
// }]

const STATUS = {
  match: { icon: Equal, label: 'Match' },
  differs: { icon: EqualNot, label: 'Differs' },
  missing: { icon: CircleDashed, label: 'Not recorded' },
}

const pct = (value, { min, max }) => `${((value - min) / (max - min)) * 100}%`

// The "not recorded" note lives only in the stretch of track on the far side of the scenario
// tick, and truncates rather than ever crossing it.
function noteBox(lane) {
  const { axis, value } = lane
  if (value == null) return { left: '0.5rem', right: '0.5rem' }
  const at = pct(value, axis)
  return (value - axis.min) / (axis.max - axis.min) < 0.5
    ? { left: `calc(${at} + 0.5rem)`, right: '0.5rem', justifyContent: 'flex-end' }
    : { left: '0.5rem', right: `calc(100% - ${at} + 0.5rem)` }
}

function RangeTrack({ lane }) {
  const { axis, band, value } = lane
  return (
    <div className="track">
      {axis.ticks.map((t) => (
        <span key={t} className="unit-tick" style={{ left: pct(t, axis) }} />
      ))}
      {band ? (
        <span
          className="band"
          style={{ left: pct(band[0], axis), width: `calc(${pct(band[1], axis)} - ${pct(band[0], axis)})` }}
        />
      ) : (
        <span className="hatch">
          {lane.missingNote && (
            <span className="hatch-note" style={noteBox(lane)}>
              <span>{lane.missingNote}</span>
            </span>
          )}
        </span>
      )}
      {value != null && <span className="scenario-tick" style={{ left: pct(value, axis) }} />}
      <span className="scale">
        {axis.ticks.map((t) => (
          <span key={t} style={{ left: pct(t, axis) }}>
            {t.toLocaleString('en-US')}
          </span>
        ))}
      </span>
    </div>
  )
}

// On a lane of named stops the scenario is drawn as a Neon Yellow frame around its stop,
// so the mark never crosses the stop's label.
function StopsTrack({ lane }) {
  const tested = [].concat(lane.band ?? [])
  return (
    <div className={tested.length ? 'track track-stops' : 'track track-stops track-none'}>
      {lane.stops.map((stop, i) => (
        <span
          key={stop}
          className={['stop', tested.includes(i) && 'stop-tested', i === lane.value && 'stop-yours']
            .filter(Boolean)
            .join(' ')}
        >
          {stop}
        </span>
      ))}
    </div>
  )
}

function PairTrack({ lane }) {
  return (
    <div className="track track-pair">
      {lane.theirs == null ? (
        <span className="pair-theirs pair-none" />
      ) : (
        <span className="pair-theirs">{lane.theirs}</span>
      )}
      <span className="pair-yours">{lane.yours}</span>
    </div>
  )
}

const TRACKS = { range: RangeTrack, stops: StopsTrack, pair: PairTrack }

// `source` is the figure's footnote at rest (the investigation's provenance); while a lane is
// lifted, the footnote shows that lane's own source instead.
export default function ConditionLanes({ caption, summary, theirsLabel, lanes, source, animate = false }) {
  const [active, setActive] = useState(null)
  const activeLane = lanes.find((lane) => lane.id === active)

  return (
    <figure className="lanes-figure">
      <figcaption className="lanes-head">
        <span className="lanes-caption">{caption}</span>
        {summary && <span className="lanes-summary">{summary}</span>}
      </figcaption>
      <ul className="lanes-legend" aria-label="How to read the lanes">
        <li>
          <span className="key key-tick" aria-hidden="true" />
          Your scenario
        </li>
        <li>
          <span className="key key-band" aria-hidden="true" />
          {theirsLabel}
        </li>
        <li>
          <span className="key key-hatch" aria-hidden="true" />
          Not recorded
        </li>
      </ul>
      <table className="lanes" data-animate={animate || undefined}>
        <thead className="visually-hidden">
          <tr>
            <th scope="col">Condition</th>
            <th scope="col">Tested range against your scenario</th>
            <th scope="col">Result</th>
          </tr>
        </thead>
        <tbody>
          {lanes.map((lane, i) => {
            const Track = TRACKS[lane.kind]
            const status = STATUS[lane.status]
            const Icon = status.icon
            return (
              <tr
                key={lane.id}
                className="lane"
                style={{ '--i': i }}
                tabIndex={0}
                data-active={active === lane.id || undefined}
                onMouseEnter={() => setActive(lane.id)}
                onMouseLeave={() => setActive(null)}
                onFocus={() => setActive(lane.id)}
                onBlur={() => setActive(null)}
              >
                <th scope="row" className="lane-label">
                  <span className="lane-name">{lane.label}</span>
                  <span className="lane-unit">{lane.unit}</span>
                </th>
                <td className="lane-track" aria-hidden="true">
                  <Track lane={lane} />
                </td>
                <td className="lane-result">
                  <span className={`status status-${lane.status}`}>
                    <Icon size={15} strokeWidth={2.5} aria-hidden="true" />
                    {lane.statusLabel ?? status.label}
                  </span>
                  <span className="readout">{lane.readout}</span>
                  <span className="visually-hidden">Source: {lane.source}</span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      <div className="lanes-source" data-active={activeLane ? true : undefined}>
        {activeLane ? (
          <p aria-hidden="true">
            <strong>{activeLane.label}</strong> comes from {activeLane.source}
          </p>
        ) : (
          <p>{source}</p>
        )}
      </div>
    </figure>
  )
}
