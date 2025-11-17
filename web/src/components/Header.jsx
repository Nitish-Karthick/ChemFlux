import { getCreds } from '../api'

export default function Header({ onLogout }) {
  const creds = getCreds()
  const initial = creds?.username?.[0]?.toUpperCase() || 'U'
  return (
    <header className="topbar">
      <div className="topbar-left">
        <div className="logo sm">CF</div>
        <div className="brand-name">ChemFlux</div>
        <div className="divider" />
        <div className="topbar-title">Equipment Parameter Dashboard</div>
      </div>
      <div className="topbar-actions">
        <button className="btn ghost" title="Settings">⚙️</button>
        <div className="avatar" title={creds?.username || 'User'}>{initial}</div>
        <button className="btn" onClick={onLogout}>Logout</button>
      </div>
    </header>
  )
}
