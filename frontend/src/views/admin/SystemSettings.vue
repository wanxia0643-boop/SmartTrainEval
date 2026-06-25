<script setup>
import { onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { listUsers } from '../../api/users'
import { listOrgs } from '../../api/orgs'
import { listProjects } from '../../api/projects'
import { listAchievements } from '../../api/achievements'
import { listReports } from '../../api/reports'
import { listEvalResults } from '../../api/evalResults'
import { listLlmLogs } from '../../api/llmLogs'
import { listRoles } from '../../api/roles'

const DATA_SCOPE = { 1: '本人', 2: '本组织', 3: '全部' }

const loading = ref(false)
const roles = ref([])
const stats = ref([
  { key: 'users', label: '平台用户', value: '—' },
  { key: 'orgs', label: '组织机构', value: '—' },
  { key: 'projects', label: '实训项目', value: '—' },
  { key: 'achievements', label: '实训成果', value: '—' },
  { key: 'evals', label: '评价记录', value: '—' },
  { key: 'reports', label: '报表记录', value: '—' },
  { key: 'llm', label: 'AI 调用', value: '—' },
])

const SYSTEM_INFO = [
  { label: '系统名称', value: '智训评 · 软件实训智能评价系统' },
  { label: '版本', value: 'v0.1.0' },
  { label: '前端技术', value: 'Vue 3 + Vite + Element Plus' },
  { label: '后端技术', value: 'FastAPI + SQLAlchemy 2.0 + MySQL' },
  { label: 'AI 能力', value: 'LangChain 智能核查' },
]

async function total(fn) {
  try { return (await fn).total } catch { return '—' }
}

async function loadAll() {
  loading.value = true
  try {
    roles.value = await listRoles()
    const p = { page: 1, page_size: 1 }
    const [u, o, pr, a, e, r, l] = await Promise.all([
      total(listUsers(p)), total(listOrgs(p)), total(listProjects(p)),
      total(listAchievements(p)), total(listEvalResults(p)),
      total(listReports(p)), total(listLlmLogs(p)),
    ])
    const map = { users: u, orgs: o, projects: pr, achievements: a, evals: e, reports: r, llm: l }
    stats.value = stats.value.map((s) => ({ ...s, value: map[s.key] }))
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
</script>

<template>
  <section class="feature-page" v-loading="loading">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">SYSTEM · SETTINGS</p>
        <h2>系统设置</h2>
        <p>查看平台运行概览、角色权限与系统信息（只读）。</p>
      </div>
      <el-button :icon="Refresh" @click="loadAll" :loading="loading">刷新</el-button>
    </div>

    <div class="stat-grid">
      <article v-for="s in stats" :key="s.key" class="data-panel stat-card">
        <span>{{ s.label }}</span><strong>{{ s.value }}</strong>
      </article>
    </div>

    <article class="data-panel">
      <div class="panel-head"><strong>角色与数据权限</strong></div>
      <el-table :data="roles" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="role_name" label="角色名称" min-width="120" />
        <el-table-column prop="role_code" label="角色编码" min-width="120" />
        <el-table-column label="数据范围" min-width="100">
          <template #default="{ row }">{{ DATA_SCOPE[row.data_scope] || '—' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" effect="plain">
              {{ row.status === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </article>

    <article class="data-panel">
      <div class="panel-head"><strong>系统信息</strong></div>
      <el-descriptions :column="1" border>
        <el-descriptions-item v-for="i in SYSTEM_INFO" :key="i.label" :label="i.label">
          {{ i.value }}
        </el-descriptions-item>
      </el-descriptions>
      <p class="settings-note">参数化的系统配置（评价规则、通知、阈值等）将在后续版本提供可编辑能力。</p>
    </article>
  </section>
</template>

<style scoped>
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 16px; }
@media (max-width: 1100px) { .stat-grid { grid-template-columns: repeat(2, 1fr); } }
.stat-card { display: flex; flex-direction: column; gap: 6px; }
.stat-card span { color: var(--el-text-color-secondary); font-size: 13px; }
.stat-card strong { font-size: 26px; color: var(--el-color-primary); }
.panel-head { margin-bottom: 12px; }
.data-panel + .data-panel { margin-top: 16px; }
.settings-note { margin-top: 14px; color: var(--el-text-color-secondary); font-size: 13px; }
</style>
