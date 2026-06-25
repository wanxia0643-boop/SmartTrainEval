<script setup>
import { onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { listAchievements } from '../../api/achievements'
import { listEvalResults } from '../../api/evalResults'
import { listIndicators } from '../../api/indicators'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

const ACH_STATUS = { 0: '草稿', 1: '已提交', 2: '评价中', 3: '已评价', 4: '退回重做' }
const ACH_TAG = { 0: 'info', 1: 'primary', 2: 'warning', 3: 'success', 4: 'danger' }
const EVAL_TYPE = { 1: 'AI 评价', 2: '教师评价', 3: '企业导师评价', 4: '学生自评' }
const EVAL_TAG = { 1: 'primary', 2: 'success', 3: 'warning', 4: 'info' }

const loading = ref(false)
const achievements = ref([])
const indicatorMap = ref({})

const drawerVisible = ref(false)
const drawerAch = ref(null)
const evalLoading = ref(false)
const results = ref([])

async function fetchIndicatorMap() {
  const data = await listIndicators({ page: 1, page_size: 200 })
  indicatorMap.value = Object.fromEntries(data.items.map((i) => [i.id, i.indicator_name]))
}

async function fetchAchievements() {
  loading.value = true
  try {
    const data = await listAchievements({ student_id: userStore.userId, page: 1, page_size: 100 })
    achievements.value = data.items
  } finally {
    loading.value = false
  }
}

async function viewFeedback(row) {
  drawerAch.value = row
  drawerVisible.value = true
  evalLoading.value = true
  try {
    const data = await listEvalResults({ achievement_id: row.id, page: 1, page_size: 100 })
    results.value = data.items
  } finally {
    evalLoading.value = false
  }
}

onMounted(async () => {
  await fetchIndicatorMap()
  await fetchAchievements()
})
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">STUDENT · FEEDBACK</p>
        <h2>评价反馈</h2>
        <p>查看导师、企业与 AI 对你实训成果的评价反馈。</p>
      </div>
      <el-button :icon="Refresh" @click="fetchAchievements" :loading="loading">刷新</el-button>
    </div>

    <article class="data-panel">
      <el-table :data="achievements" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="成果标题" min-width="180" />
        <el-table-column prop="project_id" label="项目ID" width="90" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="ACH_TAG[row.status]" effect="plain">{{ ACH_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最终得分" width="100">
          <template #default="{ row }">
            <strong v-if="row.final_score != null" class="score">{{ row.final_score }}</strong>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="viewFeedback(row)">查看评价</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !achievements.length" description="暂无成果与评价" />
    </article>

    <el-drawer v-model="drawerVisible" :title="`${drawerAch?.title || ''} · 评价详情`" size="52%">
      <div v-if="drawerAch" class="final-banner">
        最终综合得分：<strong>{{ drawerAch.final_score ?? '尚未评定' }}</strong>
      </div>
      <div v-loading="evalLoading">
        <div v-for="r in results" :key="r.id" class="eval-card">
          <div class="eval-card-head">
            <span class="indicator">{{ indicatorMap[r.indicator_id] || `指标 #${r.indicator_id}` }}</span>
            <div>
              <el-tag :type="EVAL_TAG[r.eval_type]" effect="plain" size="small">{{ EVAL_TYPE[r.eval_type] }}</el-tag>
              <span class="eval-score">{{ r.score }} 分</span>
            </div>
          </div>
          <p v-if="r.comment" class="eval-text"><b>评语：</b>{{ r.comment }}</p>
          <p v-if="r.suggestion" class="eval-text"><b>建议：</b>{{ r.suggestion }}</p>
        </div>
        <el-empty v-if="!evalLoading && !results.length" description="该成果暂无评价记录" />
      </div>
    </el-drawer>
  </section>
</template>

<style scoped>
.score { color: var(--el-color-primary); font-size: 16px; }
.final-banner {
  padding: 12px 16px; background: var(--el-color-primary-light-9); border-radius: 8px;
  margin-bottom: 16px; color: var(--el-text-color-regular);
}
.final-banner strong { color: var(--el-color-primary); font-size: 18px; }
.eval-card { padding: 12px 0; border-top: 1px solid var(--el-border-color-lighter); }
.eval-card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.indicator { font-weight: 600; }
.eval-score { margin-left: 10px; font-weight: 700; color: var(--el-color-primary); }
.eval-text { margin: 4px 0; color: var(--el-text-color-regular); }
</style>
