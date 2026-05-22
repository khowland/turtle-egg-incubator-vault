/**
 * useVersion.ts
 * Singleton hook for dynamic version fetch from system_config.
 * Requirement: §1.4 Database-Driven Versioning
 * "The UI must fetch this value dynamically via a singleton pattern on every route"
 */
import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

let cachedVersion: string | null = null
let fetchPromise: Promise<string> | null = null

async function fetchVersion(): Promise<string> {
  if (cachedVersion) return cachedVersion
  if (fetchPromise) return fetchPromise

  fetchPromise = (async () => {
    const { data, error } = await supabase
      .from('system_config')
      .select('config_value')
      .eq('config_name', 'APP_VERSION')
      .single()

    if (error || !data) {
      console.warn('useVersion: system_config fetch failed, using fallback', error)
      cachedVersion = 'v0.0.0'
    } else {
      cachedVersion = data.config_value as string
    }
    return cachedVersion
  })()

  return fetchPromise
}

export function useVersion(): string {
  const [version, setVersion] = useState<string>(cachedVersion ?? 'v0.0.0')

  useEffect(() => {
    fetchVersion().then(v => setVersion(v))
  }, [])

  return version
}
