<script setup>
import { onMounted, reactive, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { listUsers } from '../../api/users'
import { listRoles } from '../../api/roles'
import { listAchievements } from '../../api/achievements'

const ACH_STATUS = { 0: '草稿', 1: '已提交', 2: '评价中', 3: '已评价', 4: '退回重做' }
const ACH_TAG = { 0: 'info', 1: 'primary', 2: 'warning', 3: 'success', 4: 'danger' }

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10 })
const studentRoleId = ref(null)

const drawerVisible = ref(false)
const drawerStudent = ref(null)
const achLoading = ref(false)
const achievements = ref([])

async function resolveStudentRole() {
  const roles = await listRoles()
  studentRoleId.value = roles.find((r) => r.role_code === 'STUDENT')?.id ?? null
}

async function fetchStudents() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (studentRoleId.value) params.role_id = studentRoleId.value
    const data = await listUsers(params)
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function viewArchive(row) {
  drawerStudent.value = row
  drawerVisible.value = true
  achLoading.value = true
  try {
    const data = await listAchievements({ student_id: row.id, page: 1, page_size: 50 })
    achievements.value = data.items
  } finally {
    achLoading.value = false
  }
}

function handlePageChange(page) {
  query.page = page
  fetchStudents()
}

onMounted(async () => {
  await resolveStudentRole()
  await fetchStudents()
})
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">TEACHER · ARCHIVE</p>
        <h2>学生档案</h2>
        <p>查看学生能力证据与成长变化。</p>
      </div>
      <el-button :icon="Refresh" @click="fetchStudents" :loading="loading">刷新</el-button>
    </div>

    <article class="data-panel">
      <el-table :data="rows" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="账号" min-width="120" />
        <el-table-column prop="real_name" label="姓名" min-width="100" />
        <el-table-column label="学号" min-width="120">
          <template #default="{ row }">{{ row.student_no || '—' }}</template>
        </el-table-column>
        <el-table-column label="手机号" min-width="120">
          <template #default="{ row }">{{ row.phone || '—' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" effect="plain">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="viewArchive(row)">查看成果</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-pager">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          :current-page="query.page"
          :page-size="query.page_size"
          @current-change="handlePageChange"
        />
      </div>
    </article>

    <el-drawer v-model="drawerVisible" :title="`${drawerStudent?.real_name || ''} 的实训成果`" size="50%">
      <el-table :data="achievements" v-loading="achLoading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="成果标题" min-width="160" />
        <el-table-column prop="project_id" label="项目ID" width="90" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="ACH_TAG[row.status]" effect="plain">{{ ACH_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最终得分" width="100">
          <template #default="{ row }">{{ row.final_score ?? '—' }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!achLoading && !achievements.length" description="暂无提交成果" />
    </el-drawer>
  </section>
</template>

<style scoped>
.table-pager { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
