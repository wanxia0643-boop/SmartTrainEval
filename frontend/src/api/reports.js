import http from './http'

export const listReports = (params) => http.get('/reports', { params })
export const getReport = (id) => http.get(`/reports/${id}`)
export const createReport = (data) => http.post('/reports', data)
export const updateReport = (id, data) => http.put(`/reports/${id}`, data)
export const deleteReport = (id) => http.delete(`/reports/${id}`)
export const downloadReport = (id) => http.get(`/reports/${id}/download`, { responseType: 'blob' })
