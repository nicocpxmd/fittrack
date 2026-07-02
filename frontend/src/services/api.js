import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

export const getMeasurements = () => api.get('/measurements')
export const addMeasurement = (data) => api.post('/measurements', data)
export const deleteMeasurement = (id) => api.delete(`/measurements/${id}`)
export const updateMeasurement = (id, data) => api.put(`/measurements/${id}`, data)

export default api

