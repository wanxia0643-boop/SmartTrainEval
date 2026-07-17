<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Bell, ChevronDown, Maximize2, Menu as MenuIcon } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { roleLabels } from '../../router/route-data'
import { useAppStore } from '../../stores/app'

defineProps({ title: { type: String, required: true } })
const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()
const roleName = computed(() => roleLabels[userStore.role])

async function toggleFullscreen() {
  if (!document.fullscreenElement) await document.documentElement.requestFullscreen?.()
  else await document.exitFullscreen?.()
}
function signOut() {
  userStore.logout()
  router.replace('/login')
}
function openNotifications() { ElMessage.info('通知中心已同步 3 条未读消息') }
</script>

<template>
  <header class="app-header">
    <div class="header-title">
      <button class="mobile-menu-button" type="button" aria-label="打开导航菜单" @click="appStore.toggleMobileNav">
        <MenuIcon :size="17" aria-hidden="true" />
      </button>
      <h1>{{ title }}</h1>
      <span class="header-divider" aria-hidden="true"></span>
      <span class="header-context">{{ roleName }}工作台</span>
    </div>
    <div class="header-actions">
      <el-tooltip content="全屏显示" placement="bottom">
        <button class="header-icon-button" type="button" aria-label="全屏显示" @click="toggleFullscreen">
          <Maximize2 :size="17" aria-hidden="true" />
        </button>
      </el-tooltip>
      <el-tooltip content="通知中心" placement="bottom">
        <button class="header-icon-button" type="button" aria-label="通知中心" @click="openNotifications">
          <el-badge :value="3" :max="9"><Bell :size="17" aria-hidden="true" /></el-badge>
        </button>
      </el-tooltip>
      <el-dropdown trigger="click">
        <button class="profile-trigger" type="button" aria-label="打开用户菜单">
          <el-avatar :size="32" class="user-avatar">{{ userStore.initials }}</el-avatar>
          <span class="profile-copy"><strong class="profile-name">{{ userStore.name }}</strong><small>{{ roleName }}</small></span>
          <ChevronDown class="profile-arrow" :size="14" aria-hidden="true" />
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
            <el-dropdown-item divided @click="signOut">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>
