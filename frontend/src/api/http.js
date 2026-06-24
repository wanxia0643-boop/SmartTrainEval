import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 12_000,
})

http.interceptors.request.use((config) => {
  const session = JSON.parse(localStorage.getItem('ste-user-session') || '{}')
  if (session.token) config.headers.Authorization = `Bearer ${session.token}`
  return config
})

function hasSession() {
  return !!JSON.parse(localStorage.getItem('ste-user-session') || '{}').token
}

http.interceptors.response.use(
  (response) => {
    const body = response.data
    // 统一响应结构 { code, msg, data }：成功返回 data，业务失败抛错
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) return body.data
      ElMessage.error(body.msg || '请求失败')
      const err = new Error(body.msg || '请求失败')
      err.code = body.code
      return Promise.reject(err)
    }
    return body
  },
  async (error) => {
    const status = error.response?.status
    const body = error.response?.data
    const message = body?.msg || body?.message || error.message || '请求失败，请稍后重试'
    // 仅在「曾经登录、token 失效」时清理并跳登录；新登录失败只提示
    if (status === 401 && hasSession()) {
      localStorage.removeItem('ste-user-session')
      ElMessage.error('登录状态已失效，请重新登录')
      const { default: router } = await import('../router')
      if (router.currentRoute.value.name !== 'login') router.replace('/login')
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  },
)

export default http
