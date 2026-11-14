import { Link, useLocation } from 'react-router'
import './InProgress.css'

export default function NotFound() {
  const { pathname } = useLocation()
  return (
    <>
      <title>Page not found · FLARE</title>
      <section className="slot">
        <h1>Page not found</h1>
        <p className="slot-lede">
          No FLARE page lives at <code>{pathname}</code>.
        </p>
        <p className="slot-next">
          Go to the <Link to="/">Home page</Link> or to <Link to="/sources">Sources and methodology</Link>.
        </p>
      </section>
    </>
  )
}
