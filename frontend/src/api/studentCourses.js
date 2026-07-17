import request from './http'

/**
 * 获取学生已选课程列表
 */
export function listStudentCourses(params = {}) {
  return request({
    url: '/course-enrollments',
    method: 'get',
    params,
  })
}

/**
 * 学生选课（通过课程编码）
 */
export function enrollCourse(data) {
  return request({
    url: '/course-enrollments',
    method: 'post',
    data,
  })
}

/**
 * 退课
 */
export function dropCourse(enrollmentId) {
  return request({
    url: `/course-enrollments/${enrollmentId}`,
    method: 'delete',
  })
}
