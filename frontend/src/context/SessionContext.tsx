import React, { createContext, useContext, useState, useEffect } from 'react';
import type { Observer } from '../lib/identity';

interface SessionContextType {
    observer: Observer | null;
    setObserver: (o: Observer | null) => void;
    observerList: Observer[];
    loading: boolean;
    isAuthenticated: boolean;
    login: (observer: Observer, sessionId: bigint) => void;
    logout: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

const KEVIN_BYPASS_OBSERVER: Observer = {
    observer_id: 'kevin-uuid-bypass',
    observer_name: 'Kevin (Dev Override)',
    session_id: BigInt(Date.now()),
    login_timestamp: new Date().toISOString()
};

export const SessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [observer, setObserver] = useState<Observer | null>(null);
    const [observerList, setObserverList] = useState<Observer[]>([]);
    const [loading, setLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        // In dev mode, auto-login with KEVIN_BYPASS
        const isDevMode = import.meta.env.VITE_DEV_MODE === 'true';
        if (isDevMode) {
            setObserver(KEVIN_BYPASS_OBSERVER);
            setObserverList([KEVIN_BYPASS_OBSERVER]);
            setIsAuthenticated(true);
        }
        setLoading(false);
    }, []);

    const login = (obs: Observer, sessionId: bigint) => {
        const loggedInObserver = { ...obs, session_id: sessionId };
        setObserver(loggedInObserver);
        setObserverList([loggedInObserver]);
        setIsAuthenticated(true);
    };

    const logout = () => {
        setObserver(null);
        setObserverList([]);
        setIsAuthenticated(false);
    };

    return (
        <SessionContext.Provider
            value={{ observer, setObserver, observerList, loading, isAuthenticated, login, logout }}
        >
            {children}
        </SessionContext.Provider>
    );
};

export const useSession = () => {
    const context = useContext(SessionContext);
    if (context === undefined) {
        throw new Error('useSession must be used within a SessionProvider');
    }
    return context;
};
