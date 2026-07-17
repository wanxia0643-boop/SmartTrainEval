<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'
import AppHeader from './components/AppHeader.vue'
import { usePermissionStore } from '../stores/permission'
import { useUserStore } from '../stores/user'

const route = useRoute()
const userStore = useUserStore()
const permissionStore = usePermissionStore()

onMounted(() => permissionStore.setMenus(userStore.role))
watch(() => userStore.role, (role) => permissionStore.setMenus(role), { immediate: true })
const pageTitle = computed(() => {
  if (route.name === 'dashboard' && userStore.role === 'teacher') return '工作台'
  return route.meta.title || '工作台'
})
</script>

<template>
  <section class="app-shell">
    <AppSidebar />
    <main class="app-main">
      <AppHeader :title="pageTitle" />
      <div class="content-stage">
        <RouterView v-slot="{ Component }">
          <Transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </div>
    </main>
  </section>
</template>
