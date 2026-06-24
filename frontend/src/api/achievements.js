import http from './http'

export const listAchievements = (params) => http.get('/achievements', { params })
export const getAchievement = (id) => http.get(`/achievements/${id}`)
export const createAchievement = (data) => http.post('/achievements', data)
export const updateAchievement = (id, data) => http.put(`/achievements/${id}`, data)
export const deleteAchievement = (id) => http.delete(`/achievements/${id}`)
