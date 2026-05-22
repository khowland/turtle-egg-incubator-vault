import { useEffect, useState } from 'react'
import { useVersion } from '../hooks/useVersion'
import { supabase } from '../lib/supabase'

interface ConfigRow {
  config_key: number
  config_name: string
  config_value: string | null
  description: string | null
  modified_at: string | null
}

export default function Settings() {
  const version = useVersion()
  const [configs, setConfigs] = useState<ConfigRow[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchConfig() {
      try {
        const { data } = await supabase
          .from('system_config')
          .select('*')
          .order('config_key', { ascending: true })

        setConfigs(data || [])
      } catch (err) {
        console.error('Failed to fetch system config:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchConfig()
  }, [])

  return (
    <div className="page settings-page">
      <h1>⚙️ System Settings</h1>
      <p className="version-info">System Version: <strong>{version}</strong></p>

      <section className="card">
        <h2>🔧 System Configuration</h2>
        {loading ? (
          <p>⏳ Loading configuration...</p>
        ) : (
          <table className="config-table">
            <thead>
              <tr>
                <th>Key</th>
                <th>Name</th>
                <th>Value</th>
                <th>Description</th>
                <th>Last Modified</th>
              </tr>
            </thead>
            <tbody>
              {configs.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center' }}>
                    No configuration entries found.
                  </td>
                </tr>
              ) : (
                configs.map(cfg => (
                  <tr key={cfg.config_key}>
                    <td>{cfg.config_key}</td>
                    <td><code>{cfg.config_name}</code></td>
                    <td><strong>{cfg.config_value ?? '—'}</strong></td>
                    <td>{cfg.description || '—'}</td>
                    <td>
                      {cfg.modified_at
                        ? new Date(cfg.modified_at).toLocaleString()
                        : '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </section>

      <section className="card">
        <h2>📋 System Information</h2>
        <table className="info-table">
          <tbody>
            <tr>
              <td>React Version</td>
              <td>19.1.0</td>
            </tr>
            <tr>
              <td>Vite Version</td>
              <td>8.0.13</td>
            </tr>
            <tr>
              <td>Supabase Client</td>
              <td>@supabase/supabase-js</td>
            </tr>
            <tr>
              <td>Row Level Security</td>
              <td>✅ Enabled (v9.7.0)</td>
            </tr>
            <tr>
              <td>Streamlit Backend</td>
              <td>Available at localhost:8501</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="card">
        <h2>🔄 Sync Operations</h2>
        <p className="muted">
          The following management operations are available via the Streamlit backend 
          (<code>vault_views/7_Diagnostic.py</code>):
        </p>
        <ul className="sync-list">
          <li>🔄 Force Supabase Schema Refresh</li>
          <li>📊 Regenerate Performance Telemetry</li>
          <li>🧹 Purge Expired Session Tokens</li>
          <li>📋 Export System Audit Log</li>
          <li>💾 Create Database Backup Snapshot</li>
        </ul>
      </section>
    </div>
  )
}
