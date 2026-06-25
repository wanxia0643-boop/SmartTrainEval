<script setup>
import { computed, onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { listAchievements } from '../../api/achievements'
import { listEvalResults } from '../../api/evalResults'
import { listIndicators } from '../../api/indicators'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

const loading = ref(false)
const achievements = ref([])
const indicatorMap = ref({})
const competency = ref([]) // [{ name, avg }]

const submittedCount = computed(() => achievements.value.length)
const evaluatedCount = computed(() => achievements.value.filter((a) => a.status === 3).length)
const avgScore = computed(() => {
  const scored = achievements.value.filter((a) => a.final_score != null)
  if (!scored.length) return null
  const sum = scored.reduce((s, a) => s + Number(a.final_score), 0)
  return Math.round((sum / scored.length) * 10) / 10
})

async function loadAll() {
  loading.value = true
  try {
    const [achData, indData] = await Promise.all([
      listAchievements({ student_id: userStore.userId, page: 1, page_size: 100 }),
      listIndicators({ page: 1, page_size: 200 }),
    ])
    achievements.value = achData.items
    indicatorMap.value = Object.fromEntries(indData.items.map((i) => [i.id, i.indicator_name]))

    // 汇总各指标平均得分
    const buckets = {}
    const resultsArr = await Promise.all(
      achievements.value.map((a) =>
        listEvalResults({ achievement_id: a.id, page: 1, page_size: 100 }).then((d) => d.items).catch(() => []),
      ),
    )
    for (const items of resultsArr) {
      for (const r of items) {
        if (!buckets[r.indicator_id]) buckets[r.indicator_id] = { sum: 0, n: 0 }
        buckets[r.indicator_id].sum += Number(r.score)
        buckets[r.indicator_id].n += 1
      }
    }
    competency.value = Object.entries(buckets).map(([id, b]) => ({
      name: indicatorMap.value[id] || `指标 #${id}`,
      avg: Math.round((b.sum / b.n) * 10) / 10,
    })).sort((a, b) => b.avg - a.avg)
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
        <p class="page-eyebrow">STUDENT · GROWTH</p>
        <h2>成长档案</h2>
        <p>沉淀你的实训成果、能力图谱与评价轨迹。</p>
      </div>
      <el-button :icon="Refresh" @click="loadAll" :loading="loading">刷新</el-button>
    </div>

    <div class="stat-grid">
      <article class="data-panel stat-card"><span>提交成果</span><strong>{{ submittedCount }}</strong></article>
      <article class="data-panel stat-card"><span>已评价</span><strong>{{ evaluatedCount }}</strong></article>
      <article class="data-panel stat-card"><span>平均得分</span><strong>{{ avgScore ?? '—' }}</strong></article>
    </div>

    <article class="data-panel">
      <div class="panel-head"><strong>能力图谱（各指标平均得分）</strong></div>
      <div v-if="competency.length" class="competency">
        <div v-for="c in competency" :key="c.name" class="competency-row">
          <span class="c-name">{{ c.name }}</span>
          <el-progress :percentage="Math.min(100, c.avg)" :stroke-width="14" />
          <span class="c-val">{{ c.avg }}</span>
        </div>
      </div>
      <el-empty v-else description="暂无评价数据，完成评价后生成能力图谱" />
    </article>

    <article class="data-panel">
      <div class="panel-head"><strong>成果轨迹</strong></div>
      <el-timeline v-if="achievements.length">
        <el-timeline-item
          v-for="a in achievements" :key="a.id"
          :timestamp="a.submit_time || a.create_time" placement="top"
        >
          <strong>{{ a.title }}</strong>
          <span v-if="a.final_score != null" class="trace-score">得分 {{ a.final_score }}</span>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="还没有成果记录" />
    </article>
  </section>
</template>

<style scoped>
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }
.stat-card { display: flex; flex-direction: column; gap: 6px; }
.stat-card span { color: var(--el-text-color-secondary); font-size: 13px; }
.stat-card strong { font-size: 28px; color: var(--el-color-primary); }
.panel-head { margin-bottom: 12px; }
.data-panel + .data-panel { margin-top: 16px; }
.competency-row { display: grid; grid-template-columns: 120px 1fr 48px; align-items: center; gap: 12px; margin: 10px 0; }
.c-name { font-size: 14px; }
.c-val { font-weight: 700; color: var(--el-color-primary); text-align: right; }
.trace-score { margin-left: 10px; color: var(--el-color-primary); font-weight: 600; }
</style>
