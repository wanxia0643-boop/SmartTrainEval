<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, Check, Refresh, Timer } from '@element-plus/icons-vue'
import { completeWorkItem, listWorkItems } from '../../api/workItems'

const router = useRouter()
const loading = ref(false)
const status = ref(0)
const items = ref([])
const total = ref(0)

const TASK_LABELS = {
  SUBMIT_ACHIEVEMENT: '成果提交',
  REDO_ACHIEVEMENT: '整改重交',
  TEACHER_REVIEW: '教师评价',
  ENTERPRISE_REVIEW: '企业评价',
  VIEW_FEEDBACK: '查看反馈',
}

const pendingCount = computed(() => status.value === 0 ? total.value : 0)

async function fetchItems() {
  loading.value = true
  try {
    const data = await listWorkItems({ status: status.value, page: 1, page_size: 100 })
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function openTask(item) {
  const routeMap = {
    SUBMIT_ACHIEVEMENT: 'training',
    REDO_ACHIEVEMENT: 'training',
    TEACHER_REVIEW: 'intelligent-evaluation',
    ENTERPRISE_REVIEW: 'talent-evaluation',
    VIEW_FEEDBACK: 'my-evaluation',
  }
  router.push({ name: routeMap[item.task_type] || 'dashboard' })
}

async function finish(item) {
  await completeWorkItem(item.id)
  await fetchItems()
}

function formatTime(value) {
  return value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '长期'
}

onMounted(fetchItems)
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">ROLE WORKFLOW</p>
        <h2>任务中心</h2>
        <p>汇总待提交、待评价、退回整改和反馈查看，业务状态变化时自动更新。</p>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="fetchItems">刷新</el-button>
    </div>

    <article class="data-panel work-panel">
      <div class="work-toolbar">
        <el-segmented v-model="status" :options="[{ label: '待办', value: 0 }, { label: '已办', value: 1 }]" @change="fetchItems" />
        <span><el-icon><Bell /></el-icon>{{ status === 0 ? `${total} 项待处理` : `${total} 项已完成` }}</span>
      </div>
      <div v-loading="loading" class="work-list">
        <article v-for="item in items" :key="item.id" class="work-row">
          <span class="work-icon" :class="`priority-${item.priority}`"><el-icon><Timer /></el-icon></span>
          <div class="work-copy">
            <div><el-tag size="small" effect="plain">{{ TASK_LABELS[item.task_type] || item.task_type }}</el-tag><strong>{{ item.title }}</strong></div>
            <p>{{ item.description || '请进入对应业务页面完成处理。' }}</p>
            <span>截止时间：{{ formatTime(item.due_time) }}</span>
          </div>
          <div class="work-actions">
            <el-button v-if="item.status === 0" type="primary" @click="openTask(item)">去处理</el-button>
            <el-button v-if="item.status === 0 && item.task_type === 'VIEW_FEEDBACK'" :icon="Check" @click="finish(item)">标记已读</el-button>
            <el-tag v-else-if="item.status === 1" type="success" effect="plain">已完成</el-tag>
          </div>
        </article>
        <el-empty v-if="!loading && !items.length" :description="status === 0 ? '当前没有待办任务' : '暂无已办记录'" />
      </div>
    </article>
  </section>
</template>

<style scoped>
.work-panel { overflow: hidden; }
.work-toolbar { display: flex; align-items: center; justify-content: space-between; padding: 16px 18px; border-bottom: 1px solid var(--ste-border); }
.work-toolbar > span { display: flex; align-items: center; gap: 6px; color: var(--ste-muted); font-size: 13px; }
.work-list { min-height: 300px; }
.work-row { display: grid; grid-template-columns: 42px minmax(0, 1fr) auto; gap: 14px; align-items: center; padding: 18px; border-bottom: 1px solid var(--ste-border); }
.work-icon { display: grid; width: 38px; height: 38px; place-items: center; color: var(--ste-primary); background: var(--ste-primary-soft); border-radius: 8px; }
.work-icon.priority-3 { color: var(--ste-danger); background: #fff0f0; }
.work-copy { min-width: 0; }
.work-copy > div { display: flex; align-items: center; gap: 9px; }
.work-copy strong { overflow: hidden; font-size: 14px; text-overflow: ellipsis; white-space: nowrap; }
.work-copy p { margin: 7px 0 5px; color: #536178; font-size: 13px; }
.work-copy > span { color: var(--ste-muted); font-size: 11px; }
.work-actions { display: flex; gap: 8px; }
@media (max-width: 700px) { .work-row { grid-template-columns: 38px 1fr; }.work-actions { grid-column: 2; }.work-toolbar { align-items: flex-start; flex-direction: column; gap: 12px; } }
</style>

