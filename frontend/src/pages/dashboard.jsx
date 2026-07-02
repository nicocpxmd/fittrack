import { useEffect, useState } from 'react'
import { getMeasurements, deleteMeasurement, updateMeasurement } from '../services/api'
import MeasurementForm from '../components/measurementForm'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const formatDate = (ts) => new Date(ts).toISOString().slice(0, 10)

function MeasurementChart({ title, dataKey, color, chartData }) {
  return (
    <div className="bg-white rounded-xl shadow p-4">
      <h2 className="text-lg font-semibold mb-2 text-gray-800">{title}</h2>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="ts" type="number" domain={['dataMin', 'dataMax']} tickFormatter={formatDate} tick={{ fontSize: 12 }} />
          <YAxis domain={['auto', 'auto']} tick={{ fontSize: 12 }} />
          <Tooltip labelFormatter={formatDate} />
          <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={{ r: 3 }} connectNulls={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function Dashboard() {
  const [data, setData] = useState([])
  const [error, setError] = useState(null)
  const [actionError, setActionError] = useState(null)
  const [actionSuccess, setActionSuccess] = useState(null)
  const [editing, setEditing] = useState(null)
  const [editValues, setEditValues] = useState({})
  const [editError, setEditError] = useState(null)

  const refresh = () => getMeasurements().then(res => setData(res.data))

  useEffect(() => {
    refresh().catch(err => setError(err.message))
  }, [])

  if (error) return <p className="p-4 text-red-600">Error: {error}</p>

  const chartData = [...data]
    .map(d => ({ ...d, ts: new Date(d.date).getTime() }))
    .sort((a, b) => a.ts - b.ts)

  const metrics = [
    { title: 'Weight (kg)', dataKey: 'measurements.weight_kg', color: '#2563eb' },
    { title: 'Waist (cm)', dataKey: 'measurements.waist_cm', color: '#dc2626' },
    { title: 'Arm (cm)', dataKey: 'measurements.arm_cm', color: '#16a34a' },
    { title: 'Chest (cm)', dataKey: 'measurements.chest_cm', color: '#9333ea' },
  ]

  const handleDelete = async (id) => {
    if (!confirm('Delete this record?')) return
    setActionError(null)
    setActionSuccess(null)
    try {
      await deleteMeasurement(id)
      setActionSuccess('Record deleted successfully.')
      refresh()
    } catch (err) {
      setActionError(err.message)
    }
  }

  const startEdit = (record) => {
    setEditing(record)
    setEditValues({ ...record.measurements })
  }

  const saveEdit = async () => {
    setEditError(null)
    setActionError(null)
    setActionSuccess(null)

    const measurements = Object.fromEntries(
      Object.entries(editValues).filter(([, v]) => v !== undefined && !isNaN(v))
    )

    if (Object.keys(measurements).length === 0) {
      setEditError('Please set at least one measurement.')
      return
    }
    if (Object.values(measurements).some(v => v < 0)) {
      setEditError('Measurement values must be non-negative.')
      return
    }
    if (measurements.weight_kg !== undefined && (measurements.weight_kg < 20 || measurements.weight_kg > 300)) {
      setEditError('Weight must be between 20 and 300 kg.')
      return
    }

    try {
      await updateMeasurement(editing.id, { measurements })
      setEditing(null)
      setEditError(null)
      setActionSuccess('Record updated successfully.')
      refresh()
    } catch (err) {
      setEditError(err.message)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm p-4">
        <h1 className="text-2xl font-bold text-gray-900">Fitness Analytics</h1>
        <p className="text-sm text-gray-500">{data.length} records tracked</p>
        {actionError && <p className="mt-2 text-red-600 text-sm">{actionError}</p>}
        {actionSuccess && <p className="mt-2 text-green-600 text-sm">{actionSuccess}</p>}
      </header>

      <main className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <MeasurementForm onSaved={refresh} />
        {metrics.map(m => (
          <MeasurementChart key={m.dataKey} {...m} chartData={chartData} />
        ))}
      </main>

      <div className="p-4 space-y-4">
        {editing && (
          <div className="bg-white rounded-xl shadow p-4">
            <h2 className="text-lg font-semibold mb-2">Edit {editing.date}</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {Object.entries(editValues).map(([key, val]) => (
                <div key={key}>
                  <label className="block text-xs text-gray-500">{key}</label>
                  <input
                    type="number"
                    step="0.1"
                    min={key === 'weight_kg' ? 20 : 0}
                    max={key === 'weight_kg' ? 300 : undefined}
                    required={key === 'weight_kg'}
                    value={val ?? ''}
                    onChange={e => setEditValues(prev => ({ ...prev, [key]: parseFloat(e.target.value) }))}
                    className="border rounded px-2 py-1 w-full text-sm"
                  />
                </div>
              ))}
            </div>
            <div className="mt-3 space-x-2">
              <button onClick={saveEdit} className="bg-blue-600 text-white px-4 py-2 rounded">Save</button>
              <button onClick={() => setEditing(null)} className="text-gray-500">Cancel</button>
            </div>
            {editError && <p className="text-red-600 text-sm mt-2">{editError}</p>}
          </div>
        )}

        <div className="bg-white rounded-xl shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Records</h2>
          <ul className="divide-y">
            {chartData.map(d => (
              <li key={d.id} className="flex justify-between items-center py-2 text-sm">
                <span>{d.date} — {d.measurements.weight_kg ?? '—'} kg</span>
                <div className="space-x-3">
                  <button onClick={() => startEdit(d)} className="text-blue-600 hover:underline">Edit</button>
                  <button onClick={() => handleDelete(d.id)} className="text-red-600 hover:underline">Delete</button>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <details>
          <summary className="cursor-pointer text-sm text-gray-500">Raw data ({data.length})</summary>
          <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  )
}

export default Dashboard