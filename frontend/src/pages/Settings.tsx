import { useEffect, useState } from 'react'
import React from 'react'
import { useVersion } from '../hooks/useVersion'
import { useSession } from '../context/SessionContext'
import { supabase } from '../lib/supabase'

interface ConfigRow {
  config_key: number
  config_name: string
  config_value: string | null
  description: string | null
  modified_at: string | null
}

interface SpeciesRow {
  species_id: number
  common_name: string
  scientific_name: string
  species_code: string
  is_deleted: boolean
}

interface StageRow {
  stage_id: number
  label: string
  description: string | null
  ordinal_rank: number
  egg_stage_code: string | null
  is_deleted: boolean
}

interface BioPropRow {
  property_id: number
  property_label: string
  data_type: string | null
  stage_id: number | null
  is_critical: boolean
  is_deleted: boolean
}

interface ObserverRow {
  observer_id: number
  display_name: string
  is_active: boolean
}

type LookupTab = 'species' | 'stages' | 'bio-props' | 'observers'

const TAB_LABELS: Record<LookupTab, string> = {
  'species': '🐢 Species Management',
  'stages': '📋 Development Stages',
  'bio-props': '🧬 Biological Properties',
  'observers': '👤 Observers',
}

export default function Settings() {
  const versionHook = useVersion()
  const { observer } = useSession()

  // System config state
  const [configs, setConfigs] = useState<ConfigRow[]>([])
  const [loading, setLoading] = useState(true)

  // Lookup CRUD state
  const [activeTab, setActiveTab] = useState<LookupTab>('species')
  const [midSeasonLockout, setMidSeasonLockout] = useState(false)
  const [lockoutChecked, setLockoutChecked] = useState(false)

  // Lookup data
  const [speciesRows, setSpeciesRows] = useState<SpeciesRow[]>([])
  const [stageRows, setStageRows] = useState<StageRow[]>([])
  const [bioPropRows, setBioPropRows] = useState<BioPropRow[]>([])
  const [observerRows, setObserverRows] = useState<ObserverRow[]>([])
  const [tableLoading, setTableLoading] = useState(false)

  // CRUD modal state
  const [modalOpen, setModalOpen] = useState(false)
  const [editRow, setEditRow] = useState<any>(null) // existing row or null for new
  const [deleteConfirm, setDeleteConfirm] = useState<any>(null)
  const [deleteTable, setDeleteTable] = useState<string>('')
  const [saving, setSaving] = useState(false)

  // Check mid-season lockout on mount
  useEffect(() => {
    async function checkLockout() {
      try {
        const { count, error } = await supabase
          .from('egg')
          .select('*', { count: 'exact', head: true })
          .eq('status', 'Active')
          .eq('is_deleted', false)
        if (!error && count !== null) {
          setMidSeasonLockout(count > 0)
        }
      } catch (err) {
        console.error('Lockout check failed:', err)
      } finally {
        setLockoutChecked(true)
      }
    }
    checkLockout()
  }, [])

  // System config fetch
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

  // Fetch lookup table data when tab changes
  const fetchLookupData = async (tab: LookupTab) => {
    setTableLoading(true)
    try {
      switch (tab) {
        case 'species': {
          const { data } = await supabase
            .from('species')
            .select('*')
            .eq('is_deleted', false)
            .order('species_code')
          setSpeciesRows(data || [])
          break
        }
        case 'stages': {
          const { data } = await supabase
            .from('development_stage')
            .select('*')
            .eq('is_deleted', false)
            .order('ordinal_rank')
          setStageRows(data || [])
          break
        }
        case 'bio-props': {
          const { data } = await supabase
            .from('biological_property')
            .select('*')
            .eq('is_deleted', false)
            .order('property_label')
          setBioPropRows(data || [])
          break
        }
        case 'observers': {
          const { data } = await supabase
            .from('observer')
            .select('*')
            .eq('is_active', true)
            .order('display_name')
          setObserverRows(data || [])
          break
        }
      }
    } catch (err) {
      console.error(`Failed to fetch ${tab}:`, err)
    } finally {
      setTableLoading(false)
    }
  }

  useEffect(() => {
    fetchLookupData(activeTab)
  }, [activeTab])

  // Soft-delete handler
  const handleSoftDelete = async () => {
    if (!deleteConfirm || !deleteTable) return
    setSaving(true)
    try {
      if (deleteTable === 'observer') {
        // Observer uses is_active instead of is_deleted
        await supabase
          .from('observer')
          .update({ is_active: false, modified_at: new Date().toISOString() })
          .eq('observer_id', deleteConfirm.observer_id)
      } else {
        const table = deleteTable as 'species' | 'development_stage' | 'biological_property'
        const pkMap: Record<string, string> = {
          species: 'species_id',
          development_stage: 'stage_id',
          biological_property: 'property_id',
        }
        const pkCol = pkMap[table]
        const pkVal = deleteConfirm[pkCol]
        await supabase
          .from(table)
          .update({ is_deleted: true, modified_at: new Date().toISOString() })
          .eq(pkCol, pkVal)
      }

      // Log to system_log
      const sessionId = observer?.session_id || null
      if (sessionId) {
        await supabase.from('system_log').insert({
          event_type: 'SOFT_DELETE',
          event_message: `Soft-deleted row from ${deleteTable}: ${JSON.stringify(deleteConfirm)}`,
          session_id: sessionId,
        })
      }

      setDeleteConfirm(null)
      setDeleteTable('')
      fetchLookupData(activeTab)
    } catch (err) {
      console.error('Soft-delete failed:', err)
      alert('Failed to delete. Check console for details.')
    } finally {
      setSaving(false)
    }
  }

  // Save handler (create or update)
  const handleSave = async (formData: any) => {
    setSaving(true)
    try {
      const sessionId = observer?.session_id || null

      // Observer uses is_active; other tables use is_deleted
      switch (activeTab) {
        case 'species': {
          const payload = {
            common_name: formData.common_name,
            scientific_name: formData.scientific_name,
            species_code: formData.species_code,
            modified_at: new Date().toISOString(),
          }
          if (editRow) {
            await supabase.from('species').update(payload).eq('species_id', editRow.species_id)
          } else {
            await supabase.from('species').insert({ ...payload, created_at: new Date().toISOString() })
          }
          break
        }
        case 'stages': {
          const payload = {
            label: formData.label,
            description: formData.description || null,
            ordinal_rank: formData.ordinal_rank,
            egg_stage_code: formData.egg_stage_code || null,
            modified_at: new Date().toISOString(),
          }
          if (editRow) {
            await supabase.from('development_stage').update(payload).eq('stage_id', editRow.stage_id)
          } else {
            await supabase.from('development_stage').insert({ ...payload, created_at: new Date().toISOString() })
          }
          break
        }
        case 'bio-props': {
          const payload = {
            property_label: formData.property_label,
            data_type: formData.data_type || null,
            stage_id: formData.stage_id || null,
            is_critical: formData.is_critical || false,
            modified_at: new Date().toISOString(),
          }
          if (editRow) {
            await supabase.from('biological_property').update(payload).eq('property_id', editRow.property_id)
          } else {
            await supabase.from('biological_property').insert({ ...payload, created_at: new Date().toISOString() })
          }
          break
        }
        case 'observers': {
          const payload = {
            display_name: formData.display_name,
            modified_at: new Date().toISOString(),
          }
          if (editRow) {
            await supabase.from('observer').update(payload).eq('observer_id', editRow.observer_id)
          } else {
            await supabase.from('observer').insert({
              ...payload,
              is_active: true,
              created_at: new Date().toISOString(),
            })
          }
          break
        }
      }

      if (sessionId) {
        await supabase.from('system_log').insert({
          event_type: editRow ? 'UPDATE' : 'CREATE',
          event_message: `${editRow ? 'Updated' : 'Created'} row in ${activeTab}`,
          session_id: sessionId,
        })
      }

      setModalOpen(false)
      setEditRow(null)
      fetchLookupData(activeTab)
    } catch (err) {
      console.error('Save failed:', err)
      alert('Failed to save. Check console for details.')
    } finally {
      setSaving(false)
    }
  }

  // Render CRUD section
  const renderCrudTable = () => {
    if (!lockoutChecked) {
      return <p>🐢 Checking mid-season status...</p>
    }

    const isLocked = midSeasonLockout

    const openAdd = () => {
      setEditRow(null)
      setModalOpen(true)
    }

    const openEdit = (row: any) => {
      setEditRow(row)
      setModalOpen(true)
    }

    const openDelete = (row: any, table: LookupTab) => {
      const realTable = table === 'bio-props' ? 'biological_property' :
        table === 'stages' ? 'development_stage' :
        table === 'observers' ? 'observer' : 'species'
      setDeleteConfirm(row)
      setDeleteTable(realTable)
    }

    const renderRows = () => {
      switch (activeTab) {
        case 'species':
          return speciesRows.map(row => (
            <tr key={row.species_id}>
              <td>{row.species_code}</td>
              <td>{row.common_name}</td>
              <td><em>{row.scientific_name}</em></td>
              <td className="actions-cell">
                <button className="btn-icon" onClick={() => openEdit(row)} disabled={isLocked} title="Edit">✏️</button>
                <button className="btn-icon" onClick={() => openDelete(row, 'species')} disabled={isLocked} title="Delete">🗑️</button>
              </td>
            </tr>
          ))
        case 'stages':
          return stageRows.map(row => (
            <tr key={row.stage_id}>
              <td>{row.ordinal_rank}</td>
              <td>{row.label}</td>
              <td>{row.egg_stage_code || '—'}</td>
              <td>{row.description || '—'}</td>
              <td className="actions-cell">
                <button className="btn-icon" onClick={() => openEdit(row)} disabled={isLocked} title="Edit">✏️</button>
                <button className="btn-icon" onClick={() => openDelete(row, 'stages')} disabled={isLocked} title="Delete">🗑️</button>
              </td>
            </tr>
          ))
        case 'bio-props':
          return bioPropRows.map(row => (
            <tr key={row.property_id}>
              <td>{row.property_label}</td>
              <td><code>{row.data_type || '—'}</code></td>
              <td>{row.stage_id || '—'}</td>
              <td>{row.is_critical ? '⚠️ Critical' : '—'}</td>
              <td className="actions-cell">
                <button className="btn-icon" onClick={() => openEdit(row)} disabled={isLocked} title="Edit">✏️</button>
                <button className="btn-icon" onClick={() => openDelete(row, 'bio-props')} disabled={isLocked} title="Delete">🗑️</button>
              </td>
            </tr>
          ))
        case 'observers':
          return observerRows.map(row => (
            <tr key={row.observer_id}>
              <td>{row.display_name}</td>
              <td>{row.is_active ? '✅ Active' : '❌ Inactive'}</td>
              <td className="actions-cell">
                <button className="btn-icon" onClick={() => openEdit(row)} disabled={isLocked} title="Edit">✏️</button>
                <button className="btn-icon" onClick={() => openDelete(row, 'observers')} disabled={isLocked} title="Deactivate">🗑️</button>
              </td>
            </tr>
          ))
      }
    }

    const renderTableHeader = () => {
      switch (activeTab) {
        case 'species':
          return (
            <tr>
              <th>Code</th>
              <th>Common Name</th>
              <th>Scientific Name</th>
              <th>Actions</th>
            </tr>
          )
        case 'stages':
          return (
            <tr>
              <th>Rank</th>
              <th>Label</th>
              <th>Egg Stage Code</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          )
        case 'bio-props':
          return (
            <tr>
              <th>Property Label</th>
              <th>Data Type</th>
              <th>Stage Id</th>
              <th>Critical</th>
              <th>Actions</th>
            </tr>
          )
        case 'observers':
          return (
            <tr>
              <th>Display Name</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          )
      }
    }

    const renderEmptyMessage = () => {
      const messages: Record<LookupTab, string> = {
        'species': 'No species defined. Click ➕ to add the first one.',
        'stages': 'No development stages defined. Click ➕ to add the first one.',
        'bio-props': 'No biological properties defined. Click ➕ to add the first one.',
        'observers': 'No active observers. Click ➕ to add the first one.',
      }
      return messages[activeTab]
    }

    const getRowCount = () => {
      switch (activeTab) {
        case 'species': return speciesRows.length
        case 'stages': return stageRows.length
        case 'bio-props': return bioPropRows.length
        case 'observers': return observerRows.length
      }
    }

    return (
      <>
        {isLocked && (
          <div className="lockout-banner">
            🔒 MID-SEASON LOCKOUT ACTIVE — Lookup table modifications are disabled while active eggs exist in the system.
          </div>
        )}

        <div className="crud-toolbar">
          <span className="row-count">{getRowCount()} row(s)</span>
          <button className="btn-add" onClick={openAdd} disabled={isLocked}>➕ ADD</button>
        </div>

        {tableLoading ? (
          <p>🐢 Loading data...</p>
        ) : getRowCount() === 0 ? (
          <p className="empty-message">{renderEmptyMessage()}</p>
        ) : (
          <table className="config-table lookup-table">
            <thead>{renderTableHeader()}</thead>
            <tbody>{renderRows()}</tbody>
          </table>
        )}
      </>
    )
  }

  // Render modal form for add/edit
  const renderModal = () => {
    if (!modalOpen) return null

    const isEdit = editRow !== null

    const renderFields = () => {
      switch (activeTab) {
        case 'species':
          return (
            <>
              <label>Common Name <input name="common_name" defaultValue={editRow?.common_name || ''} required /></label>
              <label>Scientific Name <input name="scientific_name" defaultValue={editRow?.scientific_name || ''} required /></label>
              <label>Species Code <input name="species_code" defaultValue={editRow?.species_code || ''} required maxLength={4} /></label>
            </>
          )
        case 'stages':
          return (
            <>
              <label>Label <input name="label" defaultValue={editRow?.label || ''} required /></label>
              <label>Ordinal Rank <input name="ordinal_rank" type="number" defaultValue={editRow?.ordinal_rank ?? ''} required /></label>
              <label>Egg Stage Code <input name="egg_stage_code" defaultValue={editRow?.egg_stage_code || ''} /></label>
              <label>Description <textarea name="description" defaultValue={editRow?.description || ''} rows={3} /></label>
            </>
          )
        case 'bio-props':
          return (
            <>
              <label>Property Label <input name="property_label" defaultValue={editRow?.property_label || ''} required /></label>
              <label>Data Type <input name="data_type" defaultValue={editRow?.data_type || ''} placeholder="e.g. numeric, text, boolean" /></label>
              <label>Stage Id <input name="stage_id" type="number" defaultValue={editRow?.stage_id ?? ''} /></label>
              <label className="checkbox-label">
                <input name="is_critical" type="checkbox" defaultChecked={editRow?.is_critical || false} />
                Is Critical
              </label>
            </>
          )
        case 'observers':
          return (
            <>
              <label>Display Name <input name="display_name" defaultValue={editRow?.display_name || ''} required /></label>
            </>
          )
      }
    }

    const handleFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault()
      const form = e.currentTarget
      const formData: any = {}
      const inputs = form.querySelectorAll('input, textarea, select')
      inputs.forEach((input: any) => {
        if (input.type === 'checkbox') {
          formData[input.name] = input.checked
        } else if (input.name) {
          formData[input.name] = input.value
        }
      })
      handleSave(formData)
    }

    return (
      <div className="modal-overlay" onClick={() => { setModalOpen(false); setEditRow(null) }}>
        <div className="modal-content" onClick={e => e.stopPropagation()}>
          <h3>{isEdit ? '✏️ Edit' : '➕ Add'} {TAB_LABELS[activeTab].replace(/^[^ ]+ /, '')}</h3>
          <form onSubmit={handleFormSubmit}>
            {renderFields()}
            <div className="form-actions">
              <button type="submit" className="btn-save" disabled={saving}>
                {saving ? '🐢 Saving...' : 'SAVE'}
              </button>
              <button type="button" className="btn-cancel" onClick={() => { setModalOpen(false); setEditRow(null) }}>
                CANCEL
              </button>
            </div>
          </form>
        </div>
      </div>
    )
  }

  // Render delete confirmation dialog
  const renderDeleteConfirm = () => {
    if (!deleteConfirm) return null

    const getLabel = () => {
      if (deleteTable === 'observer') return deleteConfirm.display_name
      if (deleteTable === 'species') return deleteConfirm.common_name || deleteConfirm.species_code
      if (deleteTable === 'development_stage') return deleteConfirm.label
      if (deleteTable === 'biological_property') return deleteConfirm.property_label
      return JSON.stringify(deleteConfirm)
    }

    return (
      <div className="modal-overlay" onClick={() => { setDeleteConfirm(null); setDeleteTable('') }}>
        <div className="modal-content modal-confirm" onClick={e => e.stopPropagation()}>
          <h3>🗑️ Confirm Soft Delete</h3>
          <p>Are you sure you want to soft-delete <strong>{getLabel()}</strong> from <code>{deleteTable}</code>?</p>
          <p className="muted">This action uses soft-delete (is_deleted = true) and can be reversed by an administrator.</p>
          <div className="form-actions">
            <button className="btn-save btn-danger" onClick={handleSoftDelete} disabled={saving}>
              {saving ? '🐢 Deleting...' : 'DELETE'}
            </button>
            <button className="btn-cancel" onClick={() => { setDeleteConfirm(null); setDeleteTable('') }}>
              CANCEL
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="page settings-page">
      <h1>⚙️ System Settings</h1>
      <p className="version-info">System Version: <strong>{versionHook}</strong></p>

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

      {/* Lookup Table CRUD Section */}
      <section className="card lookup-crud-section">
        <h2>📚 Lookup Table Management</h2>
        <div className="lookup-tabs">
          {(Object.keys(TAB_LABELS) as LookupTab[]).map(tab => (
            <button
              key={tab}
              className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {TAB_LABELS[tab]}
            </button>
          ))}
        </div>
        <div className="lookup-content">
          {renderCrudTable()}
        </div>
      </section>

      {renderModal()}
      {renderDeleteConfirm()}
    </div>
  )
}
