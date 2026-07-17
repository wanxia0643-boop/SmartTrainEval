import { markRaw } from 'vue'
import { defineStore } from 'pinia'
import { getMenuRoutes } from '../router/route-data'

export const usePermissionStore = defineStore('permission', {
  state: () => ({ menus: [] }),
  actions: {
    setMenus(role) { this.menus = getMenuRoutes(role).map((route) => markRaw(route)) },
  },
})
