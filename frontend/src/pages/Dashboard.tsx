import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { useSession } from '../context/SessionContext'

interface KPI {
  activeCount: number
  hatchedCount: number
  deadCount: number
  alertCount: number
}

export default function Dashboard() {
  const { observer } = useSession()
  const [kpis, setKpis] = useState<KPI>({ activeCount: 0, hatchedCount: 0, deadCount: 0, alertCount: 0 })

  async function fetchKPIs() {
    const sos = supabase as any
    try {
      // Get active bins
      const { data: bins } = await sos.table('bin').select('bin_id').eq('is_deleted', false)
      const activeBinIds = bins?.map((b: any) => b.bin_id) || []

      if (activeBinIds.length === 0) {
        setKpis({ activeCount: 0, hatchedCount: 0, deadCount: 0, alertCount: 0 })
        return
      }

      // Counts
      const { count: active } = await sos.table('egg').select('*', { count: 'exact', head: true }).eq('status', 'Active').eq('is_deleted', false).in('bin_id', activeBinIds)
      const { count: hatched } = await sos.table('egg').select('*', { count: 'exact', head: true }).eq('status', 'Transferred').eq('is_deleted', false).in('bin_id', activeBinIds)
      const { count: dead } = await sos.table('egg').select('*', { count: 'exact', head: true }).eq('status', 'Dead').eq('is_deleted', false).in('bin_id', activeBinIds)
      
      // Alerts (molding > 0 or leaking > 0)
      const { count: alerts } = await sos.table('egg_observation').select('*', { count: 'exact', head: true }).in('bin_id', activeBinIds).or('molding.gt.0,leaking.gt.0')

      setKpis({
        activeCount: active || 0,
        hatchedCount: hatched || 0,
        deadCount: dead || 0,
        alertCount: alerts || 0
      })
    } catch (err) {
      console.error('KPI fetch error:', err)
    }
  }

  useEffect(() => {
    fetchKPIs()
  }, [])

  return (
    <div className="dashboard-container">
      <header>
        <h1>Today's Summary</h1>
        <p className="welcome-text">Session active: {observer?.observer_name}</p>
      </header>

      <section className="metrics-grid">
        <div className="metric-card">
          <label>Still Incubating</label>
          <div className="value">{kpis.activeCount}</div>
          <span className="subtext">Active</span>
        </div>
        <div className="metric-card">
          <label>Deceased / Nonviable</label>
          <div className="value">{kpis.deadCount}</div>
          <span className="subtext">Season Total</span>
        </div>
        <div className="metric-card">
          <label>Hatched / Transferred</label>
          <div className="value">{kpis.hatchedCount}</div>
          <span className="subtext">Season Total</span>
        </div>
        <div className={`metric-card ${kpis.alertCount > 0 ? 'alert' : ''}`}>
          <label>Help Needed</label>
          <div className="value">{kpis.alertCount}</div>
          <span className="subtext">{kpis.alertCount > 0 ? 'Alerts' : 'All Good'}</span>
        </div>
      </section>

      <div className="dashboard-layout">
        <section className="chart-section">
          <h2>🔥 Mortality Heatmap (§5.47)</h2>
          <div className="chart-placeholder">
            {/* Recharts implementation would go here */}
            {kpis.deadCount === 0 ? <p className="success-text">No mortalities recorded this season!</p> : <p>Loading mortality data...</p>}
          </div>
        </section>

        <section className="activity-section">
          <h2>📜 Recent Vault Activity</h2>
          {/* Add Activity List component */}
          <p className="info-text">system_log monitoring active...</p>
        </section>
      </div>
    </div>
  )
}
