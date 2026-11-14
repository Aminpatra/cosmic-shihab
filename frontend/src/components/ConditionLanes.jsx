import { CircleDashed, Equal, EqualNot } from 'lucide-react'
import './ConditionLanes.css'

// One lane per condition, read like a microgravity test record: the visitor's scenario is a
// Neon Yellow tick, an investigation's tested range is a Blue Yonder band, and a condition the
// investigation never recorded is hatched. Every lane states its result in words as well.
//
// lanes: [{
//   id, label, unit, status: 'match' | 'differs' | 'missing', statusLabel?, readout: [lines],
//   kind: 'range'  -> axis: { min, max, ticks: [numbers] }, band: [lo, hi] | null, value: number | null, missingNote?
//   kind: 'stops'  -> stops: [labels], band: index, value: index
//   kind: 'pair'   -> theirs: text, yours: text
// }]

const STATUS = {
  match: { icon: Equal, label: 'Match' },
  differs: { icon: EqualNot, label: 'Differs' },
  missing: { icon: CircleDashed, label: 'Not recorded' },
}

const pct = (value, { min, max }) => `${((value - min) / (max - min)) * 100}%`

function RangeTrack({ lane }) {
  const { axis, band, value } = lane
  // Keep the "not recorded" note on the side away from the scenario tick.
  const noteSide = value != null && (value - axis.min) / (axis.max - axis.min) < 0.5 ? 'flex-end' : 'flex-start'
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
        <span className="hatch" style={{ justifyContent: noteSide }}>
          <span>{lane.missingNote}</span>
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
  return (
    <div className="track track-stops">
      {lane.stops.map((stop, i) => (
        <span
          key={stop}
          className={['stop', i === lane.band && 'stop-tested', i === lane.value && 'stop-yours'].filter(Boolean).join(' ')}
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
      <span className="pair-theirs">{lane.theirs}</span>
      <span className="pair-yours">{lane.yours}</span>
    </div>
  )
}

const TRACKS = { range: RangeTrack, stops: StopsTrack, pair: PairTrack }

export default function ConditionLanes({ caption, summary, theirsLabel, lanes, animate = false }) {
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
              <tr key={lane.id} className="lane" style={{ '--i': i }}>
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
                  {lane.readout.map((line) => (
                    <span key={line} className="readout">
                      {line}
                    </span>
                  ))}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </figure>
  )
}
