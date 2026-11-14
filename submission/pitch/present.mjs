// Presents the FLARE pitch: run `node present.mjs` in this folder, and the pitch opens in your
// browser (or open the address it prints).
//
// It serves flare-opening.html at /pitch.html and passes every other request to the live site,
// https://cosmic-shihab.vercel.app. The website on slides 4 to 6 then shares the pitch's
// address, so the slides can use its real pages the way a visitor does: type into the Scenario
// form, move the Visualization slider, ask the Assistant a question.
//
// Needs Node 18 or later and an internet connection; nothing to install. Stop it with Ctrl+C.
// Options: --no-open (do not open a browser), PORT=5190 (another port).
import { createServer } from 'node:http'
import { request } from 'node:https'
import { readFile } from 'node:fs/promises'
import { spawn } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const SITE = new URL('https://cosmic-shihab.vercel.app')
const PAGE = fileURLToPath(new URL('./flare-opening.html', import.meta.url))
const FIRST_PORT = Number(process.env.PORT) || 5180

const server = createServer(async (req, res) => {
  const path = req.url.split('?')[0]
  if (path === '/pitch.html' || path === '/pitch') {
    try {
      const html = await readFile(PAGE)
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' })
      res.end(html)
    } catch (err) {
      res.writeHead(500, { 'content-type': 'text/plain; charset=utf-8' })
      res.end(`Could not read ${PAGE}: ${err.message}`)
    }
    return
  }

  // Everything else is the live site, passed through unchanged.
  const headers = { ...req.headers, host: SITE.host }
  delete headers.connection
  delete headers.referer
  if (headers.origin) headers.origin = SITE.origin
  const upstream = request({ host: SITE.hostname, port: 443, method: req.method, path: req.url, headers }, (up) => {
    const out = { ...up.headers }
    delete out.connection
    delete out['keep-alive']
    delete out['strict-transport-security']
    // Keep redirects on this address, so the site stays next to the pitch.
    if (typeof out.location === 'string' && out.location.startsWith(SITE.origin)) out.location = out.location.slice(SITE.origin.length) || '/'
    res.writeHead(up.statusCode || 502, out)
    up.pipe(res)
  })
  upstream.on('error', (err) => {
    if (!res.headersSent) res.writeHead(502, { 'content-type': 'text/plain; charset=utf-8' })
    res.end(`The live site did not answer: ${err.message}`)
  })
  req.pipe(upstream)
})

function open(url) {
  const [cmd, args] =
    process.platform === 'win32' ? ['cmd', ['/c', 'start', '', url]] : process.platform === 'darwin' ? ['open', [url]] : ['xdg-open', [url]]
  try {
    spawn(cmd, args, { stdio: 'ignore', detached: true }).on('error', () => {}).unref()
  } catch {
    // No browser to open: the address is printed above.
  }
}

function listen(port, triesLeft) {
  server.once('error', (err) => {
    if (err.code === 'EADDRINUSE' && triesLeft > 0) return listen(port + 1, triesLeft - 1)
    console.error(`Could not start: ${err.message}`)
    process.exit(1)
  })
  // Only this computer can reach it.
  server.listen(port, '127.0.0.1', () => {
    const url = `http://127.0.0.1:${port}/pitch.html`
    console.log(`FLARE pitch: ${url}`)
    console.log(`Slides 4 to 6 use the live site, ${SITE.origin}. Press Ctrl+C to stop.`)
    if (!process.argv.includes('--no-open')) open(url)
  })
}

listen(FIRST_PORT, 10)
