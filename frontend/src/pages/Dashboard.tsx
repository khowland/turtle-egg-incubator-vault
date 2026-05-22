import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { useSession } from '../context/SessionContext'

interface KPI {
  activeCount: number
  hatchedCount: number
  deadCount: number
  alertCount: number
}

interface StageOutcome {
  stage: string
  active: number
  dead: number
  transferred: number
  total: number
}

interface LogEntry {
  system_log_id: number
  timestamp: string
  event_type: string
  event_message: string
}

export default function Dashboard() {
  const { observer } = useSession()
  const [kpis, setKpis] = useState<KPI>({ activeCount: 0, hatchedCount: 0, deadCount: 0, alertCount: 0 })
  const [stageOutcomes, setStageOutcomes] = useState<StageOutcome[]>([])
  const [activityFeed, setActivityFeed] = useState<LogEntry[]>([])

  async function fetchKPIs() {
    try {
      // Get active bins
      const { data: bins } = await supabase.from('bin').select('bin_id').eq('is_deleted', false)
      const activeBinIds = bins?.map((b: any) => b.bin_id) || []

      if (activeBinIds.length === 0) {
        setKpis({ activeCount: 0, hatchedCount: 0, deadCount: 0, alertCount: 0 })
        return
      }

      // Counts
      const { count: active } = await supabase.from('egg').select('*', { count: 'exact', head: true }).eq('status', 'Active').eq('is_deleted', false).in('bin_id', activeBinIds)
      const { count: hatched } = await supabase.from('egg').select('*', { count: 'exact', head: true }).eq('status', 'Transferred').eq('is_deleted', false).in('bin_id', activeBinIds)
      const { count: dead } = await supabase.from('egg').select('*', { count: 'exact', head: true }).eq('status', 'Dead').eq('is_deleted', false).in('bin_id', activeBinIds)

      // Alerts (molding > 0 or leaking > 0)
      const { count: alerts } = await supabase.from('egg_observation').select('*', { count: 'exact', head: true }).in('bin_id', activeBinIds).or('molding.gt.0,leaking.gt.0')

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

  async function fetchStageOutcomes() {
    try {
      const { data, error } = await supabase
        .from('egg')
        .select('current_stage, status')
        .eq('is_deleted', false)

      if (error) {
        console.error('Stage fetch error:', error)
        return
      }

      if (!data || data.length === 0) {
        setStageOutcomes([])
        return
      }

      // Aggregate by stage
      const stageMap: Record<string, { active: number; dead: number; transferred: number }> = {}
      ;(data as any[]).forEach((egg) => {
        const stage = egg.current_stage || 'Unknown'
        if (!stageMap[stage]) {
          stageMap[stage] = { active: 0, dead: 0, transferred: 0 }
        }
        const status = egg.status?.toLowerCase()
        if (status === 'active') {
          stageMap[stage].active++
        } else if (status === 'dead') {
          stageMap[stage].dead++
        } else if (status === 'transferred') {
          stageMap[stage].transferred++
        }
      })

      const outcomes: StageOutcome[] = Object.entries(stageMap).map(([stage, counts]) => ({
        stage,
        active: counts.active,
        dead: counts.dead,
        transferred: counts.transferred,
        total: counts.active + counts.dead + counts.transferred
      }))

      // Sort by stage
      outcomes.sort((a, b) => a.stage.localeCompare(b.stage))

      setStageOutcomes(outcomes)
    } catch (err) {
      console.error('Stage outcome fetch error:', err)
    }
  }

  async function fetchActivityFeed() {
    try {
      const { data, error } = await supabase
        .from('system_log')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(8)

      if (error) {
        console.error('Activity feed error:', error)
        return
      }

      if (!data || data.length === 0) {
        setActivityFeed([])
        return
      }

      setActivityFeed(data as LogEntry[])
    } catch (err) {
      console.error('Activity feed fetch error:', err)
    }
  }

  function formatTimestamp(ts: string): string {
    try {
      const d = new Date(ts)
      return d.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return ts
    }
  }

  useEffect(() => {
    fetchKPIs()
    fetchStageOutcomes()
    fetchActivityFeed()
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
            {stageOutcomes.length === 0 ? (
              <p className="info-text">No egg data available — mortality heatmap will populate after intake.</p>
            ) : (
              <table className="heatmap-table">
                <thead>
                  <tr>
                    <th>Stage</th>
                    <th>Active</th>
                    <th>Dead</th>
                    <th>Transferred</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {stageOutcomes.map((row) => (
                    <tr key={row.stage} className={row.dead > 0 ? 'has-mortality' : ''}>
                      <td>{row.stage}</td>
                      <td>{row.active}</td>
                      <td className={row.dead > 0 ? 'text-danger' : ''}>{row.dead}</td>
                      <td>{row.transferred}</td>
                      <td><strong>{row.total}</strong></td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td><strong>Total</strong></td>
                    <td><strong>{stageOutcomes.reduce((sum, r) => sum + r.active, 0)}</strong></td>
                    <td className={stageOutcomes.reduce((sum, r) => sum + r.dead, 0) > 0 ? 'text-danger' : ''}>
                      <strong>{stageOutcomes.reduce((sum, r) => sum + r.dead, 0)}</strong>
                    </td>
                    <td><strong>{stageOutcomes.reduce((sum, r) => sum + r.transferred, 0)}</strong></td>
                    <td><strong>{stageOutcomes.reduce((sum, r) => sum + r.total, 0)}</strong></td>
                  </tr>
                </tfoot>
              </table>
            )}
          </div>
        </section>

        <section className="activity-section">
          <h2>📜 Recent Vault Activity</h2>
          {activityFeed.length === 0 ? (
            <p className="info-text">No recent activity</p>
          ) : (
            <ul className="activity-feed">
              {activityFeed.map((entry) => (
                <li key={entry.system_log_id} className="activity-entry">
                  <span className="activity-time">{formatTimestamp(entry.timestamp)}</span>
                  <span className="activity-type">{entry.event_type}</span>
                  <span className="activity-message">{entry.event_message}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}
