import { useEffect, useState } from 'react'
import { getMeasurements } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function Dashboard() {
  const [data, setData] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    getMeasurements()
      .then(res => setData(res.data))
      .catch(err => setError(err.message))
  }, [])

  if (error) return <p className="p-4 text-red-600">Error: {error}</p>

  const chartData = [...data]
    .map(d => ({ ...d, ts: new Date(d.date).getTime() }))
    .sort((a, b) => a.ts - b.ts)

  const formatDate = (ts) => new Date(ts).toISOString().slice(0, 10)

  return (
    <div className="p-4 space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-2">Weight Over Time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="ts"
              type="number"
              domain={['dataMin', 'dataMax']}
              tickFormatter={formatDate}
            />
            <YAxis domain={['auto', 'auto']} />
            <Tooltip labelFormatter={formatDate} />
            <Line
              type="monotone"
              dataKey="measurements.weight_kg"
              stroke="#2563eb"
              strokeWidth={2}
              dot={{ r: 3 }}
              connectNulls={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <details>
        <summary className="cursor-pointer text-sm text-gray-500">Raw data ({data.length})</summary>
        <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  )
}

export default Dashboard