<script setup>
import { computed, ref } from 'vue'
import { CircleCheck, DocumentChecked, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../../stores/user'

const props = defineProps({ title: String, description: String })
const userStore = useUserStore()
const filter = ref('全部状态')
const rows = computed(() => [
  { title: `${props.title} · 当前事项`, owner: userStore.name, status: '进行中', updated: '刚刚' },
  { title: `${props.title} · 本周计划`, owner: userStore.name, status: '待处理', updated: '2 小时前' },
  { title: `${props.title} · 历史记录`, owner: userStore.name, status: '已完成', updated: '昨天' },
])
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div><p class="page-eyebrow">WORKSPACE</p><h2>{{ title }}</h2><p>{{ description }}</p></div>
      <el-button type="primary" @click="ElMessage.success(`已创建${title}事项`)" :icon="Plus">新建事项</el-button>
    </div>
    <article class="data-panel feature-toolbar"><div class="toolbar-copy"><strong>当前工作</strong><span>按状态筛选并处理最新事项</span></div><el-select v-model="filter" aria-label="筛选事项状态"><el-option label="全部状态" value="全部状态" /><el-option label="进行中" value="进行中" /><el-option label="待处理" value="待处理" /></el-select></article>
    <article class="data-panel feature-list"><div v-for="row in rows" :key="row.title" class="feature-row"><div class="feature-row-icon"><el-icon><DocumentChecked /></el-icon></div><div class="feature-row-main"><strong>{{ row.title }}</strong><span>负责人：{{ row.owner }} · 最近更新 {{ row.updated }}</span></div><el-tag :type="row.status === '已完成' ? 'success' : row.status === '待处理' ? 'warning' : 'primary'" effect="plain">{{ row.status }}</el-tag><el-button text type="primary" @click="ElMessage.info('详情页面待接入业务接口')">查看详情</el-button></div></article>
    <article class="feature-empty-hint"><el-icon><CircleCheck /></el-icon><span>页面骨架、权限路由与交互状态已就绪，接入业务接口后即可扩展为完整功能模块。</span></article>
  </section>
</template>
