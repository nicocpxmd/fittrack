import { useState } from 'react'
import { addMeasurement } from '../services/api'

const FIELDS = ['weight_kg', 'waist_cm', 'chest_cm', 'arm_cm', 'forearm_cm', 'upper_leg_cm', 'lower_leg_cm', 'calf_cm', 'abdomen_cm', 'hip_cm', 'neck_cm', 'shoulder_cm', 'height_cm']

function MeasurementForm({ onSaved }) {
  const [date, setDate] = useState('')
  const [values, setValues] = useState({})
  const [status, setStatus] = useState(null)

  const handleChange = (field, val) => {
    setStatus(null)
    setValues(prev => ({ ...prev, [field]: val === '' ? undefined : parseFloat(val) }))
  }

  const validateMeasurements = (measurements) => {
    if (measurements.weight_kg !== undefined && (measurements.weight_kg < 20 || measurements.weight_kg > 300)) {
      throw new Error('Weight must be between 20 and 300 kg')
    }
    if (Object.values(measurements).some(v => v < 0)) {
      throw new Error('Measurement values cannot be negative')
    }
    if (Object.keys(measurements).length === 0) {
      throw new Error('Please enter at least one measurement')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus('saving')
    const measurements = Object.fromEntries(
      Object.entries(values).filter(([, v]) => v !== undefined && !isNaN(v))
    )
    try {
      validateMeasurements(measurements)
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
            <input
              type="number"
              step="0.1"
              min={field === 'weight_kg' ? 20 : 0}
              max={field === 'weight_kg' ? 300 : undefined}
              required={field === 'weight_kg'}
              value={values[field] ?? ''}
              onChange={e => handleChange(field, e.target.value)}
              className="border rounded px-2 py-1 w-full text-sm"
            />
          </div>
        ))}
      </div>

      <button type="submit" disabled={status === 'saving'}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50">
        {status === 'saving' ? 'Saving...' : 'Save Measurement'}
      </button>

      {status === 'saved' && (
        <div className="rounded border border-green-200 bg-green-50 p-3 text-green-700 text-sm">
          Measurement saved successfully.
        </div>
      )}
      {status?.startsWith('error') && (
        <div className="rounded border border-red-200 bg-red-50 p-3 text-red-700 text-sm">
          {status.replace('error: ', '')}
        </div>
      )}
    </form>
  )
}

export default MeasurementForm