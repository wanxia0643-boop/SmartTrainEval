<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, MagicStick, Refresh, Select, Warning } from '@element-plus/icons-vue'
import { aiReview } from '../../api/ai'
import { listProjects } from '../../api/projects'
import { listAchievements, updateAchievement } from '../../api/achievements'
import { listIndicators } from '../../api/indicators'
import { createEvalResult, listEvalResults } from '../../api/evalResults'

const STATUS = {
  0: { label: '草稿', type: 'info' },
  1: { label: '待评价', type: 'warning' },
  2: { label: '评价中', type: 'primary' },
  3: { label: '已评价', type: 'success' },
  4: { label: '退回整改', type: 'danger' },
}

const loading = ref(false)
const detailLoading = ref(false)
const aiLoading = ref(false)
const scoreSubmitting = ref(false)
const batchRunning = ref(false)
const batchProgress = ref(0)
const projects = ref([])
const achievements = ref([])
const selectedProjectId = ref(null)
const selectedAchievement = ref(null)
const selectedRows = ref([])
const statusFilter = ref('pending')
const indicators = ref([])
const scoreRows = ref([])
const reviewCache = ref({})

const currentReview = computed(() => (
  selectedAchievement.value ? reviewCache.value[selectedAchievement.value.id] || null : null
))
const selectedProject = computed(() => projects.value.find((item) => item.id === selectedProjectId.value))
const counts = computed(() => ({
  total: achievements.value.length,
  pending: achievements.value.filter((item) => [1, 2].includes(item.status)).length,
  evaluated: achievements.value.filter((item) => item.status === 3).length,
  returned: achievements.value.filter((item) => item.status === 4).length,
}))
const filteredAchievements = computed(() => {
  if (statusFilter.value === 'pending') return achievements.value.filter((item) => [1, 2].includes(item.status))
  if (statusFilter.value === 'evaluated') return achievements.value.filter((item) => item.status === 3)
  if (statusFilter.value === 'returned') return achievements.value.filter((item) => item.status === 4)
  return achievements.value
})
const completedIndicatorCount = computed(() => scoreRows.value.filter((row) => row.existingId).length)

function formatDate(value) {
  if (!value) return '未提交'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

function statusMeta(status) {
  return STATUS[status] || STATUS[0]
}

async function loadProjects() {
  const data = await listProjects({ page: 1, page_size: 100 })
  projects.value = data.items
  if (!projects.value.some((item) => item.id === selectedProjectId.value)) {
    selectedProjectId.value = projects.value.find((item) => item.status === 1)?.id || projects.value[0]?.id || null
  }
}

async function loadAchievements({ preserveSelection = true } = {}) {
  if (!selectedProjectId.value) {
    achievements.value = []
    selectedAchievement.value = null
    return
  }
  loading.value = true
  try {
    const data = await listAchievements({ project_id: selectedProjectId.value, page: 1, page_size: 100 })
    achievements.value = data.items
    selectedRows.value = []
    const previousId = preserveSelection ? selectedAchievement.value?.id : null
    const next = achievements.value.find((item) => item.id === previousId)
      || achievements.value.find((item) => [1, 2].includes(item.status))
      || achievements.value[0]
      || null
    await selectAchievement(next)
  } finally {
    loading.value = false
  }
}

async function selectAchievement(row) {
  selectedAchievement.value = row || null
  indicators.value = []
  scoreRows.value = []
  if (!row) return
  detailLoading.value = true
  try {
    const [indicatorData, resultData] = await Promise.all([
      listIndicators({ project_id: row.project_id, page: 1, page_size: 100 }),
      listEvalResults({ achievement_id: row.id, page: 1, page_size: 200 }),
    ])
    indicators.value = indicatorData.items.filter((item) => item.status === 1)
    const teacherResults = resultData.items.filter((item) => item.eval_type === 2)
    scoreRows.value = indicators.value.map((indicator) => {
      const existing = teacherResults.find((item) => item.indicator_id === indicator.id)
      return {
        indicatorId: indicator.id,
        name: indicator.indicator_name,
        rule: indicator.scoring_rule,
        weight: Number(indicator.weight || 0),
        maxScore: Number(indicator.max_score || 100),
        score: existing ? Number(existing.score) : 80,
        comment: existing?.comment || '',
        suggestion: existing?.suggestion || '',
        existingId: existing?.id || null,
      }
    })
  } finally {
    detailLoading.value = false
  }
}

async function runReviewFor(achievement, { notify = true } = {}) {
  const data = await aiReview({ achievement_id: achievement.id })
  reviewCache.value = { ...reviewCache.value, [achievement.id]: data }
  if (notify) {
    ElMessage[data.available === false ? 'warning' : 'success'](
      data.available === false ? '模型不可用，已生成稳定的人工复核提示' : 'AI 预评完成',
    )
  }
  return data
}

async function runCurrentReview() {
  if (!selectedAchievement.value) return
  aiLoading.value = true
  try {
    await runReviewFor(selectedAchievement.value)
  } finally {
    aiLoading.value = false
  }
}

async function runBatchReview() {
  const targets = selectedRows.value.filter((item) => [1, 2].includes(item.status)).slice(0, 5)
  if (!targets.length) return ElMessage.warning('请勾选待评价成果，单次最多处理 5 份')
  batchRunning.value = true
  batchProgress.value = 0
  let successCount = 0
  try {
    for (const item of targets) {
      try {
        await runReviewFor(item, { notify: false })
        successCount += 1
      } catch {
        // Keep the remaining queue running when one model request fails.
      }
      batchProgress.value += 1
    }
    ElMessage.success(`批量预评完成：${successCount}/${targets.length} 份已生成复核结果`)
  } finally {
    batchRunning.value = false
  }
}

function adoptAISuggestion() {
  if (!currentReview.value || currentReview.value.available === false) {
    return ElMessage.warning('当前没有可采纳的 AI 评分建议')
  }
  const score = Number(currentReview.value.standard_score || 0)
  scoreRows.value.forEach((row) => {
    row.score = Math.min(row.maxScore, score)
    row.comment = currentReview.value.summary || ''
    row.suggestion = currentReview.value.standard_suggestion || ''
  })
  ElMessage.info('AI 建议已填入草稿，提交前请逐项确认')
}

async function submitAllScores() {
  if (!selectedAchievement.value || !scoreRows.value.length) return
  scoreSubmitting.value = true
  try {
    let finalScore = null
    for (const row of scoreRows.value) {
      const result = await createEvalResult({
        achievement_id: selectedAchievement.value.id,
        indicator_id: row.indicatorId,
        eval_type: 2,
        score: row.score,
        comment: row.comment || null,
        suggestion: row.suggestion || null,
      })
      finalScore = result.final_score
    }
    ElMessage.success(finalScore == null
      ? '教师评价已完成，等待企业导师评价后汇总最终分数'
      : `评价完成，当前最终成绩 ${Number(finalScore).toFixed(1)} 分`)
    await loadAchievements()
  } finally {
    scoreSubmitting.value = false
  }
}

async function returnForRevision() {
  if (!selectedAchievement.value) return
  try {
    await ElMessageBox.confirm(
      `确认退回“${selectedAchievement.value.title}”并生成学生整改任务？`,
      '退回整改',
      { confirmButtonText: '确认退回', cancelButtonText: '取消', type: 'warning' },
    )
  } catch {
    return
  }
  await updateAchievement(selectedAchievement.value.id, { status: 4 })
  ElMessage.success('成果已退回，学生整改任务已生成')
  await loadAchievements({ preserveSelection: false })
}

function handleSelectionChange(rows) {
  selectedRows.value = rows
}

onMounted(async () => {
  await loadProjects()
  await loadAchievements({ preserveSelection: false })
})
</script>

<template>
  <section class="feature-page evaluation-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">TEACHER · HUMAN IN THE LOOP</p>
        <h2>智能评价工作台</h2>
        <p>AI 先定位完整性与逻辑风险，教师再按项目量规逐项确认，模型结果不会直接写入成绩。</p>
      </div>
      <el-tag type="success" effect="plain">人工最终确认</el-tag>
    </div>

    <section class="evaluation-toolbar data-panel">
      <div class="project-select">
        <span>实训项目</span>
        <el-select v-model="selectedProjectId" filterable placeholder="选择项目" @change="loadAchievements({ preserveSelection: false })">
          <el-option v-for="project in projects" :key="project.id" :label="project.project_name" :value="project.id" />
        </el-select>
      </div>
      <div class="toolbar-actions">
        <span v-if="batchRunning">正在预评 {{ batchProgress }}/{{ Math.min(selectedRows.length, 5) }}</span>
        <el-button :icon="MagicStick" :loading="batchRunning" @click="runBatchReview">批量 AI 预评</el-button>
        <el-button :icon="Refresh" :loading="loading" circle title="刷新成果" @click="loadAchievements()" />
      </div>
    </section>

    <section class="stats-strip" aria-label="评价进度">
      <article><span>项目成果</span><strong>{{ counts.total }}</strong></article>
      <article><span>待人工评价</span><strong>{{ counts.pending }}</strong></article>
      <article><span>已完成评价</span><strong>{{ counts.evaluated }}</strong></article>
      <article><span>退回整改</span><strong>{{ counts.returned }}</strong></article>
    </section>

    <div class="workspace-grid">
      <article class="data-panel queue-panel">
        <div class="panel-heading queue-heading">
          <div>
            <h3>成果评审队列</h3>
            <span>{{ selectedProject?.project_name || '请选择项目' }}</span>
          </div>
          <el-segmented v-model="statusFilter" :options="[
            { label: '待评', value: 'pending' },
            { label: '已评', value: 'evaluated' },
            { label: '退回', value: 'returned' },
            { label: '全部', value: 'all' },
          ]" />
        </div>

        <el-table
          v-loading="loading"
          :data="filteredAchievements"
          row-key="id"
          highlight-current-row
          @current-change="selectAchievement"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="44" />
          <el-table-column label="成果" min-width="230">
            <template #default="{ row }">
              <div class="achievement-cell">
                <strong>{{ row.title }}</strong>
                <span>学生 #{{ row.student_id }} · {{ formatDate(row.submit_time) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusMeta(row.status).type" effect="plain">{{ statusMeta(row.status).label }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="成绩" width="84" align="right">
            <template #default="{ row }">{{ row.final_score == null ? '—' : Number(row.final_score).toFixed(1) }}</template>
          </el-table-column>
          <el-table-column label="AI" width="72" align="center">
            <template #default="{ row }">
              <el-icon :class="reviewCache[row.id] ? 'ai-done' : 'ai-empty'">
                <Check v-if="reviewCache[row.id]" /><MagicStick v-else />
              </el-icon>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && !filteredAchievements.length" description="当前筛选下没有成果" />
      </article>

      <aside class="detail-column" v-loading="detailLoading">
        <template v-if="selectedAchievement">
          <article class="data-panel evidence-panel">
            <div class="panel-heading">
              <div>
                <h3>{{ selectedAchievement.title }}</h3>
                <span>{{ formatDate(selectedAchievement.submit_time) }}</span>
              </div>
              <el-tag :type="statusMeta(selectedAchievement.status).type" effect="plain">
                {{ statusMeta(selectedAchievement.status).label }}
              </el-tag>
            </div>
            <p class="achievement-content">{{ selectedAchievement.content || '学生未填写文字说明，请结合附件和仓库证据复核。' }}</p>
            <div class="evidence-links">
              <a v-if="selectedAchievement.attachment_url" :href="selectedAchievement.attachment_url" target="_blank" rel="noreferrer">查看成果附件</a>
              <a v-if="selectedAchievement.repo_url" :href="selectedAchievement.repo_url" target="_blank" rel="noreferrer">打开代码仓库</a>
              <span v-if="!selectedAchievement.attachment_url && !selectedAchievement.repo_url">暂无附件或仓库链接</span>
            </div>
          </article>

          <article class="data-panel ai-review-panel">
            <div class="panel-heading">
              <div><h3>AI 预评建议</h3><span>只提供复核线索，不计入最终成绩</span></div>
              <el-button type="primary" :icon="MagicStick" :loading="aiLoading" @click="runCurrentReview">
                {{ currentReview ? '重新预评' : '开始预评' }}
              </el-button>
            </div>
            <template v-if="currentReview">
              <div class="review-score">
                <strong>{{ currentReview.standard_score }}</strong>
                <div><span>规范建议分</span><small>{{ currentReview.available === false ? '模型降级，不可采纳' : '需教师确认' }}</small></div>
              </div>
              <div class="review-flags">
                <span :class="{ danger: !currentReview.function_check?.is_complete }">功能{{ currentReview.function_check?.is_complete ? '完整' : '待补' }}</span>
                <span :class="{ danger: currentReview.logic_check?.has_risk }">逻辑{{ currentReview.logic_check?.has_risk ? '有风险' : '正常' }}</span>
                <span :class="{ danger: !currentReview.step_check?.is_complete }">过程{{ currentReview.step_check?.is_complete ? '完整' : '待补' }}</span>
              </div>
              <p>{{ currentReview.summary }}</p>
              <ul v-if="currentReview.function_check?.problem_list?.length || currentReview.logic_check?.risk_list?.length">
                <li v-for="item in [...(currentReview.function_check?.problem_list || []), ...(currentReview.logic_check?.risk_list || [])]" :key="item">{{ item }}</li>
              </ul>
              <el-button :disabled="currentReview.available === false" @click="adoptAISuggestion">填入评分草稿</el-button>
            </template>
            <div v-else class="empty-review"><MagicStick /><span>运行预评后，这里会展示完整性、逻辑和过程风险。</span></div>
          </article>

          <article class="data-panel rubric-panel">
            <div class="panel-heading">
              <div>
                <h3>教师量规评分</h3>
                <span>已保存 {{ completedIndicatorCount }}/{{ scoreRows.length }} 项</span>
              </div>
            </div>
            <div v-for="row in scoreRows" :key="row.indicatorId" class="rubric-row">
              <div class="rubric-meta">
                <strong>{{ row.name }}</strong>
                <span>权重 {{ row.weight }}% · {{ row.rule || '请依据成果证据综合判断' }}</span>
              </div>
              <el-input-number v-model="row.score" :min="0" :max="row.maxScore" controls-position="right" />
              <el-input v-model="row.comment" placeholder="评价依据与表现" />
              <el-input v-model="row.suggestion" placeholder="下一步改进建议" />
            </div>
            <el-empty v-if="!scoreRows.length" description="当前项目未配置启用的评价指标" />
            <div class="rubric-actions">
              <el-button type="danger" plain :icon="Warning" @click="returnForRevision">退回整改</el-button>
              <el-button type="primary" :icon="Select" :loading="scoreSubmitting" :disabled="!scoreRows.length" @click="submitAllScores">确认并提交全部评分</el-button>
            </div>
          </article>
        </template>
        <article v-else class="data-panel empty-detail"><el-empty description="从左侧选择一份成果开始评价" /></article>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.evaluation-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 16px; }
.project-select, .toolbar-actions { display: flex; align-items: center; gap: 10px; }
.project-select > span, .toolbar-actions > span { color: var(--ste-muted); font-size: 12px; }
.project-select .el-select { width: 320px; }
.stats-strip { display: grid; grid-template-columns: repeat(4, 1fr); margin: 16px 0; border: 1px solid var(--ste-border); background: #fff; }
.stats-strip article { display: flex; align-items: baseline; justify-content: space-between; min-height: 78px; padding: 18px 20px; border-right: 1px solid var(--ste-border); }
.stats-strip article:last-child { border-right: 0; }
.stats-strip span { color: var(--ste-muted); font-size: 13px; }
.stats-strip strong { color: var(--ste-text); font-size: 26px; }
.workspace-grid { display: grid; grid-template-columns: minmax(420px, .8fr) minmax(0, 1.2fr); gap: 16px; align-items: start; }
.queue-panel { overflow: hidden; }
.queue-heading { align-items: center; }
.queue-panel .el-table { padding: 0 10px 12px; }
.achievement-cell { display: grid; gap: 5px; }
.achievement-cell strong { color: var(--ste-text); font-size: 13px; }
.achievement-cell span { color: var(--ste-muted); font-size: 11px; }
.ai-done { color: var(--el-color-success); }.ai-empty { color: #aab5c5; }
.detail-column { display: grid; gap: 16px; min-height: 520px; }
.evidence-panel, .ai-review-panel, .rubric-panel { padding: 0 18px 18px; }
.achievement-content { max-height: 120px; overflow: auto; color: #46566f; font-size: 13px; line-height: 1.75; white-space: pre-wrap; }
.evidence-links { display: flex; gap: 14px; color: var(--ste-muted); font-size: 12px; }
.evidence-links a { color: var(--ste-primary); text-decoration: none; }
.review-score { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.review-score > strong { display: grid; place-items: center; width: 56px; height: 56px; color: #fff; font-size: 22px; background: #245edb; border-radius: 50%; }
.review-score div { display: grid; gap: 4px; }.review-score span { font-weight: 600; }.review-score small { color: var(--ste-muted); }
.review-flags { display: flex; flex-wrap: wrap; gap: 8px; }
.review-flags span { padding: 5px 8px; color: #13765b; font-size: 11px; background: #eaf8f3; border-radius: 4px; }
.review-flags span.danger { color: #b54545; background: #fff0f0; }
.ai-review-panel p, .ai-review-panel li { color: #536176; font-size: 12px; line-height: 1.65; }
.empty-review { display: flex; align-items: center; gap: 9px; min-height: 80px; color: var(--ste-muted); font-size: 12px; }
.empty-review svg { width: 20px; }
.rubric-row { display: grid; grid-template-columns: minmax(180px, 1fr) 116px; gap: 10px; align-items: center; padding: 12px 0; border-top: 1px solid var(--ste-border); }
.rubric-row > .el-input { grid-column: 1 / -1; }
.rubric-meta { display: grid; gap: 5px; }.rubric-meta strong { font-size: 13px; }.rubric-meta span { color: var(--ste-muted); font-size: 11px; line-height: 1.45; }
.rubric-actions { display: flex; justify-content: flex-end; gap: 8px; padding-top: 16px; border-top: 1px solid var(--ste-border); }
.empty-detail { display: grid; place-items: center; min-height: 520px; }
@media (max-width: 1250px) { .workspace-grid { grid-template-columns: 1fr; } }
@media (max-width: 760px) { .evaluation-toolbar, .project-select, .toolbar-actions { align-items: stretch; flex-direction: column; }.project-select .el-select { width: 100%; }.stats-strip { grid-template-columns: repeat(2, 1fr); }.stats-strip article:nth-child(2) { border-right: 0; }.rubric-row { grid-template-columns: 1fr; }.rubric-row > .el-input { grid-column: auto; }.rubric-actions { flex-direction: column-reverse; } }
</style>
