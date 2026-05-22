import { useEffect, useState } from 'react'
import { useVersion } from '../hooks/useVersion'
import { supabase } from '../lib/supabase'

interface SystemStatus {
  version: string
  dbConnected: boolean | null
  dbResponseTime: number | null
  migrationCount: number
  tableCount: number
}

export default function SystemCheck() {
  const version = useVersion()
  const [status, setStatus] = useState<SystemStatus>({
    version: '',
    dbConnected: null,
    dbResponseTime: null,
    migrationCount: 0,
    tableCount: 0
  })

  useEffect(() => {
    async function checkHealth() {
      const start = performance.now()
      try {
        const { data: configData, error } = await supabase
          .from('system_config')
          .select('config_value')
          .eq('config_name', 'APP_VERSION')
          .single()

        const responseTime = Math.round(performance.now() - start)

        if (error) {
          setStatus(s => ({ ...s, dbConnected: false, dbResponseTime: null }))
          return
        }

        // Count tables via system_config as proxy
        const { data: tables } = await supabase
          .from('system_config')
          .select('config_key')

        setStatus({
          version: configData?.config_value || version,
          dbConnected: true,
          dbResponseTime: responseTime,
          migrationCount: 1, // placeholder
          tableCount: tables?.length || 0
        })
      } catch {
        setStatus(s => ({ ...s, dbConnected: false, dbResponseTime: null }))
      }
    }
    checkHealth()
  }, [version])

  return (
    <div className="page system-check-page">
      <h1>🩺 System Health Check</h1>

      <section className="card">
        <h2>📊 Status Overview</h2>
        <table className="status-table">
          <tbody>
            <tr>
              <td>System Version</td>
              <td><strong>{status.version || version}</strong></td>
            </tr>
            <tr>
              <td>Database Connection</td>
              <td>
                {status.dbConnected === null ? '⏳ Checking...' :
                 status.dbConnected ? '✅ Connected' : '❌ Failed'}
              </td>
            </tr>
            <tr>
              <td>Response Time</td>
              <td>
                {status.dbResponseTime !== null 
                  ? `${status.dbResponseTime}ms` 
                  : '—'}
              </td>
            </tr>
            <tr>
              <td>Configuration Keys</td>
              <td>{status.tableCount}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="card">
        <h2>🔧 Required Services</h2>
        <ul className="checklist">
          <li>✅ Supabase Project: turtle-db</li>
          <li>✅ API: Port 54321 (local) / Production endpoint</li>
          <li>✅ Database: PostgreSQL 15+</li>
          <li>✅ Migrations: v8.1.x through v9.7.0</li>
          <li>✅ Row Level Security: Enabled (v9.7.0)</li>
        </ul>
      </section>

      <section className="card">
        <h2>📋 Migration History</h2>
        <table className="migration-table">
          <thead>
            <tr><th>Version</th><th>Description</th></tr>
          </thead>
          <tbody>
            <tr><td>v9.7.0</td><td>Enable RLS on all clinical tables</td></tr>
            <tr><td>v9.6.6</td><td>React frontend resurrection</td></tr>
            <tr><td>v9.1.x</td><td>Numeric PK migration</td></tr>
            <tr><td>v8.x</td><td>Enterprise schema consolidation</td></tr>
          </tbody>
        </table>
      </section>
    </div>
  )
}
