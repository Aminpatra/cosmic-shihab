import { useEffect } from 'react'
import { Link, isRouteErrorResponse, useRouteError } from 'react-router'
import { RotateCw, TriangleAlert } from 'lucide-react'
import './ApiState.css'
import './RouteError.css'

// What a page shows when it throws while drawing (#86), in place of React Router's default
// "Unexpected Application Error!" screen. Inside the layout the header stays, so every other page
// is one click away; navigating anywhere clears the error.
export default function RouteError() {
  const error = useRouteError()
  useEffect(() => console.error(error), [error])
  const status = isRouteErrorResponse(error) ? ` (${error.status})` : ''

  return (
    <>
      <title>Page error · FLARE</title>
      <section className="route-error">
        <div className="api-error" role="alert">
          <TriangleAlert size={20} aria-hidden="true" />
          <div>
            <p>
              <strong>This page could not be shown.</strong> Something failed while FLARE was drawing it{status}, so it
              shows nothing rather than half a page. The rest of the site still works.
            </p>
            <div className="route-error-actions">
              <button type="button" className="button-quiet" onClick={() => window.location.reload()}>
                <RotateCw size={16} aria-hidden="true" />
                Reload the page
              </button>
              <Link to="/">Go to the home page</Link>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
