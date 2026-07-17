import http from './http'

// 后端角色编码 -> 前端角色标识
const ROLE_MAP = {
  STUDENT: 'student',
  TEACHER: 'teacher',
  ENTERPRISE: 'enterprise',
  ADMIN: 'admin',
}

/**
 * 真实后端登录：
 *   1. POST /auth/login 获取 access_token
 *   2. GET  /auth/profile 获取完整用户资料
 * 返回 user store 需要的会话结构。
 */
export async function login({ account, password }) {
  const tokenData = await http.post('/auth/login', { username: account, password })
  const token = tokenData.access_token

  const profile = await http.get('/auth/profile', {
    headers: { Authorization: `Bearer ${token}` },
  })

  const role = ROLE_MAP[profile.role_code]
  if (!role) throw new Error('未知的用户角色，无法登录')

  return {
    token,
    role,
    userId: profile.user_id,
    username: profile.username,
    name: profile.real_name || profile.username,
    department: '',
    email: profile.email || '',
    phone: profile.phone || '',
    orgId: profile.org_id || null,
    studentNo: profile.student_no || '',
  }
}

/** 获取当前用户完整资料 */
export function getProfile() {
  return http.get('/auth/profile')
}

/** 更新当前用户个人资料 */
export function updateProfile(data) {
  return http.put('/auth/profile', data)
}
