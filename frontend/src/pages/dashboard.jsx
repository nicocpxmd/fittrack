import { useEffect, useState } from 'react'
import { getMeasurements, deleteMeasurement } from '../services/api'
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
    await deleteMeasurement(id)
    refresh()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm p-4">
        <h1 className="text-2xl font-bold text-gray-900">Fitness Analytics</h1>
        <p className="text-sm text-gray-500">{data.length} records tracked</p>
      </header>

      <main className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <MeasurementForm onSaved={refresh} />
        {metrics.map(m => (
          <MeasurementChart key={m.dataKey} {...m} chartData={chartData} />
        ))}
      </main>

      <div className="p-4">
        <div className="bg-white rounded-xl shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Records</h2>
          <ul className="divide-y">
            {chartData.map(d => (
              <li key={d.id} className="flex justify-between items-center py-2 text-sm">
                <span>{d.date} — {d.measurements.weight_kg ?? '—'} kg</span>
                <button onClick={() => handleDelete(d.id)} className="text-red-600 hover:underline">
                  Delete
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <details className="p-4">
        <summary className="cursor-pointer text-sm text-gray-500">Raw data ({data.length})</summary>
        <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  )
}

export default Dashboard