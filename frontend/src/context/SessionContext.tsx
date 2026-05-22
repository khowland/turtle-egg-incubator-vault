import React, { createContext, useContext, useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import type { Observer } from '../lib/identity'

interface SessionContextType {
  observer: Observer | null
  setObserver: (o: Observer | null) => void
  observerList: Observer[]
  loading: boolean
}

const SessionContext = createContext<SessionContextType | undefined>(undefined)

// KEVIN_UUID bypass — §4 forensic audit override for local dev without login flow
const KEVIN_BYPASS_OBSERVER: Observer = {
  observer_id: 'kevin-uuid-bypass',
  observer_name: 'Kevin (Audit Override)',
  session_id: BigInt(Date.now()), // Temp surrogate — TODO: replace with real session_log insert when login flow exists
  login_timestamp: new Date().toISOString()
}

export const SessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [observer, setObserver] = useState<Observer | null>(null)
  const [observerList, setObserverList] = useState<Observer[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadObservers() {
      try {
        const { data, error } = await supabase
          .from('observer')
          .select('*')
          .eq('is_active', true)
          .order('display_name')

        if (error) {
          console.error('Observer fetch error:', error)
          // Fall back to KEVIN_UUID bypass
          setObserver(KEVIN_BYPASS_OBSERVER)
          setObserverList([KEVIN_BYPASS_OBSERVER])
          return
        }

        if (!data || data.length === 0) {
          console.warn('No active observers found — using KEVIN_UUID bypass')
          setObserver(KEVIN_BYPASS_OBSERVER)
          setObserverList([KEVIN_BYPASS_OBSERVER])
          return
        }

        const observers: Observer[] = data.map((row: any) => ({
          observer_id: String(row.observer_id),
          observer_name: row.display_name,
          session_id: BigInt(Date.now()), // TODO: replace with real session_log insert when login flow exists
          login_timestamp: new Date().toISOString()
        }))

        setObserverList(observers)
        setObserver(observers[0]) // Default to first active observer
      } catch (err) {
        console.error('Observer load exception:', err)
        setObserver(KEVIN_BYPASS_OBSERVER)
        setObserverList([KEVIN_BYPASS_OBSERVER])
      } finally {
        setLoading(false)
      }
    }

    loadObservers()
  }, [])

  return (
    <SessionContext.Provider value={{ observer, setObserver, observerList, loading }}>
      {children}
    </SessionContext.Provider>
  )
}

export const useSession = () => {
  const context = useContext(SessionContext)
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider')
  }
  return context
}
