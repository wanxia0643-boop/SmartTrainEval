<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { ArrowRight, CircleCheck, DocumentChecked, Histogram, Timer, UserFilled } from '@element-plus/icons-vue'
import { useUserStore } from '../../stores/user'
import { useRouter } from 'vue-router'
import TeacherDashboard from './TeacherDashboard.vue'
import { listAchievements } from '../../api/achievements'
import { listProjects } from '../../api/projects'
import { listEvalResults } from '../../api/evalResults'
import { listIndicators } from '../../api/indicators'
import { listUsers } from '../../api/users'
import { listRoles } from '../../api/roles'

const userStore = useUserStore()
const router = useRouter()
const trendElement = ref()
const abilityElement = ref()
let trendChart
let abilityChart

const ACH_STATUS = { 0: '草稿', 1: '已提交', 2: '评价中', 3: '已评价', 4: '退回重做' }

const roleCopy = {
  student: { greeting: '今天的实训目标，稳稳推进', caption: '按计划完成任务，及时吸收评价反馈。', queue: '我的实训成果', role: '学生工作台' },
  enterprise: { greeting: '人才培养正在发生在项目现场', caption: '关注优先事项，把企业反馈变成学习者成长的下一步。', queue: '待评价成果', role: '成长工作室' },
  admin: { greeting: '平台运行平稳，组织协同在线', caption: '关注系统使用与评价质量，及时完成平台基础配置。', queue: '最新提交成果', role: '运营工作台' },
}
const copy = ref(roleCopy[userStore.role] || roleCopy.admin)
const todayText = ref('')

const metrics = ref([])
const rows = ref([])
const queue = ref([])
const statFoot = ref([['平均得分', '—'], ['优秀率', '—'], ['及格率', '—'], ['低分率', '—']])
const abilityList = ref([])
const notifications = ref([])
let trendLabels = ['6/17', '6/18', '6/19', '6/20', '6/21', '6/22', '6/23']
let trendData = [0, 0, 0, 0, 0, 0, 0]
let abilityData = []

function fmtTime(t) { return (t || '').replace('T', ' ').slice(0, 16) || '—' }
function pct(n, d) { return d ? Math.round((n / d) * 1000) / 10 : 0 }

async function loadData() {
  if (userStore.role === 'teacher') return
  const role = userStore.role
  copy.value = roleCopy[role] || roleCopy.admin

  const roles = await listRoles()
  const studentRoleId = roles.find((r) => r.role_code === 'STUDENT')?.id

  const projRes = await listProjects({ page: 1, page_size: 100 })
  const achRes = await listAchievements(
    role === 'student'
      ? { student_id: userStore.userId, page: 1, page_size: 100 }
      : { page: 1, page_size: 100 },
  )
  const achs = achRes.items || []
  const indRes = await listIndicators({ page: 1, page_size: 200 })
  const indMap = Object.fromEntries((indRes.items || []).map((i) => [i.id, i.indicator_name]))

  // 评价记录：学生取自己成果的评价，其它角色取全部
  let evalItems = []
  if (role === 'student') {
    const arrs = await Promise.all(
      achs.map((a) => listEvalResults({ achievement_id: a.id, page: 1, page_size: 100 }).then((d) => d.items).catch(() => [])),
    )
    evalItems = arrs.flat()
  } else {
    evalItems = (await listEvalResults({ page: 1, page_size: 100 })).items || []
  }

  // 学生姓名映射（非学生角色用于展示提交人）
  let stuMap = {}
  let studentTotal = 0
  if (role !== 'student' && studentRoleId) {
    const stuRes = await listUsers({ role_id: studentRoleId, page: 1, page_size: 100 })
    stuMap = Object.fromEntries((stuRes.items || []).map((u) => [u.id, u.real_name]))
    studentTotal = stuRes.total
  }
  const projMap = Object.fromEntries((projRes.items || []).map((p) => [p.id, p.project_name]))

  const pending = achs.filter((a) => [1, 2].includes(a.status)).length
  const evaluated = achs.filter((a) => a.status === 3).length
  const ongoing = (projRes.items || []).filter((p) => p.status === 1).length
  const scored = achs.filter((a) => a.final_score != null).map((a) => Number(a.final_score))
  const avg = scored.length ? Math.round((scored.reduce((s, x) => s + x, 0) / scored.length) * 10) / 10 : null

  // 角色化指标卡
  if (role === 'student') {
    metrics.value = [
      { label: '我的成果', value: String(achs.length), unit: '份', delta: `已评价 ${evaluated} 份`, tone: 'primary', icon: DocumentChecked },
      { label: '平均得分', value: avg == null ? '—' : String(avg), unit: '分', delta: '基于已评成果', tone: 'success', icon: Histogram },
      { label: '进行中项目', value: String(ongoing), unit: '个', delta: `共 ${projRes.total} 个`, tone: 'warning', icon: Timer },
      { label: '待反馈', value: String(pending), unit: '份', delta: '提交待评价', tone: 'primary', icon: CircleCheck },
    ]
  } else if (role === 'enterprise') {
    const myScores = evalItems.filter((e) => e.eval_type === 3).length
    metrics.value = [
      { label: '实训项目', value: String(projRes.total), unit: '个', delta: `进行中 ${ongoing} 个`, tone: 'primary', icon: DocumentChecked },
      { label: '待评成果', value: String(pending), unit: '份', delta: `共 ${achRes.total} 份`, tone: 'warning', icon: Timer },
      { label: '已评成果', value: String(evaluated), unit: '份', delta: '完成评价', tone: 'success', icon: CircleCheck },
      { label: '我的评分', value: String(myScores), unit: '条', delta: '企业侧评价', tone: 'primary', icon: Histogram },
    ]
  } else {
    metrics.value = [
      { label: '在册学生', value: String(studentTotal || '—'), unit: '人', delta: '平台用户', tone: 'primary', icon: UserFilled },
      { label: '实训项目', value: String(projRes.total), unit: '个', delta: `进行中 ${ongoing} 个`, tone: 'success', icon: DocumentChecked },
      { label: '实训成果', value: String(achRes.total), unit: '份', delta: `待评 ${pending} 份`, tone: 'warning', icon: Timer },
      { label: '评价记录', value: String(evalItems.length), unit: '条', delta: '累计评分', tone: 'primary', icon: Histogram },
    ]
  }

  // 列表：最近成果
  rows.value = achs.slice(0, 6).map((a) => ({
    name: role === 'student' ? userStore.name : (stuMap[a.student_id] || `学生#${a.student_id}`),
    project: projMap[a.project_id] || `项目#${a.project_id}`,
    task: a.title,
    time: fmtTime(a.submit_time || a.create_time),
    score: a.final_score ?? '—',
    status: ACH_STATUS[a.status] || '—',
  }))

  // 队列：成果状态分布
  const statusCounts = {}
  for (const a of achs) statusCounts[a.status] = (statusCounts[a.status] || 0) + 1
  queue.value = Object.entries(statusCounts).map(([s, n]) => [ACH_STATUS[s] || `状态${s}`, `${n} 份`])

  // 成绩统计
  if (scored.length) {
    statFoot.value = [
      ['平均得分', `${avg} 分`],
      ['优秀率', `${pct(scored.filter((s) => s >= 85).length, scored.length)} %`],
      ['及格率', `${pct(scored.filter((s) => s >= 60).length, scored.length)} %`],
      ['低分率', `${pct(scored.filter((s) => s < 60).length, scored.length)} %`],
    ]
  }

  // 能力维度：按指标平均分
  const buckets = {}
  for (const e of evalItems) {
    if (!buckets[e.indicator_id]) buckets[e.indicator_id] = { sum: 0, n: 0 }
    buckets[e.indicator_id].sum += Number(e.score)
    buckets[e.indicator_id].n += 1
  }
  abilityList.value = Object.entries(buckets).map(([id, b]) => [indMap[id] || `指标#${id}`, String(Math.round((b.sum / b.n) * 10) / 10)])
  const palette = ['#165DFF', '#14B8A6', '#5E84F4', '#F6B94B', '#8B6FE8', '#F58B55']
  abilityData = abilityList.value.map(([name, val], i) => ({ value: Number(val), name, itemStyle: { color: palette[i % palette.length] } }))

  // 近 7 天提交趋势
  const today = new Date()
  const days = []
  for (let i = 6; i >= 0; i--) { const d = new Date(today); d.setDate(d.getDate() - i); days.push(d) }
  trendLabels = days.map((d) => `${d.getMonth() + 1}/${d.getDate()}`)
  trendData = days.map((d) => {
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    return achs.filter((a) => (a.submit_time || a.create_time || '').slice(0, 10) === key).length
  })

  // 通知：从真实数据派生
  notifications.value = [
    { tone: pending ? 'is-danger' : '', title: `有 ${pending} 份成果待评价`, desc: '关注最近提交的实训成果，及时完成评价。', time: '实时' },
    { tone: '', title: `平台共 ${projRes.total} 个实训项目`, desc: `其中 ${ongoing} 个进行中。`, time: '今日' },
    { tone: '', title: `累计 ${achRes.total} 份实训成果`, desc: `已评价 ${evaluated} 份。`, time: '今日' },
  ]

  await nextTick()
  initCharts()
}

function initCharts() {
  if (userStore.role === 'teacher') return
  if (!trendElement.value || !abilityElement.value) return
  trendChart?.dispose(); abilityChart?.dispose()
  trendChart = echarts.init(trendElement.value)
  abilityChart = echarts.init(abilityElement.value)
  trendChart.setOption({
    grid: { left: 34, right: 18, top: 34, bottom: 28 }, tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: trendLabels, axisTick: { show: false }, axisLine: { lineStyle: { color: '#E9EDF5' } }, axisLabel: { color: '#7A8499', fontSize: 11 } },
    yAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: '#F0F2F6' } }, axisLabel: { color: '#7A8499', fontSize: 11 } },
    series: [{ name: '提交量', type: 'line', smooth: true, data: trendData, symbolSize: 6, lineStyle: { color: '#165DFF', width: 2.5 }, itemStyle: { color: '#165DFF' }, areaStyle: { color: 'rgba(22,93,255,0.08)' } }],
  })
  abilityChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}<br/>平均 {c} 分' },
    series: [{ type: 'pie', radius: ['52%', '73%'], center: ['50%', '51%'], label: { show: false }, data: abilityData.length ? abilityData : [{ value: 1, name: '暂无评价数据', itemStyle: { color: '#E3E8F0' } }] }],
  })
}
function resizeCharts() { trendChart?.resize(); abilityChart?.resize() }
function startReview() { router.push({ name: userStore.role === 'student' ? 'my-evaluation' : 'data-report' }) }
function showInfo() { router.push({ name: userStore.role === 'student' ? 'my-evaluation' : 'data-report' }) }

onMounted(async () => {
  todayText.value = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
  await loadData()
  window.addEventListener('resize', resizeCharts)
})
onBeforeUnmount(() => { window.removeEventListener('resize', resizeCharts); trendChart?.dispose(); abilityChart?.dispose() })
watch(() => userStore.role, () => loadData())
</script>

<template>
  <TeacherDashboard v-if="userStore.role === 'teacher'" />
  <section v-else class="dashboard-page">
    <div class="dashboard-hero">
      <div>
        <p class="page-eyebrow">{{ copy.role }}</p>
        <h2>{{ copy.greeting }}，{{ userStore.name }}</h2>
        <p>{{ copy.caption }}</p>
      </div>
      <div class="hero-date"><el-icon><Timer /></el-icon> {{ todayText }}</div>
    </div>

    <div class="metric-strip">
      <article v-for="metric in metrics" :key="metric.label" class="metric-item">
        <span class="metric-icon" :class="`tone-${metric.tone}`"><el-icon><component :is="metric.icon" /></el-icon></span>
        <div><p>{{ metric.label }}</p><strong>{{ metric.value }}<small>{{ metric.unit }}</small></strong><span class="metric-delta">{{ metric.delta }}</span></div>
      </article>
    </div>

    <div class="dashboard-grid top-grid">
      <article class="data-panel trend-panel">
        <div class="panel-heading"><div><h3>近 7 天成果提交趋势</h3><span>按提交时间统计</span></div></div>
        <div ref="trendElement" class="chart-region" aria-label="近七天成果提交趋势图"></div>
        <div class="stat-foot"><div v-for="item in statFoot" :key="item[0]"><span>{{ item[0] }}</span><strong>{{ item[1] }}</strong></div></div>
      </article>

      <article class="data-panel ability-panel">
        <div class="panel-heading"><div><h3>能力维度分布</h3><span>评价指标平均得分</span></div></div>
        <div class="ability-body">
          <div ref="abilityElement" class="ability-chart" aria-label="能力维度分布图"></div>
          <dl class="ability-list">
            <template v-for="item in abilityList" :key="item[0]"><dt>{{ item[0] }}</dt><dd>{{ item[1] }}</dd></template>
            <dt v-if="!abilityList.length" class="ability-empty">暂无评价数据</dt>
          </dl>
        </div>
      </article>

      <aside class="side-rail">
        <article class="data-panel compact-panel queue-panel">
          <div class="panel-heading"><h3>成果状态分布</h3></div>
          <ul>
            <li v-for="item in queue" :key="item[0]"><span><el-icon><DocumentChecked /></el-icon>{{ item[0] }}</span><strong>{{ item[1] }}</strong></li>
            <li v-if="!queue.length" class="queue-empty">暂无成果</li>
          </ul>
        </article>
      </aside>
    </div>

    <div class="dashboard-grid bottom-grid">
      <article class="data-panel review-panel">
        <div class="panel-heading review-heading">
          <div><h3>{{ copy.queue }}</h3></div>
          <el-button text type="primary" @click="showInfo">查看全部 <el-icon><ArrowRight /></el-icon></el-button>
        </div>
        <el-table :data="rows" class="review-table" table-layout="auto">
          <el-table-column label="学生姓名" min-width="120"><template #default="{ row }"><div class="student-cell"><el-avatar :size="26">{{ row.name.slice(0, 1) }}</el-avatar><span>{{ row.name }}</span></div></template></el-table-column>
          <el-table-column prop="project" label="实训项目" min-width="150" show-overflow-tooltip />
          <el-table-column prop="task" label="成果标题" min-width="140" show-overflow-tooltip />
          <el-table-column prop="time" label="提交时间" min-width="142" />
          <el-table-column prop="score" label="得分" min-width="80" />
          <el-table-column label="状态" min-width="100"><template #default="{ row }"><el-tag size="small" :type="row.status === '已评价' ? 'success' : row.status === '已提交' ? 'primary' : 'warning'" effect="plain">{{ row.status }}</el-tag></template></el-table-column>
          <el-table-column label="操作" width="84" fixed="right"><template #default="{ row }"><el-button text type="primary" @click="startReview(row)">查看</el-button></template></el-table-column>
        </el-table>
        <div v-if="!rows.length" class="review-empty">暂无成果数据</div>
        <div v-else class="table-footer"><span>共 {{ rows.length }} 条</span></div>
      </article>
      <aside class="data-panel notification-panel">
        <div class="panel-heading"><h3>系统动态</h3></div>
        <ul class="notice-list">
          <li v-for="n in notifications" :key="n.title"><span class="notice-dot" :class="n.tone"></span><div><strong>{{ n.title }}</strong><p>{{ n.desc }}</p></div><time>{{ n.time }}</time></li>
        </ul>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.review-empty, .queue-empty, .ability-empty { padding: 24px; color: var(--el-text-color-secondary); text-align: center; font-size: 13px; }
.table-footer { display: flex; justify-content: flex-end; padding: 12px 4px 0; color: var(--el-text-color-secondary); font-size: 13px; }
</style>
