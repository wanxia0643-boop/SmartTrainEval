<script setup>
import { computed } from 'vue'
import { Menu as MenuIcon } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { usePermissionStore } from '../../stores/permission'

const appStore = useAppStore()
const permissionStore = usePermissionStore()
const router = useRouter()
const route = useRoute()
const collapsed = computed(() => appStore.sidebarCollapsed)

function navigate(name) { router.push({ name }); appStore.closeMobileNav() }
function handleSidebarControl() {
  if (window.matchMedia('(max-width: 700px)').matches) appStore.closeMobileNav()
  else appStore.toggleSidebar()
}
</script>

<template>
  <aside class="sidebar" :class="{ 'is-collapsed': collapsed, 'is-mobile-open': appStore.mobileNavOpen }">
    <div class="brand-lockup" :aria-label="collapsed ? '智训评' : '智训评 软件实训智能评价系统'">
      <div class="brand-mark"><img src="/logo.svg" alt="" /></div>
      <div v-show="!collapsed" class="brand-copy">
        <strong>智训评</strong>
        <span>实训协同与评价</span>
      </div>
    </div>

    <nav class="sidebar-nav" aria-label="主导航">
      <el-menu
        :collapse="collapsed"
        :default-active="String(route.name)"
        background-color="transparent"
        text-color="#4e5969"
        active-text-color="#1677ff"
        :collapse-transition="false"
      >
        <el-menu-item v-for="item in permissionStore.menus" :key="item.name" :index="item.name" @click="navigate(item.name)">
          <el-icon><component :is="item.meta.icon" /></el-icon>
          <template #title>{{ item.meta.title }}</template>
        </el-menu-item>
      </el-menu>
    </nav>

    <button class="collapse-control" type="button" :aria-label="appStore.mobileNavOpen ? '关闭导航菜单' : (collapsed ? '展开侧边栏' : '收起侧边栏')" @click="handleSidebarControl">
      <el-icon><MenuIcon /></el-icon>
      <span v-show="!collapsed">收起</span>
    </button>
  </aside>
</template>
