import { useVersion } from '../hooks/useVersion'

export default function Reports() {
  const version = useVersion()

  return (
    <div className="page reports-page">
      <h1>📈 Reports & Analytics</h1>
      <p className="version-info">System Version: <strong>{version}</strong></p>

      <section className="card">
        <h2>📊 Available Reports</h2>
        <p>The following clinical reports are available for generation:</p>
        <div className="report-grid">
          <div className="report-card">
            <h3>🥚 Hatch Rate Analysis</h3>
            <p>Calculate hatch success rates by species, intake batch, or incubation bin. Includes temporal trends and seasonal analysis.</p>
            <span className="badge badge-pending">Pending Port</span>
          </div>
          <div className="report-card">
            <h3>🕐 Incubation Duration Report</h3>
            <p>Analyze average incubation duration by species and stage progression. Compare against expected ranges per biological reference.</p>
            <span className="badge badge-pending">Pending Port</span>
          </div>
          <div className="report-card">
            <h3>⚖️ Weight Tracking</h3>
            <p>Monitor bin weight changes over time, water addition tracking, and moisture deficit logs for environmental control.</p>
            <span className="badge badge-pending">Pending Port</span>
          </div>
          <div className="report-card">
            <h3>🩺 Clinical Property Trends</h3>
            <p>Track molding, chalking, leaking, denting, and vascularity observations across all active bins and eggs.</p>
            <span className="badge badge-pending">Pending Port</span>
          </div>
          <div className="report-card">
            <h3>📋 Hatchling Ledger Export</h3>
            <p>Export hatchling records with vitality scores, incubation duration, and transfer details for external reporting.</p>
            <span className="badge badge-pending">Pending Port</span>
          </div>
          <div className="report-card">
            <h3>🔍 Clinical Audit Trail</h3>
            <p>Complete forensic audit of all observations, modifications, deletions, and session events with cryptographic trace IDs.</p>
            <span className="badge badge-pending">Pending Port</span>
          </div>
        </div>
      </section>

      <section className="card">
        <h2>⏳ Report Generation Status</h2>
        <p>
          These reports are currently available via the <strong>Streamlit backend</strong> (<code>vault_views/6_Reports.py</code>).
          The React frontend report views are scheduled for a future sprint. For now, please use the Streamlit interface for
          full report generation capabilities.
        </p>
        <p style={{ marginTop: 10, color: 'var(--color-muted)' }}>
          Contact your system administrator to access the Streamlit dashboard at <code>http://localhost:8501</code>
        </p>
      </section>
    </div>
  )
}
