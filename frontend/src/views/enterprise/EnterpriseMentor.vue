<script setup>
import { onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { listUsers } from '../../api/users'
import { listRoles } from '../../api/roles'

const loading = ref(false)
const rows = ref([])

async function fetchMentors() {
  loading.value = true
  try {
    const roles = await listRoles()
    const roleId = roles.find((r) => r.role_code === 'ENTERPRISE')?.id
    const params = { page: 1, page_size: 100 }
    if (roleId) params.role_id = roleId
    const data = await listUsers(params)
    rows.value = data.items
  } finally {
    loading.value = false
  }
}

onMounted(fetchMentors)
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">ENTERPRISE · MENTORS</p>
        <h2>企业导师</h2>
        <p>协同企业导师处理指导与反馈事项。</p>
      </div>
      <el-button :icon="Refresh" @click="fetchMentors" :loading="loading">刷新</el-button>
    </div>

    <article class="data-panel">
      <el-table :data="rows" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="账号" min-width="120" />
        <el-table-column prop="real_name" label="姓名" min-width="100" />
        <el-table-column label="邮箱" min-width="160">
          <template #default="{ row }">{{ row.email || '—' }}</template>
        </el-table-column>
        <el-table-column label="手机号" min-width="120">
          <template #default="{ row }">{{ row.phone || '—' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" effect="plain">
              {{ row.status === 1 ? '在岗' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !rows.length" description="暂无企业导师" />
    </article>
  </section>
</template>
