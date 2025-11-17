export default function Summary({ dataset }) {
  if (!dataset) return (
    <div className="card"><h2>Summary</h2><div>No dataset selected</div></div>
  )
  const s = dataset.summary || {}
  const averages = s.averages || {}
  const typeDist = s.type_distribution || {}
  const columns = s.columns || []
  const preview = s.preview || []

  return (
    <div className="card">
      <h2>Summary</h2>
      <div className="grid2">
        <div className="metric">
          <div className="metric-label">Total Count</div>
          <div className="metric-value">{s.total_count || 0}</div>
        </div>
      </div>
      <h3>Averages</h3>
      <table className="table">
        <thead><tr><th>Parameter</th><th>Average</th></tr></thead>
        <tbody>
          {Object.entries(averages).map(([k,v]) => (
            <tr key={k}><td>{k}</td><td>{v}</td></tr>
          ))}
        </tbody>
      </table>
      <h3>Type Distribution</h3>
      <table className="table">
        <thead><tr><th>Type</th><th>Count</th></tr></thead>
        <tbody>
          {Object.entries(typeDist).map(([k,v]) => (
            <tr key={k}><td>{k}</td><td>{v}</td></tr>
          ))}
        </tbody>
      </table>
      <h3>Preview</h3>
      <div className="table-scroll">
        <table className="table">
          <thead>
            <tr>
              {columns.map(c => <th key={c}>{c}</th>)}
            </tr>
          </thead>
          <tbody>
            {preview.map((row,i) => (
              <tr key={i}>
                {columns.map(c => <td key={c}>{row[c]}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
