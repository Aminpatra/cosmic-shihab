import { Inbox, RotateCw, TriangleAlert } from 'lucide-react'
import './ApiState.css'

export function Loading({ label }) {
  return (
    <div className="api-loading" role="status">
      <span className="api-loading-track" aria-hidden="true" />
      {label}
    </div>
  )
}

function TryAgain({ retry }) {
  return (
    <button type="button" className="button-quiet" onClick={retry}>
      <RotateCw size={16} aria-hidden="true" />
      Try again
    </button>
  )
}

// `error` is the one useApi gives; without it the box assumes the API did not answer.
export function LoadError({ what, retry, error }) {
  const why = error?.status
    ? `The FLARE API answered with an error (${error.status})`
    : 'The FLARE API did not answer'
  return (
    <div className="api-error" role="alert">
      <TriangleAlert size={20} aria-hidden="true" />
      <div>
        <p>
          <strong>{what} could not load.</strong> {why}, so this section shows nothing rather than a guess.
        </p>
        <TryAgain retry={retry} />
      </div>
    </div>
  )
}

export function Empty({ what, retry }) {
  return (
    <div className="api-error" role="status">
      <Inbox size={20} aria-hidden="true" />
      <div>
        <p>
          <strong>{what} came back empty.</strong> The FLARE API answered with no investigations, so there is nothing
          to show here yet.
        </p>
        <TryAgain retry={retry} />
      </div>
    </div>
  )
}
