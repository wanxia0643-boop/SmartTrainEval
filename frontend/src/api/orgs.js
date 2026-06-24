import http from './http'

export const listOrgs = (params) => http.get('/orgs', { params })
export const getOrg = (id) => http.get(`/orgs/${id}`)
export const createOrg = (data) => http.post('/orgs', data)
export const updateOrg = (id, data) => http.put(`/orgs/${id}`, data)
export const deleteOrg = (id) => http.delete(`/orgs/${id}`)
