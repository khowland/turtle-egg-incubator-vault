import { NavLink } from 'react-router-dom'
import { useSession } from '../context/SessionContext'

export default function Sidebar() {
  const { observer } = useSession()

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="turtle-icon">🐢</div>
        <div className="version-tag">v9.6.6</div>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>
          📊 Today's Summary
        </NavLink>
        <NavLink to="/intake" className={({ isActive }) => isActive ? 'active' : ''}>
          📥 New Intake
        </NavLink>
        <NavLink to="/observations" className={({ isActive }) => isActive ? 'active' : ''}>
          🔍 Observations
        </NavLink>
        <NavLink to="/reports" className={({ isActive }) => isActive ? 'active' : ''}>
          📈 Reports
        </NavLink>
        <NavLink to="/system-check" className={({ isActive }) => isActive ? 'active' : ''}>
          🩺 System Check
        </NavLink>
        <NavLink to="/help" className={({ isActive }) => isActive ? 'active' : ''}>
          📚 Help
        </NavLink>
        <NavLink to="/settings" className={({ isActive }) => isActive ? 'active' : ''}>
          ⚙️ Settings
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <div className="observer-info">
          <p>{observer?.observer_name}</p>
          <span>Expert Herpetologist</span>
        </div>
        
        <button className="btn btn-danger btn-shift-end" onClick={() => window.location.reload()}>
          SHIFT END
        </button>

        <div className="sidebar-terminal-trigger">
          {'>'}_ Forensic Echo
        </div>
      </div>
    </aside>
  )
}
