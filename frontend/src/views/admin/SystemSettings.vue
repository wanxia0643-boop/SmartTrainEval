<script setup>
import { computed, onMounted, ref } from 'vue'
import { Bell, CircleCheck, DataLine, Document, Refresh, Timer, Warning } from '@element-plus/icons-vue'
import { getAIHealth } from '../../api/aiAgent'

const SCENE_LABELS = {
  COACH_CHAT: '学生学伴',
  PROJECT_DRAFT: '项目设计',
  ACHIEVEMENT_PRECHECK: '成果预检',
  CLASS_ANALYSIS: '班级学情',
  ENTERPRISE_EVIDENCE: '岗位证据',
  PROJECT_BRIEFING: '数字人播报',
  ACHIEVEMENT_REVIEW: '智能核查',
}

const TASK_LABELS = {
  SUBMIT_ACHIEVEMENT: '成果提交',
  REDO_ACHIEVEMENT: '整改重交',
  TEACHER_REVIEW: '教师评价',
  ENTERPRISE_REVIEW: '企业评价',
  VIEW_FEEDBACK: '查看反馈',
}

const loading = ref(false)
const health = ref(null)
const logView = ref('failures')

const recent = computed(() => health.value?.recent_24h || {})
const processHealth = computed(() => health.value?.process_health || {})
const knowledge = computed(() => health.value?.knowledge_status || {})
const maxDailyCalls = computed(() => Math.max(1, ...(health.value?.daily_calls || []).map((item) => item.total)))
const logRows = computed(() => (
  logView.value === 'failures' ? health.value?.recent_failures || [] : health.value?.recent_calls || []
))

function sceneLabel(value) {
  return SCENE_LABELS[value] || value || '未知场景'
}

function taskLabel(value) {
  return TASK_LABELS[value] || value
}

function formatDuration(value) {
  const duration = Number(value || 0)
  if (duration < 1000) return `${Math.round(duration)} ms`
  return `${(duration / 1000).toFixed(1)} s`
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '—'
}

function dayLabel(value) {
  const date = new Date(`${value}T00:00:00`)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

function alertType(level) {
  return { critical: 'danger', warning: 'warning', info: 'primary' }[level] || 'info'
}

async function loadGovernance() {
  loading.value = true
  try {
    health.value = await getAIHealth()
  } finally {
    loading.value = false
  }
}

onMounted(loadGovernance)
</script>

<template>
  <section class="feature-page governance-page" v-loading="loading">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">ADMIN · AI GOVERNANCE</p>
        <h2>系统治理工作台</h2>
        <p>监控模型质量、知识资料、业务待办和评价完整率，异常可追踪但不介入人工评分。</p>
      </div>
      <div class="hero-actions">
        <el-tag :type="health?.operational ? 'success' : 'warning'" effect="plain">
          {{ health?.operational ? `${health.model} 运行正常` : '模型需要关注' }}
        </el-tag>
        <el-button :icon="Refresh" :loading="loading" circle title="刷新治理数据" @click="loadGovernance" />
      </div>
    </div>

    <section class="metric-strip" aria-label="系统治理核心指标">
      <article class="metric-item">
        <span class="metric-icon tone-success"><CircleCheck /></span>
        <div><p>模型状态</p><strong>{{ health?.configured ? '已配置' : '未配置' }}</strong><span>{{ health?.model || '—' }}</span></div>
      </article>
      <article class="metric-item">
        <span class="metric-icon tone-primary"><DataLine /></span>
        <div><p>近 24h 成功率</p><strong>{{ recent.success_rate ?? 0 }}<small>%</small></strong><span>{{ recent.success_calls || 0 }}/{{ recent.total_calls || 0 }} 次成功</span></div>
      </article>
      <article class="metric-item">
        <span class="metric-icon tone-warning"><Timer /></span>
        <div><p>平均响应耗时</p><strong>{{ formatDuration(recent.average_duration_ms) }}</strong><span>P95 {{ formatDuration(recent.p95_duration_ms) }}</span></div>
      </article>
      <article class="metric-item">
        <span class="metric-icon" :class="processHealth.overdue_tasks ? 'tone-danger' : 'tone-success'"><Bell /></span>
        <div><p>业务待办</p><strong>{{ processHealth.pending_tasks || 0 }}<small>项</small></strong><span>{{ processHealth.overdue_tasks || 0 }} 项逾期</span></div>
      </article>
    </section>

    <article v-if="health?.alerts?.length" class="data-panel alert-panel">
      <div class="panel-heading"><div><h3>运行预警</h3><span>按影响程度排序，管理员只负责治理和协调</span></div></div>
      <div class="alert-list">
        <div v-for="item in health.alerts" :key="`${item.level}-${item.title}`" class="alert-row">
          <el-icon :class="`alert-${item.level}`"><Warning /></el-icon>
          <div><strong>{{ item.title }}</strong><span>{{ item.description }}</span></div>
          <el-tag :type="alertType(item.level)" effect="plain">{{ item.level === 'critical' ? '紧急' : item.level === 'warning' ? '关注' : '提示' }}</el-tag>
        </div>
      </div>
    </article>

    <div class="governance-grid">
      <article class="data-panel trend-panel">
        <div class="panel-heading">
          <div><h3>近 7 日 AI 调用趋势</h3><span>成功与失败调用按天聚合</span></div>
          <span class="token-total">24h Token {{ recent.total_tokens || 0 }}</span>
        </div>
        <div class="daily-chart" role="img" aria-label="近七日 AI 调用成功与失败趋势">
          <div v-for="item in health?.daily_calls || []" :key="item.date" class="day-column">
            <div class="bar-track" :title="`${item.total} 次调用`">
              <div class="bar-stack" :style="{ height: `${Math.max(4, item.total / maxDailyCalls * 100)}%` }">
                <span class="bar-failed" :style="{ flex: item.failed || 0 }" />
                <span class="bar-success" :style="{ flex: item.success || 0 }" />
              </div>
            </div>
            <strong>{{ item.total }}</strong><span>{{ dayLabel(item.date) }}</span>
          </div>
        </div>
        <div class="chart-legend"><span><i class="legend-success" />成功</span><span><i class="legend-failed" />失败</span></div>
      </article>

      <article class="data-panel process-panel">
        <div class="panel-heading"><div><h3>评价流程健康</h3><span>从提交到多方评价完成</span></div></div>
        <div class="completion-score">
          <el-progress type="dashboard" :percentage="processHealth.evaluation_completion_rate || 0" :width="112" :stroke-width="9" />
          <div><strong>{{ processHealth.evaluated_achievements || 0 }}/{{ processHealth.submitted_achievements || 0 }}</strong><span>成果已形成最终成绩</span></div>
        </div>
        <dl class="process-stats">
          <div><dt>进行中项目</dt><dd>{{ processHealth.active_projects || 0 }}</dd></div>
          <div><dt>评价中成果</dt><dd>{{ processHealth.evaluating_achievements || 0 }}</dd></div>
          <div><dt>退回整改</dt><dd>{{ processHealth.returned_achievements || 0 }}</dd></div>
          <div><dt>高优先级待办</dt><dd>{{ processHealth.high_priority_tasks || 0 }}</dd></div>
        </dl>
      </article>

      <article class="data-panel knowledge-panel">
        <div class="panel-heading"><div><h3>知识库解析状态</h3><span>课程资料与岗位标准</span></div><Document /></div>
        <div class="knowledge-total"><strong>{{ knowledge.total || 0 }}</strong><span>份知识资料</span></div>
        <div class="knowledge-rows">
          <div><span>可检索</span><strong class="success-text">{{ knowledge.ready || 0 }}</strong></div>
          <div><span>解析中</span><strong>{{ knowledge.processing || 0 }}</strong></div>
          <div><span>解析失败</span><strong :class="{ 'danger-text': knowledge.failed }">{{ knowledge.failed || 0 }}</strong></div>
        </div>
      </article>
    </div>

    <div class="lower-grid">
      <article class="data-panel scene-panel">
        <div class="panel-heading"><div><h3>AI 场景质量</h3><span>近 24 小时各智能体场景表现</span></div></div>
        <el-table :data="health?.scene_stats || []" empty-text="近 24 小时暂无调用">
          <el-table-column label="场景" min-width="130"><template #default="{ row }"><strong>{{ sceneLabel(row.scene) }}</strong></template></el-table-column>
          <el-table-column prop="total" label="调用" width="72" align="right" />
          <el-table-column label="成功率" width="110" align="right"><template #default="{ row }"><span :class="row.success_rate < 80 ? 'danger-text' : 'success-text'">{{ row.success_rate }}%</span></template></el-table-column>
          <el-table-column label="平均耗时" width="110" align="right"><template #default="{ row }">{{ formatDuration(row.average_duration_ms) }}</template></el-table-column>
          <el-table-column prop="total_tokens" label="Token" width="100" align="right" />
        </el-table>
      </article>

      <article class="data-panel task-panel">
        <div class="panel-heading"><div><h3>待办类型分布</h3><span>四角色未完成业务任务</span></div></div>
        <div class="task-list">
          <div v-for="item in processHealth.task_types || []" :key="item.task_type">
            <span>{{ taskLabel(item.task_type) }}</span>
            <strong>{{ item.count }}</strong>
          </div>
          <el-empty v-if="!processHealth.task_types?.length" :image-size="56" description="当前没有业务待办" />
        </div>
      </article>
    </div>

    <article class="data-panel log-panel">
      <div class="panel-heading log-heading">
        <div><h3>AI 调用审计</h3><span>仅展示场景、耗时与脱敏错误，不暴露提示词和模型响应正文</span></div>
        <el-segmented v-model="logView" :options="[{ label: '失败记录', value: 'failures' }, { label: '最近调用', value: 'recent' }]" />
      </div>
      <el-table :data="logRows" empty-text="当前没有相关调用记录">
        <el-table-column prop="id" label="ID" width="74" />
        <el-table-column label="场景" min-width="130"><template #default="{ row }">{{ sceneLabel(row.scene) }}</template></el-table-column>
        <el-table-column prop="model" label="模型" min-width="150" />
        <el-table-column label="状态" width="86"><template #default="{ row }"><el-tag :type="row.status === 1 ? 'success' : 'danger'" effect="plain">{{ row.status === 1 ? '成功' : '失败' }}</el-tag></template></el-table-column>
        <el-table-column label="耗时" width="100" align="right"><template #default="{ row }">{{ formatDuration(row.duration_ms) }}</template></el-table-column>
        <el-table-column v-if="logView === 'recent'" prop="total_tokens" label="Token" width="90" align="right" />
        <el-table-column v-else prop="error" label="失败摘要" min-width="260" show-overflow-tooltip />
        <el-table-column label="时间" min-width="170"><template #default="{ row }">{{ formatDate(row.create_time) }}</template></el-table-column>
      </el-table>
    </article>
  </section>
</template>

<style scoped>
.hero-actions { display: flex; align-items: center; gap: 10px; }
.metric-strip { grid-template-columns: repeat(4, minmax(180px, 1fr)); }
.metric-item { min-height: 104px; }
.metric-item > div { min-width: 0; }
.metric-item > div > span { display: block; max-width: 180px; margin-top: 5px; overflow: hidden; color: var(--ste-muted); font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.tone-danger { color: var(--ste-danger); background: #fff0f0; }
.alert-panel { margin-bottom: 16px; overflow: hidden; }
.alert-list { padding: 0 18px 12px; }
.alert-row { display: grid; grid-template-columns: 28px minmax(0, 1fr) auto; gap: 10px; align-items: center; padding: 11px 0; border-top: 1px solid var(--ste-border); }
.alert-row > .el-icon { font-size: 18px; }.alert-critical { color: var(--ste-danger); }.alert-warning { color: var(--ste-warning); }.alert-info { color: var(--ste-primary); }
.alert-row div { display: grid; gap: 3px; }.alert-row strong { font-size: 13px; }.alert-row span { color: var(--ste-muted); font-size: 11px; }
.governance-grid { display: grid; grid-template-columns: minmax(480px, 1.35fr) minmax(270px, .7fr) minmax(230px, .55fr); gap: 16px; }
.token-total { color: var(--ste-muted); font-size: 11px; }
.daily-chart { display: grid; grid-template-columns: repeat(7, 1fr); gap: 14px; height: 230px; padding: 12px 22px 0; }
.day-column { display: grid; grid-template-rows: 1fr auto auto; gap: 5px; min-width: 0; text-align: center; }
.bar-track { display: flex; align-items: end; justify-content: center; min-height: 150px; border-bottom: 1px solid var(--ste-border); }
.bar-stack { display: flex; flex-direction: column; justify-content: end; width: min(30px, 70%); min-height: 4px; overflow: hidden; background: #eef2f7; border-radius: 3px 3px 0 0; }
.bar-stack span { min-height: 2px; }.bar-success { background: var(--ste-success); }.bar-failed { background: var(--ste-danger); }
.day-column strong { font-size: 12px; }.day-column > span { color: var(--ste-muted); font-size: 10px; }
.chart-legend { display: flex; justify-content: center; gap: 16px; padding: 10px 0 16px; color: var(--ste-muted); font-size: 11px; }
.chart-legend span { display: flex; align-items: center; gap: 5px; }.chart-legend i { width: 8px; height: 8px; border-radius: 2px; }.legend-success { background: var(--ste-success); }.legend-failed { background: var(--ste-danger); }
.completion-score { display: flex; align-items: center; gap: 14px; padding: 4px 18px 12px; }
.completion-score > div { display: grid; gap: 5px; }.completion-score strong { font-size: 20px; }.completion-score span { color: var(--ste-muted); font-size: 11px; }
.process-stats { display: grid; grid-template-columns: 1fr 1fr; margin: 0; border-top: 1px solid var(--ste-border); }
.process-stats div { display: flex; align-items: center; justify-content: space-between; padding: 13px 16px; border-bottom: 1px solid var(--ste-border); }
.process-stats div:nth-child(odd) { border-right: 1px solid var(--ste-border); }.process-stats dt { color: var(--ste-muted); font-size: 11px; }.process-stats dd { margin: 0; font-size: 14px; font-weight: 700; }
.knowledge-panel .panel-heading > svg { width: 20px; color: var(--ste-primary); }
.knowledge-total { display: grid; gap: 4px; padding: 14px 18px 18px; }.knowledge-total strong { font-size: 30px; }.knowledge-total span { color: var(--ste-muted); font-size: 11px; }
.knowledge-rows { border-top: 1px solid var(--ste-border); }.knowledge-rows div { display: flex; justify-content: space-between; padding: 13px 18px; border-bottom: 1px solid var(--ste-border); }.knowledge-rows span { color: var(--ste-muted); font-size: 12px; }.knowledge-rows strong { font-size: 13px; }
.lower-grid { display: grid; grid-template-columns: minmax(560px, 1.4fr) minmax(280px, .6fr); gap: 16px; margin-top: 16px; }
.scene-panel, .task-panel, .log-panel { overflow: hidden; }.scene-panel .el-table, .log-panel .el-table { padding: 0 10px 12px; }
.task-list { padding: 0 18px 14px; }.task-list > div { display: flex; justify-content: space-between; padding: 13px 0; border-top: 1px solid var(--ste-border); }.task-list span { color: #4e5e76; font-size: 12px; }.task-list strong { font-size: 13px; }
.log-panel { margin-top: 16px; }.log-heading { align-items: center; }
.success-text { color: var(--ste-success); }.danger-text { color: var(--ste-danger); }
@media (max-width: 1320px) { .governance-grid { grid-template-columns: 1fr 1fr; }.trend-panel { grid-column: 1 / -1; } }
@media (max-width: 980px) { .metric-strip { grid-template-columns: repeat(2, 1fr); }.lower-grid { grid-template-columns: 1fr; } }
@media (max-width: 700px) { .hero-actions { align-items: flex-start; }.metric-strip, .governance-grid { grid-template-columns: 1fr; }.trend-panel { grid-column: auto; }.daily-chart { gap: 6px; padding-inline: 10px; }.alert-row { grid-template-columns: 24px 1fr; }.alert-row .el-tag { grid-column: 2; justify-self: start; }.log-heading { align-items: flex-start; flex-direction: column; } }
</style>
