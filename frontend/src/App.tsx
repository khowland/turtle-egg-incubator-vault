import React, { Component } from 'react'
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

// ---------------------------------------------------------------------------
// Error Boundary — catastrophic UI failure catches render-time exceptions
// ---------------------------------------------------------------------------
interface ErrorBoundaryProps { children: React.ReactNode }
interface ErrorBoundaryState { hasError: boolean; error: Error | null }

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('[ErrorBoundary] Uncaught render error:', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="app-loading" style={{ color: 'red', padding: '2rem', textAlign: 'center' }}>
          <h2>Something went wrong.</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>Reload Application</button>
        </div>
      )
    }
    return this.props.children
  }
}

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
        <ErrorBoundary>
            <SessionProvider>
                <BrowserRouter>
                    <AppInner />
                </BrowserRouter>
            </SessionProvider>
        </ErrorBoundary>
    );
};

export default App;
