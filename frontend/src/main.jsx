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
import InProgress from './pages/InProgress.jsx'
import NotFound from './pages/NotFound.jsx'
import { PAGES } from './pages.js'

const slots = PAGES.filter((page) => !page.ready).map((page) => ({
  path: page.path.slice(1),
  element: <InProgress page={page} />,
}))

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'sources', element: <Sources /> },
      { path: 'assistant', element: <Assistant /> },
      { path: 'scenario', element: <Scenario /> },
      ...slots,
      { path: '*', element: <NotFound /> },
    ],
  },
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
