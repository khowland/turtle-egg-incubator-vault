import { NavLink, useNavigate } from 'react-router-dom'
import { useVersion } from '../hooks/useVersion'
import { useSession } from '../context/SessionContext'
import { supabase } from '../lib/supabase'

function handleShiftEnd(observer: { observer_id: string; observer_name: string; session_id: bigint } | null, navigate: ReturnType<typeof useNavigate>) {
  // Log forensic SHIFT END event to system_log per §4
  if (observer) {
    supabase.from('system_log').insert({
      session_id: observer.session_id,
      observer_id: observer.observer_id,
      event_type: 'SESSION_TERMINATED',
      event_message: `SHIFT END by ${observer.observer_name}`,
      payload: { action: 'shift_end', observer_id: observer.observer_id }
    }).then(
      () => console.log('[Forensic] SHIFT END logged'),
      (err) => console.error('[Forensic] SHIFT END log failed:', err)
    )
  }
  // Navigate to root with full state reset via replace + reload
  navigate('/', { replace: true })
  setTimeout(() => window.location.reload(), 100)
}

export default function Sidebar() {
  const { observer } = useSession()
  const version = useVersion()
  const navigate = useNavigate()

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="turtle-icon">🐢</div>
        <div className="version-tag">{version}</div>
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
          <p>{observer?.observer_name || 'Unknown Observer'}</p>
          <span>{observer ? `ID: ${observer.observer_id.slice(0, 8)}...` : 'Not logged in'}</span>
        </div>
        
        <button className="btn btn-danger btn-shift-end" onClick={() => handleShiftEnd(observer, navigate)}>
          SHIFT END
        </button>
          <span>{observer ? `ID: ${String(observer.observer_id).slice(0, 8)}...` : 'Not logged in'}</span>
        <div className="sidebar-terminal-trigger">
          {'>'}_ Forensic Echo
        </div>
      </div>
    </aside>
  )
}
