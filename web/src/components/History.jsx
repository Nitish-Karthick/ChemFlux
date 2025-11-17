import { useEffect, useState } from 'react'
import { apiGet, apiGetBlob } from '../api'

export default function History({ onSelect }) {
  const [items, setItems] = useState([])
  const [busy, setBusy] = useState(false)

  async function load() {
    setBusy(true)
    try {
      const data = await apiGet('/datasets/')
      setItems(data.results || [])
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => { load() }, [])

  async function downloadPdf(id) {
    const blob = await apiGetBlob(`/datasets/${id}/report/`)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `chemflux_report_${id}.pdf`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="card">
      <h2>History (Last 5)</h2>
      {busy ? <div>Loading...</div> : (
        <ul className="list">
          {items.map(it => (
            <li key={it.id} className="list-item">
              <div>
                <div className="title">{it.name}</div>
                <div className="sub">{new Date(it.uploaded_at).toLocaleString()}</div>
              </div>
              <div className="actions">
                <button onClick={() => onSelect(it.id)}>View</button>
                <button onClick={() => downloadPdf(it.id)}>PDF</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
