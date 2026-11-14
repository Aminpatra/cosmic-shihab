import { useCallback, useEffect, useState } from 'react'

// Every backend route starts with /api (docs/DECISIONS.md, #8).
export async function getJSON(path, { signal } = {}) {
  const res = await fetch(`/api${path}`, { signal, headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`The FLARE API answered ${res.status} for ${path}.`)
  return res.json()
}

// { status: 'loading' | 'ready' | 'error', data, error, retry }
export function useApi(path) {
  const [state, setState] = useState({ status: 'loading', data: null, error: null })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    setState({ status: 'loading', data: null, error: null })
    getJSON(path, { signal: controller.signal })
      .then((data) => setState({ status: 'ready', data, error: null }))
      .catch((error) => {
        if (error.name !== 'AbortError') setState({ status: 'error', data: null, error })
      })
    return () => controller.abort()
  }, [path, attempt])

  const retry = useCallback(() => setAttempt((n) => n + 1), [])
  return { ...state, retry }
}
