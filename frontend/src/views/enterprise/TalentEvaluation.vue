<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, MagicStick, Refresh, Select, TrendCharts } from '@element-plus/icons-vue'
import { listProjects } from '../../api/projects'
import { listAchievements } from '../../api/achievements'
import { listIndicators } from '../../api/indicators'
import { createEvalResult, listEvalResults } from '../../api/evalResults'
import { generateEnterpriseEvidence, listAIAnalyses } from '../../api/aiAgent'

const STATUS = {
  0: { label: '草稿', type: 'info' },
  1: { label: '待评价', type: 'warning' },
  2: { label: '多方评价中', type: 'primary' },
  3: { label: '已完成', type: 'success' },
  4: { label: '退回整改', type: 'danger' },
}

const loading = ref(false)
const detailLoading = ref(false)
const evidenceLoading = ref(false)
const submitting = ref(false)
const projects = ref([])
const achievements = ref([])
const selectedProjectId = ref(null)
const selectedAchievement = ref(null)
const statusFilter = ref('pending')
const scoreRows = ref([])
const teacherResultCount = ref(0)
const evidenceCache = ref({})

const selectedProject = computed(() => projects.value.find((item) => item.id === selectedProjectId.value))
const currentEvidence = computed(() => (
  selectedAchievement.value ? evidenceCache.value[selectedAchievement.value.id] || null : null
))
const enterpriseResultCount = computed(() => scoreRows.value.filter((item) => item.existingId).length)
const enterpriseComplete = computed(() => (
  scoreRows.value.length > 0 && enterpriseResultCount.value === scoreRows.value.length
))
const counts = computed(() => ({
  total: achievements.value.length,
  pending: achievements.value.filter((item) => [1, 2].includes(item.status)).length,
  completed: achievements.value.filter((item) => item.status === 3).length,
  evidenced: achievements.value.filter((item) => evidenceCache.value[item.id]).length,
}))
const filteredAchievements = computed(() => {
  if (statusFilter.value === 'pending') return achievements.value.filter((item) => [1, 2].includes(item.status))
  if (statusFilter.value === 'completed') return achievements.value.filter((item) => item.status === 3)
  if (statusFilter.value === 'returned') return achievements.value.filter((item) => item.status === 4)
  return achievements.value
})

function formatDate(value) {
  if (!value) return '未提交'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

function statusMeta(status) {
  return STATUS[status] || STATUS[0]
}

async function loadContext() {
  loading.value = true
  try {
    const [projectData, historyData] = await Promise.all([
      listProjects({ page: 1, page_size: 100 }),
      listAIAnalyses({ scene: 'ENTERPRISE_EVIDENCE', page: 1, page_size: 100 }),
    ])
    projects.value = projectData.items
    const history = {}
    historyData.items.forEach((item) => {
      if (!history[item.biz_id]) {
        history[item.biz_id] = {
          ...item.result,
          citations: item.citations || [],
          available: item.status === 1,
          analysis_id: item.id,
          model_name: item.model_name,
        }
      }
    })
    evidenceCache.value = history
    if (!projects.value.some((item) => item.id === selectedProjectId.value)) {
      selectedProjectId.value = projects.value.find((item) => item.status === 1)?.id || projects.value[0]?.id || null
    }
    await loadAchievements({ preserveSelection: false })
  } finally {
    loading.value = false
  }
}

async function loadAchievements({ preserveSelection = true } = {}) {
  if (!selectedProjectId.value) {
    achievements.value = []
    selectedAchievement.value = null
    scoreRows.value = []
    return
  }
  loading.value = true
  try {
    const data = await listAchievements({ project_id: selectedProjectId.value, page: 1, page_size: 100 })
    achievements.value = data.items
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
  scoreRows.value = []
  teacherResultCount.value = 0
  if (!row) return
  detailLoading.value = true
  try {
    const [indicatorData, resultData] = await Promise.all([
      listIndicators({ project_id: row.project_id, page: 1, page_size: 100 }),
      listEvalResults({ achievement_id: row.id, page: 1, page_size: 200 }),
    ])
    const indicators = indicatorData.items.filter((item) => item.status === 1)
    const enterpriseResults = resultData.items.filter((item) => item.eval_type === 3)
    teacherResultCount.value = resultData.items.filter((item) => item.eval_type === 2).length
    scoreRows.value = indicators.map((indicator) => {
      const existing = enterpriseResults.find((item) => item.indicator_id === indicator.id)
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

async function runEvidenceAnalysis() {
  if (!selectedAchievement.value) return
  evidenceLoading.value = true
  try {
    const data = await generateEnterpriseEvidence(selectedAchievement.value.id)
    evidenceCache.value = {
      ...evidenceCache.value,
      [selectedAchievement.value.id]: data,
    }
    ElMessage[data.available === false ? 'warning' : 'success'](
      data.available === false ? '模型不可用，已返回人工证据核验清单' : '岗位能力证据已生成',
    )
  } finally {
    evidenceLoading.value = false
  }
}

function applyEvidenceNotes() {
  const evidence = currentEvidence.value
  const competencies = evidence?.competencies || []
  if (!competencies.length) return ElMessage.warning('当前没有可引用的岗位能力证据')
  const missing = (evidence.missing_evidence || []).join('、')
  scoreRows.value.forEach((row, index) => {
    const competency = competencies[index % competencies.length]
    if (!row.comment) {
      row.comment = `岗位证据：${competency.name}（${competency.level}）— ${competency.evidence}`
    }
    if (!row.suggestion && missing) {
      row.suggestion = `建议补充：${missing}`
    }
  })
  ElMessage.info('证据已引用到空白评语，分数未被 AI 修改')
}

async function submitAllScores() {
  if (!selectedAchievement.value || !scoreRows.value.length) return
  try {
    await ElMessageBox.confirm(
      `确认提交“${selectedAchievement.value.title}”的全部企业评价？提交后系统将按教师 60% + 企业 40% 汇总。`,
      '确认企业评价',
      { confirmButtonText: '确认提交', cancelButtonText: '继续检查', type: 'warning' },
    )
  } catch {
    return
  }
  submitting.value = true
  try {
    let finalScore = null
    for (const row of scoreRows.value) {
      const result = await createEvalResult({
        achievement_id: selectedAchievement.value.id,
        indicator_id: row.indicatorId,
        eval_type: 3,
        score: row.score,
        comment: row.comment || null,
        suggestion: row.suggestion || null,
      })
      finalScore = result.final_score
    }
    ElMessage.success(finalScore == null
      ? '企业评价已保存，等待教师完成量规后生成最终成绩'
      : `多方评价完成，最终成绩 ${Number(finalScore).toFixed(1)} 分`)
    await loadAchievements()
  } finally {
    submitting.value = false
  }
}

onMounted(loadContext)
</script>

<template>
  <section class="feature-page talent-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">ENTERPRISE · EVIDENCE BASED REVIEW</p>
        <h2>岗位证据评价工作台</h2>
        <p>从真实成果中提取岗位能力证据，由企业导师按项目量规完成人工评价。</p>
      </div>
      <el-tag type="success" effect="plain">企业评价权重 40%</el-tag>
    </div>

    <section class="context-toolbar data-panel">
      <div class="project-select">
        <span>分配项目</span>
        <el-select v-model="selectedProjectId" filterable placeholder="选择项目" @change="loadAchievements({ preserveSelection: false })">
          <el-option v-for="project in projects" :key="project.id" :label="project.project_name" :value="project.id" />
        </el-select>
      </div>
      <div class="toolbar-copy">
        <span>{{ selectedProject?.project_code || '暂无项目' }}</span>
        <el-button :icon="Refresh" :loading="loading" circle title="刷新项目与成果" @click="loadContext" />
      </div>
    </section>

    <section class="stats-strip" aria-label="企业评价进度">
      <article><span>可评成果</span><strong>{{ counts.total }}</strong></article>
      <article><span>多方评价中</span><strong>{{ counts.pending }}</strong></article>
      <article><span>已形成最终分</span><strong>{{ counts.completed }}</strong></article>
      <article><span>AI 证据记录</span><strong>{{ counts.evidenced }}</strong></article>
    </section>

    <div class="talent-workspace">
      <article class="data-panel queue-panel">
        <div class="panel-heading queue-heading">
          <div>
            <h3>企业成果队列</h3>
            <span>仅展示分配给当前企业导师的项目成果</span>
          </div>
          <el-segmented v-model="statusFilter" :options="[
            { label: '待评', value: 'pending' },
            { label: '已完成', value: 'completed' },
            { label: '退回', value: 'returned' },
            { label: '全部', value: 'all' },
          ]" />
        </div>
        <el-table
          v-loading="loading"
          :data="filteredAchievements"
          row-key="id"
          highlight-current-row
          @row-click="selectAchievement"
        >
          <el-table-column label="成果" min-width="230">
            <template #default="{ row }">
              <div class="achievement-cell">
                <strong>{{ row.title }}</strong>
                <span>学生 #{{ row.student_id }} · {{ formatDate(row.submit_time) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="112">
            <template #default="{ row }">
              <el-tag :type="statusMeta(row.status).type" effect="plain">{{ statusMeta(row.status).label }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="最终分" width="82" align="right">
            <template #default="{ row }">{{ row.final_score == null ? '—' : Number(row.final_score).toFixed(1) }}</template>
          </el-table-column>
          <el-table-column label="证据" width="72" align="center">
            <template #default="{ row }">
              <el-icon :class="evidenceCache[row.id] ? 'evidence-done' : 'evidence-empty'">
                <Check v-if="evidenceCache[row.id]" /><MagicStick v-else />
              </el-icon>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && !filteredAchievements.length" description="当前筛选下没有成果" />
      </article>

      <aside class="detail-column" v-loading="detailLoading">
        <template v-if="selectedAchievement">
          <article class="data-panel achievement-panel">
            <div class="panel-heading">
              <div>
                <h3>{{ selectedAchievement.title }}</h3>
                <span>{{ formatDate(selectedAchievement.submit_time) }}</span>
              </div>
              <el-tag :type="statusMeta(selectedAchievement.status).type" effect="plain">
                {{ statusMeta(selectedAchievement.status).label }}
              </el-tag>
            </div>
            <p class="achievement-content">{{ selectedAchievement.content || '学生未填写文字说明，请结合附件和仓库材料核验。' }}</p>
            <div class="achievement-footer">
              <div class="evidence-links">
                <a v-if="selectedAchievement.attachment_url" :href="selectedAchievement.attachment_url" target="_blank" rel="noreferrer">查看成果附件</a>
                <a v-if="selectedAchievement.repo_url" :href="selectedAchievement.repo_url" target="_blank" rel="noreferrer">打开代码仓库</a>
                <span v-if="!selectedAchievement.attachment_url && !selectedAchievement.repo_url">暂无附件或仓库链接</span>
              </div>
              <div class="review-progress">
                <span>教师 {{ teacherResultCount }}/{{ scoreRows.length }}</span>
                <span :class="{ complete: enterpriseComplete }">企业 {{ enterpriseResultCount }}/{{ scoreRows.length }}</span>
              </div>
            </div>
          </article>

          <article class="data-panel ai-evidence-panel">
            <div class="panel-heading">
              <div>
                <h3>AI 岗位能力证据</h3>
                <span>结合成果、量规、教师评价和岗位资料，仅提供证据线索</span>
              </div>
              <el-button type="primary" :icon="MagicStick" :loading="evidenceLoading" @click="runEvidenceAnalysis">
                {{ currentEvidence ? '重新分析' : '生成证据' }}
              </el-button>
            </div>

            <template v-if="currentEvidence">
              <div class="evidence-context">
                <span>{{ currentEvidence.available === false ? '规则降级结果' : 'AI 分析完成' }}</span>
                <span v-if="currentEvidence.context_summary">量规 {{ currentEvidence.context_summary.indicator_count }} 项</span>
                <span v-if="currentEvidence.context_summary">教师评价 {{ currentEvidence.context_summary.teacher_result_count }} 项</span>
                <span v-if="currentEvidence.context_summary">岗位资料 {{ currentEvidence.context_summary.knowledge_source_count }} 条</span>
              </div>
              <div class="competency-list">
                <div v-for="item in currentEvidence.competencies || []" :key="`${item.name}-${item.level}`" class="competency-row">
                  <div><strong>{{ item.name }}</strong><el-tag size="small" effect="plain">{{ item.level }}</el-tag></div>
                  <p>{{ item.evidence }}</p>
                </div>
              </div>
              <div class="evidence-columns">
                <section>
                  <h4>待补证据</h4>
                  <div class="missing-tags">
                    <el-tag v-for="item in currentEvidence.missing_evidence || []" :key="item" type="warning" effect="plain">{{ item }}</el-tag>
                  </div>
                </section>
                <section>
                  <h4>面试追问</h4>
                  <ol><li v-for="item in currentEvidence.interview_questions || []" :key="item">{{ item }}</li></ol>
                </section>
              </div>
              <div v-if="currentEvidence.citations?.length" class="citation-line">
                <strong>资料来源</strong>
                <span v-for="item in currentEvidence.citations" :key="item.chunk_id">{{ item.title }} · {{ item.source_label }}</span>
              </div>
              <div class="evidence-note">
                <p>{{ currentEvidence.review_note }}</p>
                <el-button :icon="TrendCharts" @click="applyEvidenceNotes">仅引用证据到评语</el-button>
              </div>
            </template>
            <div v-else class="empty-evidence">
              <MagicStick />
              <span>生成后展示岗位能力证据、缺失材料和可用于答辩的追问问题。</span>
            </div>
          </article>

          <article class="data-panel rubric-panel">
            <div class="panel-heading">
              <div>
                <h3>企业导师量规评价</h3>
                <span>已保存 {{ enterpriseResultCount }}/{{ scoreRows.length }} 项，最终成绩由教师 60% + 企业 40% 汇总</span>
              </div>
            </div>
            <div v-for="row in scoreRows" :key="row.indicatorId" class="rubric-row">
              <div class="rubric-meta">
                <strong>{{ row.name }}</strong>
                <span>权重 {{ row.weight }}% · {{ row.rule || '请依据岗位能力证据综合判断' }}</span>
              </div>
              <el-input-number v-model="row.score" :min="0" :max="row.maxScore" controls-position="right" />
              <el-input v-model="row.comment" type="textarea" :rows="2" placeholder="说明支撑该评分的成果证据" />
              <el-input v-model="row.suggestion" type="textarea" :rows="2" placeholder="给出面向岗位能力的改进建议" />
            </div>
            <el-empty v-if="!scoreRows.length" description="当前项目未配置启用的评价指标" />
            <div class="rubric-actions">
              <span>AI 不会修改分数，企业导师保留最终评价决定权</span>
              <el-button
                type="primary"
                :icon="Select"
                :loading="submitting"
                :disabled="!scoreRows.length || selectedAchievement.status === 4"
                @click="submitAllScores"
              >确认并提交全部评价</el-button>
            </div>
          </article>
        </template>
        <article v-else class="data-panel empty-detail"><el-empty description="从左侧选择一份成果开始岗位评价" /></article>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.context-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 16px; }
.project-select, .toolbar-copy { display: flex; align-items: center; gap: 10px; }
.project-select > span, .toolbar-copy > span { color: var(--ste-muted); font-size: 12px; }
.project-select .el-select { width: 320px; }
.stats-strip { display: grid; grid-template-columns: repeat(4, 1fr); margin: 16px 0; background: #fff; border: 1px solid var(--ste-border); }
.stats-strip article { display: flex; align-items: baseline; justify-content: space-between; min-height: 78px; padding: 18px 20px; border-right: 1px solid var(--ste-border); }
.stats-strip article:last-child { border-right: 0; }
.stats-strip span { color: var(--ste-muted); font-size: 13px; }
.stats-strip strong { color: var(--ste-text); font-size: 26px; }
.talent-workspace { display: grid; grid-template-columns: minmax(420px, .8fr) minmax(0, 1.2fr); gap: 16px; align-items: start; }
.queue-panel { overflow: hidden; }
.queue-heading { align-items: center; }
.queue-panel .el-table { padding: 0 10px 12px; cursor: pointer; }
.achievement-cell { display: grid; gap: 5px; }
.achievement-cell strong { color: var(--ste-text); font-size: 13px; }
.achievement-cell span { color: var(--ste-muted); font-size: 11px; }
.evidence-done { color: var(--el-color-success); }
.evidence-empty { color: #aab5c5; }
.detail-column { display: grid; gap: 16px; min-height: 540px; }
.achievement-panel, .ai-evidence-panel, .rubric-panel { padding: 0 18px 18px; }
.achievement-content { max-height: 120px; overflow: auto; color: #46566f; font-size: 13px; line-height: 1.75; white-space: pre-wrap; }
.achievement-footer { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.evidence-links, .review-progress { display: flex; flex-wrap: wrap; gap: 10px; color: var(--ste-muted); font-size: 12px; }
.evidence-links a { color: var(--ste-primary); text-decoration: none; }
.review-progress span { padding: 4px 7px; background: #f3f6fa; border-radius: 4px; }
.review-progress span.complete { color: #13765b; background: #eaf8f3; }
.evidence-context { display: flex; flex-wrap: wrap; gap: 8px; margin: 2px 0 14px; }
.evidence-context span { padding: 5px 8px; color: #35516f; font-size: 11px; background: #edf3fa; border-radius: 4px; }
.competency-list { border-top: 1px solid var(--ste-border); }
.competency-row { display: grid; grid-template-columns: minmax(130px, .35fr) minmax(0, 1fr); gap: 16px; padding: 13px 0; border-bottom: 1px solid var(--ste-border); }
.competency-row > div { display: flex; align-items: center; gap: 8px; }
.competency-row strong { font-size: 13px; }
.competency-row p { margin: 0; color: #526176; font-size: 12px; line-height: 1.65; }
.evidence-columns { display: grid; grid-template-columns: .8fr 1.2fr; gap: 20px; padding: 14px 0; }
.evidence-columns h4, .citation-line > strong { margin: 0 0 9px; color: #344158; font-size: 12px; }
.missing-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.evidence-columns ol { margin: 0; padding-left: 18px; color: #526176; font-size: 12px; line-height: 1.7; }
.citation-line { display: flex; flex-wrap: wrap; gap: 7px; padding: 11px 0; border-top: 1px solid var(--ste-border); }
.citation-line > strong { width: 100%; }
.citation-line span { color: #526176; font-size: 11px; }
.evidence-note { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding-top: 12px; border-top: 1px solid var(--ste-border); }
.evidence-note p { margin: 0; color: var(--ste-muted); font-size: 11px; }
.empty-evidence { display: flex; align-items: center; gap: 9px; min-height: 100px; color: var(--ste-muted); font-size: 12px; }
.empty-evidence svg { width: 20px; }
.rubric-row { display: grid; grid-template-columns: minmax(180px, 1fr) 116px; gap: 10px; align-items: center; padding: 13px 0; border-top: 1px solid var(--ste-border); }
.rubric-row > .el-textarea { grid-column: 1 / -1; }
.rubric-meta { display: grid; gap: 5px; }
.rubric-meta strong { font-size: 13px; }
.rubric-meta span { color: var(--ste-muted); font-size: 11px; line-height: 1.45; }
.rubric-actions { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding-top: 16px; border-top: 1px solid var(--ste-border); }
.rubric-actions > span { color: var(--ste-muted); font-size: 11px; }
.empty-detail { display: grid; min-height: 540px; place-items: center; }
@media (max-width: 1250px) { .talent-workspace { grid-template-columns: 1fr; } }
@media (max-width: 760px) {
  .context-toolbar, .project-select, .toolbar-copy, .achievement-footer, .evidence-note, .rubric-actions { align-items: stretch; flex-direction: column; }
  .project-select .el-select { width: 100%; }
  .stats-strip { grid-template-columns: repeat(2, 1fr); }
  .stats-strip article:nth-child(2) { border-right: 0; }
  .competency-row, .evidence-columns, .rubric-row { grid-template-columns: 1fr; }
  .rubric-row > .el-textarea { grid-column: auto; }
}
</style>
