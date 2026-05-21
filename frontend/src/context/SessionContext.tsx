import React, { createContext, useContext, useState } from 'react'
import type { Observer } from '../lib/identity'

interface SessionContextType {
  observer: Observer | null
  setObserver: (o: Observer | null) => void
  loading: boolean
}

const SessionContext = createContext<SessionContextType | undefined>(undefined)

// KEVIN_UUID bypass for primary user (Enterprise Parity)
const DEFAULT_OBSERVER: Observer = {
  observer_id: 1,
  observer_name: 'Expert Herpetologist',
  session_id: BigInt(Date.now()), // Temp surrogate, will be hardened in v9.6.6
  login_timestamp: new Date().toISOString()
}

export const SessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [observer, setObserver] = useState<Observer | null>(DEFAULT_OBSERVER)
  const [loading] = useState(false)

  return (
    <SessionContext.Provider value={{ observer, setObserver, loading }}>
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
