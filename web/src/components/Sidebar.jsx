import { useState } from 'react'

export default function Sidebar({ onDownloadReport, onNavigate, active }) {
  const [open, setOpen] = useState(true)
  return (
    <aside className={open ? 'sidebar' : 'sidebar collapsed'}>
      <div className="top-controls">
        <button className="ghost toggle" onClick={() => setOpen(!open)} aria-label="toggle" title="Toggle">≡</button>
      </div>
      {open && (
        <>
          <div className="brand">
            <div className="logo">CF</div>
            <div className="brand-text">
              <div className="title">ChemFlux</div>
              <div className="sub">Parameter Visualizer</div>
            </div>
          </div>
          <nav className="nav">
            <button className={`nav-item ${active==='dashboard'?'active':''}`} onClick={() => onNavigate('dashboard')}>
              <span>Dashboard</span>
            </button>
            <button className="nav-item" onClick={onDownloadReport}>
              <span>Download Report</span>
            </button>
          </nav>
        </>
      )}
    </aside>
  )
}
