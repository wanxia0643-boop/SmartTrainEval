import http from './http'

export const listUsers = (params) => http.get('/users', { params })
export const getUser = (id) => http.get(`/users/${id}`)
export const createUser = (data) => http.post('/users', data)
export const updateUser = (id, data) => http.put(`/users/${id}`, data)
export const deleteUser = (id) => http.delete(`/users/${id}`)
