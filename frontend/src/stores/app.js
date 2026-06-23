import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarCollapsed: localStorage.getItem('ste-sidebar-collapsed') === 'true',
    mobileNavOpen: false,
  }),
  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
      localStorage.setItem('ste-sidebar-collapsed', String(this.sidebarCollapsed))
    },
    toggleMobileNav() { this.mobileNavOpen = !this.mobileNavOpen },
    closeMobileNav() { this.mobileNavOpen = false },
  },
})
