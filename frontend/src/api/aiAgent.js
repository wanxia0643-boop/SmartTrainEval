import http from './http'

export const coachChat = (data) => http.post('/ai/coach/chat', data, { timeout: 35_000 })
export const generateProjectDraft = (data) => http.post('/ai/projects/draft', data, { timeout: 35_000 })
export const applyProjectDraft = (data) => http.post('/ai/projects/draft/apply', data)
export const precheckAchievement = (id) => http.post(`/ai/achievements/${id}/precheck`, null, { timeout: 35_000 })
export const analyzeClass = (projectId) => http.post(`/ai/projects/${projectId}/class-analysis`, null, { timeout: 35_000 })
export const generateEnterpriseEvidence = (id) => http.post(`/ai/achievements/${id}/enterprise-evidence`, null, { timeout: 35_000 })
export const generateProjectBriefing = (projectId) => http.post(`/ai/projects/${projectId}/briefing`, null, { timeout: 35_000 })
export const listAIAnalyses = (params) => http.get('/ai/analyses', { params })
export const getAIHealth = () => http.get('/ai/health')
