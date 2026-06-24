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
 *   2. GET  /auth/me 获取角色与姓名
 * 返回 user store 需要的会话结构。
 */
export async function login({ account, password }) {
  const tokenData = await http.post('/auth/login', { username: account, password })
  const token = tokenData.access_token

  const me = await http.get('/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  })

  const role = ROLE_MAP[me.role_code]
  if (!role) throw new Error('未知的用户角色，无法登录')

  return {
    token,
    role,
    userId: me.user_id,
    username: me.username,
    name: me.real_name || me.username,
    department: '',
  }
}
