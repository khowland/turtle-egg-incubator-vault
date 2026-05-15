import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { SessionProvider } from './context/SessionContext'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Intake from './pages/Intake'
import Observations from './pages/Observations'
import Settings from './pages/Settings'
import Reports from './pages/Reports'

const App: React.FC = () => {
  return (
    <SessionProvider>
      <BrowserRouter>
        <div className="app-container">
          <Sidebar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/intake" element={<Intake />} />
              <Route path="/observations" element={<Observations />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </SessionProvider>
  )
}

export default App
