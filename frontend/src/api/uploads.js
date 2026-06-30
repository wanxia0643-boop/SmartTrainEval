import http from './http'

export function uploadAttachment(file) {
  const form = new FormData()
  form.append('file', file)
  return http.post('/uploads', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
