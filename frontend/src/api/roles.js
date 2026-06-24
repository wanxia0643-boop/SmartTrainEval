import http from './http'

export const listRoles = () => http.get('/roles')
