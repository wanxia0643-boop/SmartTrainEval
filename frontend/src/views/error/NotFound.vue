<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <main class="not-found-page"><section><p>404</p><h1>这个页面暂时找不到</h1><span>它可能已被移动，或当前角色没有访问权限。</span><el-button type="primary" @click="router.replace('/dashboard')">回到工作台</el-button></section></main>
</template>
