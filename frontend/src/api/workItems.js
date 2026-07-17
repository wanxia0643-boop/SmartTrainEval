import http from './http'

export const listWorkItems = (params) => http.get('/work-items', { params })
export const completeWorkItem = (id) => http.post(`/work-items/${id}/complete`)

