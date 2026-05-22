import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { SessionProvider, useSession } from './context/SessionContext'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Intake from './pages/Intake'
import Observations from './pages/Observations'
import SystemCheck from './pages/SystemCheck'
import Help from './pages/Help'
import Settings from './pages/Settings'
import Reports from './pages/Reports'
import Login from './pages/Login'

const AppInner: React.FC = () => {
    const { loading, isAuthenticated } = useSession();

    if (loading) {
        return (
            <div className="app-loading">
                <p>Loading Turtle Incubator...</p>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Login />;
    }

    return (
        <div className="app-container">
            <Sidebar />
            <main className="main-content">
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/intake" element={<Intake />} />
                    <Route path="/observations" element={<Observations />} />
                    <Route path="/system-check" element={<SystemCheck />} />
                    <Route path="/help" element={<Help />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/reports" element={<Reports />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </main>
        </div>
    );
};

const App: React.FC = () => {
    return (
        <SessionProvider>
            <BrowserRouter>
                <AppInner />
            </BrowserRouter>
        </SessionProvider>
    );
};

export default App;
