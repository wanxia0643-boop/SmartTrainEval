import http from './http'

export const listIndicators = (params) => http.get('/indicators', { params })
export const createIndicator = (data) => http.post('/indicators', data)
export const updateIndicator = (id, data) => http.put(`/indicators/${id}`, data)
export const deleteIndicator = (id) => http.delete(`/indicators/${id}`)
