import { useMemo, useState } from 'react'
import { Bar, Pie } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend } from 'chart.js'
ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

function findColumn(columns = [], targets = []) {
  const lc = columns.map(c => c.toLowerCase())
  for (const t of targets) {
    const i = lc.indexOf(t)
    if (i !== -1) return columns[i]
  }
  // fuzzy contains
  for (const t of targets) {
    const i = lc.findIndex(c => c.includes(t))
    if (i !== -1) return columns[i]
  }
  return null
}

export default function Charts({ summary }) {
  if (!summary) return (
    <section className="section"><div className="card"><h2>Charts</h2><div>No dataset selected</div></div></section>
  )
  const [tab, setTab] = useState('pressure')
  const typeDist = summary.type_distribution || {}
  const columns = summary.columns || []
  const preview = summary.preview || []

  const colMap = {
    pressure: findColumn(columns, ['pressure', 'psi']),
    temperature: findColumn(columns, ['temperature', 'temp']),
    flowrate: findColumn(columns, ['flowrate', 'flow rate', 'flow'])
  }
  const labelCol = findColumn(columns, ['equipment name', 'name'])

  const distData = useMemo(() => {
    const key = colMap[tab]
    const labels = preview.map((row, idx) => labelCol ? String(row[labelCol]) : `Row ${idx + 1}`)
    const values = preview.map(row => {
      const v = parseFloat(row[key])
      return isNaN(v) ? null : v
    })
    const filtered = labels.map((l, i) => ({ l, v: values[i] })).filter(x => x.v !== null)
    return {
      labels: filtered.map(x => x.l),
      datasets: [{
        label: tab.charAt(0).toUpperCase() + tab.slice(1),
        data: filtered.map(x => x.v),
        backgroundColor: '#22d3ee'
      }]
    }
  }, [preview, labelCol, colMap, tab])

  const typeData = useMemo(() => ({
    labels: Object.keys(typeDist),
    datasets: [{ data: Object.values(typeDist), backgroundColor: ['#3b82f6','#22c55e','#ef4444','#f59e0b','#8b5cf6','#06b6d4'] }]
  }), [typeDist])

  return (
    <section className="section">
      <div className="charts-grid">
        <div className="card">
          <div className="card-head">
            <h2>Distribution by Unit</h2>
            <div className="tabs">
              <button className={`tab ${tab==='pressure'?'active':''}`} onClick={() => setTab('pressure')}>Pressure</button>
              <button className={`tab ${tab==='temperature'?'active':''}`} onClick={() => setTab('temperature')}>Temperature</button>
              <button className={`tab ${tab==='flowrate'?'active':''}`} onClick={() => setTab('flowrate')}>Flow Rate</button>
            </div>
          </div>
          <Bar data={distData} options={{ responsive: true, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#94a3b8' } }, y: { ticks: { color: '#94a3b8' } } } }} />
        </div>
        <div className="card pie-wrap">
          <h3>Type Distribution</h3>
          <div className="pie-inner">
            <Pie data={typeData} options={{ responsive: true, maintainAspectRatio: false, plugins:{ legend:{ position:'bottom', labels:{ color:'#94a3b8' } } } }} />
          </div>
        </div>
      </div>
    </section>
  )
}
