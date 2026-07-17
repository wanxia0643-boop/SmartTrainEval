import http from './http'

export const listKnowledgeDocuments = (params) => http.get('/knowledge/documents', { params })
export const uploadKnowledgeDocument = ({ courseId, projectId, title, file }) => {
  const data = new FormData()
  data.append('course_id', courseId)
  if (projectId) data.append('project_id', projectId)
  if (title) data.append('title', title)
  data.append('file', file)
  return http.post('/knowledge/documents', data, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 35_000 })
}
export const deleteKnowledgeDocument = (id) => http.delete(`/knowledge/documents/${id}`)

