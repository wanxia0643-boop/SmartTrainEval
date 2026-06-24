import http from './http'

export const listProjects = (params) => http.get('/projects', { params })
export const getProject = (id) => http.get(`/projects/${id}`)
export const createProject = (data) => http.post('/projects', data)
export const updateProject = (id, data) => http.put(`/projects/${id}`, data)
export const deleteProject = (id) => http.delete(`/projects/${id}`)
