import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, ScrollRestoration, useLocation } from 'react-router'
import { CircleDashed, Menu, X } from 'lucide-react'
import { PAGES } from './pages.js'
import './Layout.css'

export default function Layout() {
  const [menuOpen, setMenuOpen] = useState(false)
  const { pathname } = useLocation()

  // Close the phone menu whenever the page changes.
  useEffect(() => setMenuOpen(false), [pathname])

  return (
    <>
      <a className="skip-link" href="#content">
        Skip to content
      </a>
      <header className="bar">
        <Link to="/" className="wordmark" aria-label="FLARE, home">
          FLARE
          <span className="wordmark-full">Fire Learning, Analysis &amp; Research Explorer</span>
        </Link>
        <button
          type="button"
          className="menu-toggle"
          aria-expanded={menuOpen}
          aria-controls="site-nav"
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? <X size={20} aria-hidden="true" /> : <Menu size={20} aria-hidden="true" />}
          Menu
        </button>
        <nav id="site-nav" className="nav" data-open={menuOpen} aria-label="Pages">
          <ul>
            {PAGES.map((page) => (
              <li key={page.path}>
                <NavLink to={page.path} end={page.path === '/'} className="nav-link">
                  {page.nav}
                  {!page.ready && (
                    <>
                      <CircleDashed className="nav-pending" size={12} strokeWidth={2.25} aria-hidden="true" />
                      <span className="visually-hidden"> (in progress)</span>
                    </>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </header>

      <main id="content" tabIndex={-1}>
        <Outlet />
      </main>

      <footer className="site-footer">
        <p>
          <strong>FLARE</strong> by Cosmic Shihab
          <br />
          NASA Space Apps 2026, Flame in Freefall
        </p>
        <p>
          Data: NASA Physical Sciences Informatics. FLARE helps people find and compare research. A relevance score is
          not a safety assessment, and FLARE never predicts a real fire. <Link to="/sources">Sources and methodology</Link>
        </p>
      </footer>
      <ScrollRestoration />
    </>
  )
}
