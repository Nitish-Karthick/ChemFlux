// Prefer Vite env (for Netlify / production), fall back to local dev API
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api'

export function getCreds() {
  try { return JSON.parse(localStorage.getItem('chemflux_creds')) } catch { return null }
}
export function setCreds(username, password) {
  localStorage.setItem('chemflux_creds', JSON.stringify({ username, password }))
}
export function clearCreds() {
  localStorage.removeItem('chemflux_creds')
}
function authHeader() {
  const c = getCreds()
  if (!c) return {}
  const token = btoa(`${c.username}:${c.password}`)
  return { Authorization: `Basic ${token}` }
}
export function tempAuthHeader(username, password) {
  const token = btoa(`${username}:${password}`)
  return { Authorization: `Basic ${token}` }
}
export async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`, { headers: { ...authHeader() } })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
export async function apiPostForm(path, formData) {
  const res = await fetch(`${API_BASE}${path}`, { method: 'POST', headers: { ...authHeader() }, body: formData })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
export async function apiGetBlob(path) {
  const res = await fetch(`${API_BASE}${path}`, { headers: { ...authHeader() } })
  if (!res.ok) throw new Error(await res.text())
  return res.blob()
}
export async function testAuth(username, password) {
  const res = await fetch(`${API_BASE}/datasets/`, { headers: { ...tempAuthHeader(username, password) } })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
