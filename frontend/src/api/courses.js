import http from './http'

export const listCourses = (params) => http.get('/courses', { params })
export const getCourse = (id) => http.get(`/courses/${id}`)
export const createCourse = (data) => http.post('/courses', data)
export const updateCourse = (id, data) => http.put(`/courses/${id}`, data)
export const deleteCourse = (id) => http.delete(`/courses/${id}`)
export const pinCourse = (id) => http.post(`/courses/${id}/pin`)
