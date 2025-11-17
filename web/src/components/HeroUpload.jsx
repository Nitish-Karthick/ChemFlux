import { useRef, useState } from 'react'
import { apiPostForm } from '../api'

export default function HeroUpload({ onUploaded }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [drag, setDrag] = useState(false)
  const fileRef = useRef(null)

  async function upload(file) {
    if (!file) return
    setBusy(true)
    setError('')
    const form = new FormData()
    form.append('file', file)
    try {
      const data = await apiPostForm('/upload/', form)
      onUploaded?.(data)
    } catch (e) {
      setError('Upload failed')
    } finally {
      setBusy(false)
      setDrag(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  function onDrop(e) {
    e.preventDefault()
    const f = e.dataTransfer.files?.[0]
    upload(f)
  }

  return (
    <div className="hero">
      <div
        className={`dropzone ${drag ? 'drag' : ''}`}
        onDragOver={e => { e.preventDefault(); setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
      >
        <div className="drop-content">
          <div className="drop-title">Upload your data to get started</div>
          <div className="drop-sub">Drag & drop your CSV file here or click the button below to browse your files.</div>
          <div className="drop-actions">
            <input ref={fileRef} type="file" accept=".csv" hidden onChange={e => upload(e.target.files?.[0])} />
            <button className="btn primary" onClick={() => fileRef.current?.click()} disabled={busy}>
              {busy ? 'Uploading…' : 'Upload CSV'}
            </button>
          </div>
          {error && <div className="error mt8">{error}</div>}
        </div>
      </div>
    </div>
  )
}
