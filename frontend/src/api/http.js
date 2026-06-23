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

http.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const status = error.response?.status
    const message = error.response?.data?.message || error.message || '请求失败，请稍后重试'
    if (status === 401) {
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
