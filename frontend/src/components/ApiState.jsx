import { RotateCw, TriangleAlert } from 'lucide-react'
import './ApiState.css'

export function Loading({ label }) {
  return (
    <div className="api-loading" role="status">
      <span className="api-loading-track" aria-hidden="true" />
      {label}
    </div>
  )
}

export function LoadError({ what, retry }) {
  return (
    <div className="api-error" role="alert">
      <TriangleAlert size={20} aria-hidden="true" />
      <div>
        <p>
          <strong>{what} could not load.</strong> The FLARE API did not answer, so this section shows nothing rather
          than a guess.
        </p>
        <button type="button" className="button-quiet" onClick={retry}>
          <RotateCw size={16} aria-hidden="true" />
          Try again
        </button>
      </div>
    </div>
  )
}
