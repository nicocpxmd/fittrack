import { useState } from 'react'
import { addMeasurement } from '../services/api'

const FIELDS = ['weight_kg', 'waist_cm', 'chest_cm', 'arm_cm', 'forearm_cm', 'upper_leg_cm', 'lower_leg_cm', 'calf_cm', 'abdomen_cm', 'hip_cm', 'neck_cm', 'shoulder_cm', 'height_cm']

function MeasurementForm({ onSaved }) {
  const [date, setDate] = useState('')
  const [values, setValues] = useState({})
  const [status, setStatus] = useState(null)

  const handleChange = (field, val) => {
    setValues(prev => ({ ...prev, [field]: val === '' ? undefined : parseFloat(val) }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus('saving')
    const measurements = Object.fromEntries(
      Object.entries(values).filter(([, v]) => v !== undefined && !isNaN(v))
    )
    try {
      await addMeasurement({
        date,
        date_confidence: 'exact',
        data_context: 'adult_baseline',
        measurements,
        notes: '',
      })
      setStatus('saved')
      setValues({})
      onSaved?.()
    } catch (err) {
      setStatus('error: ' + err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow p-4 space-y-3">
      <h2 className="text-lg font-semibold text-gray-800">Log New Measurement</h2>

      <div>
        <label className="block text-sm text-gray-600 mb-1">Date</label>
        <input type="date" required value={date} onChange={e => setDate(e.target.value)}
          className="border rounded px-2 py-1 w-full" />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {FIELDS.map(field => (
          <div key={field}>
            <label className="block text-xs text-gray-500 mb-1">{field}</label>
            <input type="number" step="0.1" value={values[field] ?? ''}
              onChange={e => handleChange(field, e.target.value)}
              className="border rounded px-2 py-1 w-full text-sm" />
          </div>
        ))}
      </div>

      <button type="submit" disabled={status === 'saving'}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50">
        {status === 'saving' ? 'Saving...' : 'Save Measurement'}
      </button>

      {status === 'saved' && <p className="text-green-600 text-sm">Saved!</p>}
      {status?.startsWith('error') && <p className="text-red-600 text-sm">{status}</p>}
    </form>
  )
}

export default MeasurementForm