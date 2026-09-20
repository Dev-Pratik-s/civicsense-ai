import { useState, useEffect } from 'react'
import axios from 'axios'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const API = 'http://127.0.0.1:8000'

function App() {
  const [reports, setReports] = useState([])
  const [form, setForm] = useState({ file: null, latitude: '', longitude: '', description: '' })
  const [loading, setLoading] = useState(false)

  useEffect(() => { fetchReports() }, [])

  const fetchReports = async () => {
    try {
      const res = await axios.get(`${API}/reports`)
      setReports(res.data)
    } catch (err) { console.error(err) }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.file || !form.latitude || !form.longitude) {
      alert('Please fill all required fields')
      return
    }
    setLoading(true)
    const data = new FormData()
    data.append('file', form.file)
    data.append('latitude', form.latitude)
    data.append('longitude', form.longitude)
    data.append('description', form.description)
    try {
      await axios.post(`${API}/report`, data)
      alert('Report submitted! AI detected the issue.')
      setForm({ file: null, latitude: '', longitude: '', description: '' })
      fetchReports()
    } catch (err) { alert('Error submitting report') }
    setLoading(false)
  }

  const getCurrentLocation = () => {
    navigator.geolocation.getCurrentPosition((pos) => {
      setForm({ ...form, latitude: pos.coords.latitude, longitude: pos.coords.longitude })
    })
  }

  const severityColor = (s) => {
    if (s === 'High') return '#ef4444'
    if (s === 'Medium') return '#f59e0b'
    return '#10b981'
  }

  return (
    <div className="min-h-screen">
      <header className="bg-blue-900 text-white p-4 shadow-lg">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">🏙️ CivicSense AI</h1>
            <p className="text-sm text-blue-200">Predictive City Problem Detector | SIH 2026 · PS 26205</p>
          </div>
          <p className="text-sm">Reports: <span className="font-bold">{reports.length}</span></p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">📸 Report an Issue</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input type="file" accept="image/*"
              onChange={(e) => setForm({ ...form, file: e.target.files[0] })}
              className="w-full border rounded p-2 text-sm" />
            <div className="grid grid-cols-2 gap-2">
              <input type="number" step="any" placeholder="Latitude *"
                value={form.latitude}
                onChange={(e) => setForm({ ...form, latitude: e.target.value })}
                className="border rounded p-2 text-sm" />
              <input type="number" step="any" placeholder="Longitude *"
                value={form.longitude}
                onChange={(e) => setForm({ ...form, longitude: e.target.value })}
                className="border rounded p-2 text-sm" />
            </div>
            <button type="button" onClick={getCurrentLocation}
              className="w-full bg-blue-100 text-blue-800 py-2 rounded text-sm font-medium hover:bg-blue-200">
              📍 Use My Location
            </button>
            <textarea placeholder="Description (optional)"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full border rounded p-2 text-sm" rows="3" />
            <button type="submit" disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50">
              {loading ? 'Submitting...' : '🚀 Submit Report'}
            </button>
          </form>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-4 lg:col-span-2">
          <h2 className="text-xl font-bold mb-4">🗺️ Live City Map</h2>
          <div style={{ height: '500px' }}>
            <MapContainer center={[20.5937, 78.9629]} zoom={5} style={{ height: '100%', width: '100%' }}>
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; OpenStreetMap' />
              {reports.map((r) => (
                <Marker key={r.id} position={[r.latitude, r.longitude]}>
                  <Popup>
                    <div className="text-sm">
                      <p className="font-bold capitalize">{r.category}</p>
                      <p>Severity: <span style={{ color: severityColor(r.severity) }}>{r.severity}</span></p>
                      <p>Confidence: {(r.confidence * 100).toFixed(0)}%</p>
                      <p>Status: {r.status}</p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 lg:col-span-3">
          <h2 className="text-xl font-bold mb-4">📋 Recent Reports</h2>
          {reports.length === 0 ? (
            <p className="text-gray-500">No reports yet. Submit one above!</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {reports.map((r) => (
                <div key={r.id} className="border rounded-lg p-4"
                  style={{ borderLeft: `5px solid ${severityColor(r.severity)}` }}>
                  <p className="font-bold capitalize">{r.category}</p>
                  <p className="text-sm text-gray-600">Severity: {r.severity}</p>
                  <p className="text-sm text-gray-600">Confidence: {(r.confidence * 100).toFixed(0)}%</p>
                  <p className="text-xs text-gray-400 mt-2">{new Date(r.created_at).toLocaleString()}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      <footer className="text-center p-6 text-gray-500 text-sm">
        Built for Smart India Hackathon 2026 · Problem Statement 26205
      </footer>
    </div>
  )
}

export default App