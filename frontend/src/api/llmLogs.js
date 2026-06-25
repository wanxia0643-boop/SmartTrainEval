import http from './http'

export const listLlmLogs = (params) => http.get('/llm-logs', { params })
export const getLlmLog = (id) => http.get(`/llm-logs/${id}`)
