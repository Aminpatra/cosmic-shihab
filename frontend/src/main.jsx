import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter } from 'react-router'
import { RouterProvider } from 'react-router/dom'

import '@fontsource/fira-sans/600.css'
import '@fontsource/fira-sans/700.css'
import '@fontsource/fira-sans/900.css'
import '@fontsource/overpass/300.css'
import '@fontsource/overpass/400.css'
import '@fontsource/overpass/600.css'
import '@fontsource/overpass/700.css'
import '@fontsource/fira-code/400.css'
import './styles/tokens.css'
import './styles/base.css'

import Layout from './Layout.jsx'
import Home from './pages/Home.jsx'
import Sources from './pages/Sources.jsx'
import Assistant from './pages/Assistant.jsx'
import Scenario from './pages/Scenario.jsx'
import Comparison from './pages/Comparison.jsx'
import Explorer from './pages/Explorer.jsx'
import ExplorerInvestigation from './pages/ExplorerInvestigation.jsx'
import Methodology from './pages/Methodology.jsx'
import Visualization from './pages/Visualization.jsx'
import InProgress from './pages/InProgress.jsx'
import NotFound from './pages/NotFound.jsx'
import RouteError from './components/RouteError.jsx'
import { PAGES } from './pages.js'

const slots = PAGES.filter((page) => !page.ready).map((page) => ({
  path: page.path.slice(1),
  element: <InProgress page={page} />,
}))

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    // If the layout itself fails there is no header to keep: the message stands on its own.
    errorElement: <RouteError />,
    children: [
      {
        // A page that throws while drawing shows FLARE's message inside the layout, header kept (#86).
        errorElement: <RouteError />,
        children: [
      { index: true, element: <Home /> },
      { path: 'sources', element: <Sources /> },
      { path: 'assistant', element: <Assistant /> },
      { path: 'explorer', element: <Explorer /> },
      { path: 'explorer/:accession', element: <ExplorerInvestigation /> },
      { path: 'scenario', element: <Scenario /> },
      { path: 'comparison', element: <Comparison /> },
      { path: 'methodology', element: <Methodology /> },
      { path: 'visualization', element: <Visualization /> },
      ...slots,
      { path: '*', element: <NotFound /> },
        ],
      },
    ],
  },
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
