import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

export const getMeasurements = () => api.get('/measurements')

export default api