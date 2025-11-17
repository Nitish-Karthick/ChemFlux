import { useState } from 'react'
import { apiPostForm } from '../api'

export default function Upload({ onUploaded }) {
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function handleUpload() {
    if (!file) return
    setBusy(true)
    setError('')
    const form = new FormData()
    form.append('file', file)
    try {
      const data = await apiPostForm('/upload/', form)
      onUploaded(data)
    } catch (e) {
      setError('Upload failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="card">
      <h2>Upload CSV</h2>
      <input type="file" accept=".csv" onChange={e => setFile(e.target.files?.[0])} />
      <button onClick={handleUpload} disabled={!file || busy}>{busy ? 'Uploading...' : 'Upload'}</button>
      {error && <div className="error">{error}</div>}
    </div>
  )
}
