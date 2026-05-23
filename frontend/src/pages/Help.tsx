import { useVersion } from '../hooks/useVersion'

export default function Help() {
  const version = useVersion()

  return (
    <div className="page help-page">
      <h1>📚 Operator Help & Reference</h1>
      <p className="version-info">System Version: <strong>{version}</strong></p>

      <section className="card">
        <h2>🔄 Biological Stage Reference</h2>
        <table className="stage-table">
          <thead>
            <tr><th>Stage</th><th>Code</th><th>Description</th></tr>
          </thead>
          <tbody>
            <tr><td>S0</td><td>Intake</td><td>Egg received, initial assessment, bin assignment</td></tr>
            <tr><td>S1</td><td>Early Development</td><td>Embryo attachment visible, temperature stabilization</td></tr>
            <tr><td>S2</td><td>Organogenesis</td><td>Major organ formation, increased sensitivity</td></tr>
            <tr><td>S3</td><td>Growth Phase</td><td>Rapid growth, shell calcification begins</td></tr>
            <tr><td>S4</td><td>Late Development</td><td>Full organ maturation, pre-hatch positioning</td></tr>
            <tr><td>S5</td><td>Pre-Hatch</td><td>Internal pipping, yolk absorption final stage</td></tr>
            <tr><td>S6</td><td>Hatchling Transfer</td><td>Hatched, transferred to hatchling care facility</td></tr>
          </tbody>
        </table>
      </section>

      <section className="card">
        <h2>📐 Biological Property Scales</h2>
        <table className="scale-table">
          <thead>
            <tr><th>Property</th><th>Scale</th><th>Values</th></tr>
          </thead>
          <tbody>
            <tr><td>Chalking</td><td>0–2</td><td>0=None, 1=Minor, 2=Severe</td></tr>
            <tr><td>Molding</td><td>0–3</td><td>0=None, 1=Trace, 2=Moderate, 3=Severe</td></tr>
            <tr><td>Leaking</td><td>0–3</td><td>0=None, 1=Trace, 2=Moderate, 3=Severe</td></tr>
            <tr><td>Denting</td><td>0–3</td><td>0=None, 1=Minor, 2=Moderate, 3=Collapsed</td></tr>
            <tr><td>Vascularity</td><td>Boolean</td><td>Yes/No — visible blood vessels</td></tr>
          </tbody>
        </table>
      </section>

      <section className="card">
        <h2>🔍 Observations Workflow</h2>
        <ol className="workflow-list">
          <li>Select an active <strong>Bin</strong> from the Observations page</li>
          <li>Select one or more <strong>Eggs</strong> for batch observation</li>
          <li>Set the <strong>Stage</strong> and <strong>Status</strong> for all selected eggs</li>
          <li>Evaluate each <strong>Biological Property</strong> on the matrix</li>
          <li>Click <strong>SAVE OBSERVATIONS</strong> to commit to the clinical record</li>
          <li>Verify the saved observation appears in the egg history</li>
        </ol>
      </section>

      <section className="card">
        <h2>⚠️ Clinical Alerts</h2>
        <ul className="alert-list">
          <li>🔴 <strong>Molding ≥ 2:</strong> Requires immediate antifungal intervention</li>
          <li>🟡 <strong>Leaking ≥ 2:</strong> Shell integrity compromised, isolate bin</li>
          <li>🟠 <strong>Chalking ≥ 2:</strong> Severe dehydration, adjust humidity protocol</li>
          <li>⚪ <strong>Denting ≥ 2:</strong> Osmotic imbalance, check substrate moisture</li>
        </ul>
      </section>
    </div>
  )
}
