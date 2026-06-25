<script setup>
import { computed, onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { listOrgs } from '../../api/orgs'

const ORG_TYPE = { 1: '学校', 2: '学院', 3: '专业', 4: '班级', 5: '企业' }
// 合作院校：展示学校 / 学院 / 专业层级
const SCHOOL_TYPES = [1, 2, 3]

const loading = ref(false)
const allOrgs = ref([])
const rows = computed(() => allOrgs.value.filter((o) => SCHOOL_TYPES.includes(o.org_type)))

async function fetchOrgs() {
  loading.value = true
  try {
    const data = await listOrgs({ page: 1, page_size: 100 })
    allOrgs.value = data.items
  } finally {
    loading.value = false
  }
}

onMounted(fetchOrgs)
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">ENTERPRISE · SCHOOLS</p>
        <h2>合作院校</h2>
        <p>维护合作院校与实训项目关系。</p>
      </div>
      <el-button :icon="Refresh" @click="fetchOrgs" :loading="loading">刷新</el-button>
    </div>

    <article class="data-panel">
      <el-table :data="rows" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="org_name" label="名称" min-width="160" />
        <el-table-column prop="org_code" label="编码" min-width="120" />
        <el-table-column label="类型" width="90">
          <template #default="{ row }">
            <el-tag effect="plain">{{ ORG_TYPE[row.org_type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="负责人" min-width="100">
          <template #default="{ row }">{{ row.leader || '—' }}</template>
        </el-table-column>
        <el-table-column label="联系电话" min-width="120">
          <template #default="{ row }">{{ row.contact || '—' }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !rows.length" description="暂无合作院校" />
    </article>
  </section>
</template>
