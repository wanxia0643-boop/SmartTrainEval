import { defineStore } from 'pinia'
import { login as loginRequest } from '../api/auth'
import { resetRoleRoutes } from '../router'

const STORAGE_KEY = 'ste-user-session'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    role: '',
    userId: null,
    username: '',
    name: '',
    department: '',
    initialized: false,
  }),
  getters: {
    initials: (state) => state.name?.slice(0, 1) || '智',
  },
  actions: {
    hydrate() {
      if (this.initialized) return
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        try { Object.assign(this, JSON.parse(saved)) } catch { localStorage.removeItem(STORAGE_KEY) }
      }
      this.initialized = true
    },
    persist() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        token: this.token, role: this.role, userId: this.userId,
        username: this.username, name: this.name, department: this.department,
      }))
    },
    async login(payload) {
      const session = await loginRequest(payload)
      Object.assign(this, session)
      this.persist()
      return session
    },
    logout() {
      this.$patch({ token: '', role: '', userId: null, username: '', name: '', department: '' })
      localStorage.removeItem(STORAGE_KEY)
      resetRoleRoutes()
    },
  },
})
