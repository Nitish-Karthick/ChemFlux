export default function Stats({ summary }) {
  const total = summary?.total_count ?? 0
  const averages = summary?.averages || {}
  function getAvg(keys) {
    const key = Object.keys(averages).find(k => keys.includes(k.toLowerCase()))
    return key ? averages[key] : null
  }
  const avgPressure = getAvg(['pressure'])
  const avgTemp = getAvg(['temperature', 'temp'])
  const avgFlow = getAvg(['flowrate', 'flow', 'flow rate'])

  return (
    <section className="section">
      <h2 className="section-title">Summary Statistics</h2>
      <div className="cards">
        <div className="card stat">
          <div className="label">Total Equipment Units</div>
          <div className="value xl">{total}</div>
          <div className="subtle">Latest dataset</div>
        </div>
        <div className="card stat">
          <div className="label">Average Pressure (PSI)</div>
          <div className="value xl">{avgPressure ?? '—'}</div>
          <div className="trend bad">± this period</div>
        </div>
        <div className="card stat">
          <div className="label">Mean Temperature (°C)</div>
          <div className="value xl">{avgTemp ?? '—'}</div>
          <div className="trend good">± this period</div>
        </div>
        <div className="card stat">
          <div className="label">Average Flow Rate</div>
          <div className="value xl">{avgFlow ?? '—'}</div>
          <div className="subtle">Across numeric rows</div>
        </div>
      </div>
    </section>
  )
}
