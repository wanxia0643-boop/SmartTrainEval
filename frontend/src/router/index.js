import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/auth/Login.vue'
import NotFound from '../views/error/NotFound.vue'
import MainLayout from '../layout/MainLayout.vue'
import { getAccessibleRoutes } from './route-data'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: Login, meta: { public: true } },
    { path: '/', name: 'root', component: MainLayout, redirect: '/dashboard', children: [] },
    { path: '/:pathMatch(.*)*', name: '404', component: NotFound, meta: { public: true } },
  ],
})

let dynamicRoutesReady = false
let installedRole = ''

export function installRoleRoutes(role) {
  if (dynamicRoutesReady && installedRole === role && router.hasRoute('dashboard')) return
  if (dynamicRoutesReady) resetRoleRoutes()
  getAccessibleRoutes(role).forEach((route) => router.addRoute('root', route))
  dynamicRoutesReady = true
  installedRole = role
}

export function resetRoleRoutes() {
  const routes = ['student', 'teacher', 'enterprise', 'admin'].flatMap(getAccessibleRoutes)
  routes.forEach((route) => router.hasRoute(route.name) && router.removeRoute(route.name))
  dynamicRoutesReady = false
  installedRole = ''
}

router.beforeEach(async (to) => {
  const { useUserStore } = await import('../stores/user')
  const userStore = useUserStore()
  userStore.hydrate()

  if (to.name === 'login') return userStore.token ? '/dashboard' : true
  if (!userStore.token) {
    if (to.meta.public) return true
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (!dynamicRoutesReady) {
    installRoleRoutes(userStore.role)
    return { path: to.fullPath, replace: true }
  }
  if (to.meta.public) return true
  if (to.meta.roles && !to.meta.roles.includes(userStore.role)) return '/404'
  return true
})

export default router
