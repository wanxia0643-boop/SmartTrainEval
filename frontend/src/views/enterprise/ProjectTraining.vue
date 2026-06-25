<script setup>
import { onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { listProjects } from '../../api/projects'
import { listAchievements } from '../../api/achievements'

const DIFFICULTY = { 1: '初级', 2: '中级', 3: '高级' }
const PROJ_STATUS = { 0: '未开始', 1: '进行中', 2: '已结束', 3: '已归档' }
const PROJ_TAG = { 0: 'info', 1: 'primary', 2: 'success', 3: 'warning' }
const ACH_STATUS = { 0: '草稿', 1: '已提交', 2: '评价中', 3: '已评价', 4: '退回重做' }
const ACH_TAG = { 0: 'info', 1: 'primary', 2: 'warning', 3: 'success', 4: 'danger' }

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10

const drawerVisible = ref(false)
const drawerProject = ref(null)
const achLoading = ref(false)
const achievements = ref([])

async function fetchProjects() {
  loading.value = true
  try {
    const data = await listProjects({ page: page.value, page_size: pageSize })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function viewProgress(row) {
  drawerProject.value = row
  drawerVisible.value = true
  achLoading.value = true
  try {
    const data = await listAchievements({ project_id: row.id, page: 1, page_size: 100 })
    achievements.value = data.items
  } finally {
    achLoading.value = false
  }
}

function handlePageChange(p) {
  page.value = p
  fetchProjects()
}

onMounted(fetchProjects)
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">ENTERPRISE · PROJECTS</p>
        <h2>项目实训</h2>
        <p>跟进企业项目中的实训进度与实践产出。</p>
      </div>
      <el-button :icon="Refresh" @click="fetchProjects" :loading="loading">刷新</el-button>
    </div>

    <article class="data-panel">
      <el-table :data="rows" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="project_name" label="项目名称" min-width="160" />
        <el-table-column prop="project_code" label="编码" min-width="120" />
        <el-table-column label="难度" width="80">
          <template #default="{ row }">{{ DIFFICULTY[row.difficulty] || '—' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="PROJ_TAG[row.status]" effect="plain">{{ PROJ_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="viewProgress(row)">查看进度</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-pager">
        <el-pagination background layout="total, prev, pager, next" :total="total"
          :current-page="page" :page-size="pageSize" @current-change="handlePageChange" />
      </div>
    </article>

    <el-drawer v-model="drawerVisible" :title="`${drawerProject?.project_name || ''} · 实训产出`" size="52%">
      <el-table :data="achievements" v-loading="achLoading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="成果标题" min-width="160" />
        <el-table-column prop="student_id" label="学生ID" width="90" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="ACH_TAG[row.status]" effect="plain">{{ ACH_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="得分" width="90">
          <template #default="{ row }">{{ row.final_score ?? '—' }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!achLoading && !achievements.length" description="该项目暂无实训产出" />
    </el-drawer>
  </section>
</template>

<style scoped>
.table-pager { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
