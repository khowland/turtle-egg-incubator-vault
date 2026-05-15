import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import { useSession } from '../context/SessionContext'

interface Egg {
  egg_id: string
  bin_id: number
  current_stage: string
  status: string
  last_chalk: number
  last_vasc: boolean
}

interface Bin {
  bin_id: number
  bin_code: string
}

export default function Observations() {
  const { observer } = useSession()
  const [bins, setBins] = useState<Bin[]>([])
  const [activeBinId, setActiveBinId] = useState<number | null>(null)
  const [eggs, setEggs] = useState<Egg[]>([])
  const [selectedEggIds, setSelectedEggIds] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  // Form State
  const [matrixStage, setMatrixStage] = useState('S1')
  const [matrixStatus, setMatrixStatus] = useState('Active')
  const [matrixChalking, setMatrixChalking] = useState(0)
  const [matrixMolding, setMatrixMolding] = useState(0)
  const [matrixLeaking, setMatrixLeaking] = useState(0)
  const [matrixDenting, setMatrixDenting] = useState(0)

  const fetchBins = useCallback(async () => {
    const { data } = await supabase.table('bin').select('bin_id, bin_code').eq('is_deleted', false)
    setBins(data || [])
    if (data && data.length > 0 && !activeBinId) setActiveBinId(data[0].bin_id)
  }, [activeBinId])

  const fetchEggs = useCallback(async (binId: number) => {
    setLoading(true)
    const { data } = await supabase.table('egg')
      .select('egg_id, bin_id, current_stage, status, last_chalk, last_vasc')
      .eq('bin_id', binId)
      .eq('status', 'Active')
      .eq('is_deleted', false)
    setEggs(data || [])
    setLoading(false)
  }, [])

  useEffect(() => { fetchBins() }, [fetchBins])
  useEffect(() => { if (activeBinId) fetchEggs(activeBinId) }, [activeBinId, fetchEggs])

  const toggleEggSelection = (id: string) => {
    setSelectedEggIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  const handleSave = async () => {
    if (selectedEggIds.length === 0) return
    
    // Batch commit logic (simplified for v9.6.6 React core)
    const promises = selectedEggIds.map(async (eggId) => {
      // 1. Create Observation
      await supabase.table('egg_observation').insert({
        egg_id: eggId,
        bin_id: activeBinId,
        session_id: observer?.session_id ?? 'SYSTEM',
        observer_id: observer?.observer_id ?? null,
        stage_at_observation: matrixStage,
        chalking: matrixChalking,
        molding: matrixMolding,
        leaking: matrixLeaking,
        denting: matrixDenting,
        status_at_observation: matrixStatus
      })

      // 2. Update Egg State
      await supabase.table('egg').update({
        current_stage: matrixStage,
        status: matrixStatus,
        last_chalk: matrixChalking,
        last_molding: matrixMolding,
        last_leaking: matrixLeaking,
        last_dented: matrixDenting
      }).eq('egg_id', eggId)
    })

    await Promise.all(promises)
    setSelectedEggIds([])
    if (activeBinId) fetchEggs(activeBinId)
    alert(`Successfully saved ${selectedEggIds.length} observations.`)
  }

  return (
    <div className="observations-container">
      <header>
        <h1>Observations</h1>
        <div className="bin-selector-card card">
          <label className="field-label">Current Bin Focus</label>
          <select value={activeBinId || ''} onChange={e => setActiveBinId(Number(e.target.value))}>
            {bins.map(b => <option key={b.bin_id} value={b.bin_id}>{b.bin_code}</option>)}
          </select>
        </div>
      </header>

      <section className="biological-grid">
        <h2>🥚 Biological Grid</h2>
        <div className="egg-cards">
          {loading ? <div className="spinner" /> : eggs.map(egg => (
            <div 
              key={egg.egg_id} 
              className={`egg-card ${selectedEggIds.includes(egg.egg_id) ? 'selected' : ''}`}
              onClick={() => toggleEggSelection(egg.egg_id)}
            >
              <div className="egg-icon">🥚</div>
              <div className="egg-id">{egg.egg_id.split('-E').pop()}</div>
              <div className="egg-stage">{egg.current_stage}</div>
            </div>
          ))}
        </div>
      </section>

      {selectedEggIds.length > 0 && (
        <section className="property-matrix card">
          <h3>📐 Property Matrix: [{selectedEggIds.length} Selected]</h3>
          <div className="matrix-grid">
            <div>
              <label className="field-label">Stage</label>
              <select value={matrixStage} onChange={e => setMatrixStage(e.target.value)}>
                {['S1', 'S2', 'S3', 'S4', 'S5', 'S6'].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="field-label">Status</label>
              <select value={matrixStatus} onChange={e => setMatrixStatus(e.target.value)}>
                {['Active', 'Transferred', 'Dead'].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
          <div className="matrix-scales">
            {/* Scales for Chalking, Molding, etc. */}
            <div>
              <label className="field-label">Molding (0-3)</label>
              <select value={matrixMolding} onChange={e => setMatrixMolding(Number(e.target.value))}>
                {[0, 1, 2, 3].map(n => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
            <div>
              <label className="field-label">Leaking (0-3)</label>
              <select value={matrixLeaking} onChange={e => setMatrixLeaking(Number(e.target.value))}>
                {[0, 1, 2, 3].map(n => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
          </div>
          <button className="btn btn-primary" style={{ width: '100%', marginTop: 20 }} onClick={handleSave}>
            SAVE OBSERVATIONS
          </button>
        </section>
      )}
    </div>
  )
}
