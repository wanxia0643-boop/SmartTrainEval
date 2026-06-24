import http from './http'

export const listEvalResults = (params) => http.get('/eval-results', { params })
export const createEvalResult = (data) => http.post('/eval-results', data)
export const updateEvalResult = (id, data) => http.put(`/eval-results/${id}`, data)
export const deleteEvalResult = (id) => http.delete(`/eval-results/${id}`)
export const recalcFinalScore = (achievementId) => http.post(`/eval-results/recalc/${achievementId}`)
