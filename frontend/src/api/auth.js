import { roleCredentials } from '../router/route-data'

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

/** Replace this adapter with a real /auth/login API when the backend is available. */
export async function login({ account, password, role }) {
  await wait(420)
  const credential = roleCredentials[role]
  if (!credential || credential.account !== account || credential.password !== password) {
    throw new Error('账号、密码或登录角色不匹配')
  }
  return {
    token: `demo-${role}-${Date.now()}`,
    role,
    name: credential.name,
    department: credential.department,
  }
}
