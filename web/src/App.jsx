import { useEffect, useState } from 'react'
import Login from './components/Login'
import History from './components/History'
import Summary from './components/Summary'
import Charts from './components/Charts'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import HeroUpload from './components/HeroUpload'
import Stats from './components/Stats'
import { apiGet, clearCreds, getCreds, apiGetBlob } from './api'

export default function App() {
  const [authed, setAuthed] = useState(false)
  const [datasets, setDatasets] = useState([])
  const [current, setCurrent] = useState(null)
  const [error, setError] = useState('')
  const [active, setActive] = useState('dashboard')

  async function loadDatasets() {
    try {
      const data = await apiGet('/datasets/')
      setDatasets(data.results)
      // Do not auto-select a dataset; wait for user action or upload
      setCurrent(null)
    } catch (e) { setError('Failed to load datasets') }
  }

  useEffect(() => {
    if (authed) loadDatasets()
  }, [authed])

  async function handleSelect(id) {
    const detail = await apiGet(`/datasets/${id}/`)
    setCurrent(detail)
  }

  function handleUploaded(ds) {
    setDatasets(prev => [ds, ...prev].slice(0, 5))
    setCurrent(ds)
  }

  function logout() {
    clearCreds()
    setAuthed(false)
    setDatasets([])
    setCurrent(null)
  }

  async function downloadCurrentPdf() {
    if (!current?.id) return
    const blob = await apiGetBlob(`/datasets/${current.id}/report/`)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `chemflux_report_${current.id}.pdf`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  if (!authed) return <div className="auth-wrap"><Login onLoggedIn={() => setAuthed(true)} /></div>

  return (
    <div className="layout">
      <Sidebar onDownloadReport={downloadCurrentPdf} onNavigate={setActive} active={active} />
      <div className="main">
        <Header onLogout={logout} />
        {error && <div className="error banner">{error}</div>}
        <div className="content">
          <HeroUpload onUploaded={handleUploaded} />
          {current && <Stats summary={current?.summary} />}
          {current && <Charts summary={current?.summary} />}
          {current && (
            <div className="two-col">
              <div className="col">
                <Summary dataset={current} />
              </div>
              <div className="col">
                <History onSelect={handleSelect} />
              </div>
            </div>
          )}
          {!current && (
            <div className="section">
              <History onSelect={handleSelect} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
