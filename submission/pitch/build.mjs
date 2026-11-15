// Rebuilds the pitch after an edit to FlareOpening.jsx. Run from the repository root, after
// `npm ci` in frontend/:
//
//     node submission/pitch/build.mjs
//
// It bundles FlareOpening.jsx with React from frontend/node_modules (using the Vite installed
// there) into one minified script, puts it in place of the script in flare-opening.html (the
// head, with its comment and inline fonts, stays as it is), and copies the page byte for byte to
// frontend/public/pitch.html, which the live site serves (#90).
// SI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
import { createRequire } from 'node:module'
import { copyFileSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repo = resolve(here, '..', '..')
const modules = join(repo, 'frontend', 'node_modules')
const { build } = await import(pathToFileURL(createRequire(join(repo, 'frontend', 'package.json')).resolve('vite')).href)

const work = mkdtempSync(join(tmpdir(), 'flare-pitch-'))
try {
  const entry = join(work, 'entry.js')
  writeFileSync(entry, [
    "import React from 'react'",
    "import { createRoot } from 'react-dom/client'",
    `import FlareOpening from ${JSON.stringify(join(here, 'FlareOpening.jsx').replace(/\\/g, '/'))}`,
    "createRoot(document.getElementById('root')).render(React.createElement(FlareOpening))",
  ].join('\n'))
  await build({
    configFile: false,
    root: work,
    logLevel: 'warn',
    define: { 'process.env.NODE_ENV': '"production"' },
    resolve: { alias: { react: join(modules, 'react'), 'react-dom': join(modules, 'react-dom') } },
    build: {
      outDir: join(work, 'dist'),
      minify: true,
      lib: { entry, formats: ['iife'], name: 'FlarePitch', fileName: () => 'pitch.js' },
    },
  })
  const bundle = readFileSync(join(work, 'dist', 'pitch.js'), 'utf-8').trim()
  if (bundle.includes('</script')) throw new Error('the bundle contains "</script" and cannot be inlined')

  const pagePath = join(here, 'flare-opening.html')
  const page = readFileSync(pagePath, 'utf-8')
  const start = page.indexOf('<script>') + '<script>'.length
  const end = page.lastIndexOf('</script>')
  writeFileSync(pagePath, page.slice(0, start) + bundle + '\n' + page.slice(end))
  copyFileSync(pagePath, join(repo, 'frontend', 'public', 'pitch.html'))
  console.log(`flare-opening.html and frontend/public/pitch.html rebuilt (${bundle.length} characters of script)`)
} finally {
  rmSync(work, { recursive: true, force: true })
}
