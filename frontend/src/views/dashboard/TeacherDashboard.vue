<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  CaretBottom,
  CaretTop,
  CircleCheck,
  DocumentChecked,
  FolderOpened,
  UserFilled,
} from '@element-plus/icons-vue'
import ResponsiveEChart from './components/ResponsiveEChart.vue'
import { listAchievements } from '../../api/achievements'
import { listProjects } from '../../api/projects'
import { listUsers } from '../../api/users'
import { listRoles } from '../../api/roles'

const router = useRouter()
const reviewRows = ref([])
const scoredCount = ref(0)

const metrics = ref([
  { label: '待评审实训数', value: '—', unit: '项', comparison: '加载中', direction: 'up', icon: DocumentChecked, tone: 'blue' },
  { label: '进行中实训项目', value: '—', unit: '个', comparison: '加载中', direction: 'up', icon: FolderOpened, tone: 'cyan' },
  { label: '学生总数', value: '—', unit: '人', comparison: '加载中', direction: 'up', icon: UserFilled, tone: 'violet' },
  { label: '已评价成果', value: '—', unit: '项', comparison: '加载中', direction: 'up', icon: CircleCheck, tone: 'green' },
])

function fmtTime(t) {
  return (t || '').replace('T', ' ').slice(0, 16) || '—'
}

async function loadDashboard() {
  const roles = await listRoles()
  const studentRoleId = roles.find((r) => r.role_code === 'STUDENT')?.id
  const [achRes, projRes, stuRes] = await Promise.all([
    listAchievements({ page: 1, page_size: 100 }),
    listProjects({ page: 1, page_size: 100 }),
    studentRoleId ? listUsers({ role_id: studentRoleId, page: 1, page_size: 100 }) : Promise.resolve({ total: 0, items: [] }),
  ])
  const achs = achRes.items || []
  const pending = achs.filter((a) => [1, 2].includes(a.status)).length
  const evaluated = achs.filter((a) => a.status === 3).length
  const ongoing = (projRes.items || []).filter((p) => p.status === 1).length

  metrics.value = [
    { label: '待评审实训数', value: String(pending), unit: '项', comparison: `共 ${achRes.total} 份成果`, direction: 'up', icon: DocumentChecked, tone: 'blue' },
    { label: '进行中实训项目', value: String(ongoing), unit: '个', comparison: `共 ${projRes.total} 个项目`, direction: 'up', icon: FolderOpened, tone: 'cyan' },
    { label: '学生总数', value: String(stuRes.total), unit: '人', comparison: '平台在册', direction: 'up', icon: UserFilled, tone: 'violet' },
    { label: '已评价成果', value: String(evaluated), unit: '项', comparison: '评价完成', direction: 'up', icon: CircleCheck, tone: 'green' },
  ]

  // 待评审成果列表（最近提交的未完成评价成果）
  const projMap = Object.fromEntries((projRes.items || []).map((p) => [p.id, p.project_name]))
  const stuMap = Object.fromEntries((stuRes.items || []).map((u) => [u.id, u.real_name]))
  reviewRows.value = achs
    .filter((a) => [1, 2].includes(a.status))
    .slice(0, 6)
    .map((a) => ({
      name: stuMap[a.student_id] || `学生#${a.student_id}`,
      project: projMap[a.project_id] || `项目#${a.project_id}`,
      submittedAt: fmtTime(a.submit_time || a.create_time),
    }))

  // 成绩分布（按 final_score 分档）
  const bands = { 优秀: 0, 良好: 0, 及格: 0, 不及格: 0 }
  for (const a of achs) {
    if (a.final_score == null) continue
    const s = Number(a.final_score)
    if (s >= 85) bands.优秀++
    else if (s >= 70) bands.良好++
    else if (s >= 60) bands.及格++
    else bands.不及格++
  }
  scoredCount.value = bands.优秀 + bands.良好 + bands.及格 + bands.不及格
  scoreOption.value = buildScoreOption(bands)

  // 近 7 天提交量（按 submit_time 分日统计）
  const today = new Date()
  const days = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    days.push(d)
  }
  const labels = days.map((d) => `${d.getMonth() + 1}/${d.getDate()}`)
  const counts = days.map((d) => {
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    return achs.filter((a) => (a.submit_time || a.create_time || '').slice(0, 10) === key).length
  })
  submissionOption.value = buildSubmissionOption(labels, counts)
}

onMounted(loadDashboard)

function buildSubmissionOption(labels, data) {
  return ({
  animationDuration: 260,
  animationEasing: 'cubicOut',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1D2940',
    borderWidth: 0,
    textStyle: { color: '#fff', fontSize: 12 },
    formatter: (items) => `${items[0].axisValue}<br/>提交量：${items[0].value} 份`,
  },
  grid: { top: 28, right: 20, bottom: 30, left: 38 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: labels,
    axisTick: { show: false },
    axisLine: { lineStyle: { color: '#E8EDF5' } },
    axisLabel: { color: '#6F7B91', fontSize: 12, margin: 12 },
  },
  yAxis: {
    type: 'value',
    minInterval: 5,
    splitNumber: 4,
    axisLabel: { color: '#6F7B91', fontSize: 12 },
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: '#EEF2F7', type: 'dashed' } },
  },
  series: [{
    name: '提交量',
    type: 'line',
    smooth: true,
    data,
    symbol: 'circle',
    symbolSize: 7,
    lineStyle: { color: '#165DFF', width: 3 },
    itemStyle: { color: '#165DFF', borderColor: '#fff', borderWidth: 2 },
    areaStyle: { color: 'rgba(22, 93, 255, 0.09)' },
  }],
  })
}

function buildScoreOption(bands) {
  return ({
  animationDuration: 260,
  animationEasing: 'cubicOut',
  tooltip: {
    trigger: 'item',
    backgroundColor: '#1D2940',
    borderWidth: 0,
    textStyle: { color: '#fff', fontSize: 12 },
    formatter: '{b}<br/>{c} 人，占比 {d}%',
  },
  legend: {
    bottom: 4,
    left: 'center',
    itemWidth: 9,
    itemHeight: 9,
    itemGap: 15,
    textStyle: { color: '#637087', fontSize: 12 },
  },
  series: [{
    type: 'pie',
    radius: '68%',
    center: ['50%', '45%'],
    avoidLabelOverlap: true,
    label: { show: false },
    labelLine: { show: false },
    data: [
      { value: bands.优秀, name: '优秀', itemStyle: { color: '#165DFF' } },
      { value: bands.良好, name: '良好', itemStyle: { color: '#28B28B' } },
      { value: bands.及格, name: '及格', itemStyle: { color: '#F3B63F' } },
      { value: bands.不及格, name: '不及格', itemStyle: { color: '#E56767' } },
    ],
  }],
  })
}

const submissionOption = ref(buildSubmissionOption(['6/17', '6/18', '6/19', '6/20', '6/21', '6/22', '6/23'], [0, 0, 0, 0, 0, 0, 0]))
const scoreOption = ref(buildScoreOption({ 优秀: 0, 良好: 0, 及格: 0, 不及格: 0 }))

function goToReview(row) {
  router.push({ name: 'intelligent-evaluation', query: { student: row.name, project: row.project } })
}
</script>

<template>
  <section class="teacher-dashboard">
    <header class="teacher-dashboard__heading">
      <div>
        <p>教师工作台</p>
        <h2>实训评价概览</h2>
      </div>
      <span>数据更新时间：今天 10:30</span>
    </header>

    <section class="teacher-metrics" aria-label="实训核心数据">
      <article v-for="item in metrics" :key="item.label" class="teacher-metric-card">
        <span class="teacher-metric-card__icon" :class="`is-${item.tone}`"><el-icon><component :is="item.icon" /></el-icon></span>
        <div class="teacher-metric-card__content">
          <p>{{ item.label }}</p>
          <strong>{{ item.value }}<small>{{ item.unit }}</small></strong>
          <span class="teacher-metric-card__trend" :class="`is-${item.direction}`">
            <el-icon><component :is="item.direction === 'up' ? CaretTop : CaretBottom" /></el-icon>
            {{ item.comparison }}
          </span>
        </div>
      </article>
    </section>

    <section class="teacher-chart-grid" aria-label="实训数据图表">
      <article class="teacher-panel">
        <div class="teacher-panel__heading"><div><h3>近 7 天实训提交量</h3><span>按每日最新提交记录统计</span></div></div>
        <ResponsiveEChart :option="submissionOption" aria-label="近七天实训提交量折线图" />
      </article>
      <article class="teacher-panel">
        <div class="teacher-panel__heading"><div><h3>成绩分布</h3><span>已完成评审成果</span></div><strong>{{ scoredCount }} 人</strong></div>
        <ResponsiveEChart :option="scoreOption" aria-label="成绩分布饼图，包含优秀、良好、及格和不及格占比" />
      </article>
    </section>

    <section class="teacher-panel teacher-review-list" aria-labelledby="pending-review-title">
      <div class="teacher-panel__heading teacher-review-list__heading">
        <div><h3 id="pending-review-title">待评审成果</h3><span>优先处理最近提交的实训成果</span></div>
        <el-button type="primary" plain @click="router.push({ name: 'intelligent-evaluation' })">查看全部</el-button>
      </div>
      <el-table :data="reviewRows" class="teacher-review-table" table-layout="auto">
        <el-table-column prop="name" label="学生姓名" min-width="150">
          <template #default="{ row }"><div class="teacher-student"><el-avatar :size="28">{{ row.name.slice(0, 1) }}</el-avatar><span>{{ row.name }}</span></div></template>
        </el-table-column>
        <el-table-column prop="project" label="实训项目名称" min-width="260" show-overflow-tooltip />
        <el-table-column prop="submittedAt" label="提交时间" min-width="170" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }"><el-button type="primary" link @click="goToReview(row)">前往评审</el-button></template>
        </el-table-column>
      </el-table>
    </section>
  </section>
</template>

<style scoped>
.teacher-dashboard { max-width: 1480px; margin: 0 auto; }
.teacher-dashboard__heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 18px; }
.teacher-dashboard__heading p { margin: 0 0 6px; color: #165DFF; font-size: 12px; font-weight: 650; }
.teacher-dashboard__heading h2 { margin: 0; color: #1D2940; font-size: 24px; line-height: 1.2; letter-spacing: -.02em; }
.teacher-dashboard__heading > span { padding-bottom: 2px; color: #778399; font-size: 12px; }
.teacher-metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); margin-bottom: 16px; overflow: hidden; background: #fff; border: 1px solid #E8EDF5; border-radius: 9px; }
.teacher-metric-card { display: flex; gap: 13px; min-width: 0; padding: 20px; border-right: 1px solid #E8EDF5; }.teacher-metric-card:last-child { border-right: 0; }
.teacher-metric-card__icon { display: grid; flex: 0 0 40px; width: 40px; height: 40px; place-items: center; border-radius: 8px; font-size: 19px; }.is-blue { color: #165DFF; background: #EDF3FF; }.is-cyan { color: #0F9FC4; background: #E9F8FC; }.is-violet { color: #7557D9; background: #F1EDFF; }.is-green { color: #1D9B72; background: #EAF8F2; }
.teacher-metric-card__content { min-width: 0; }.teacher-metric-card__content p { margin: 0 0 5px; overflow: hidden; color: #66738A; font-size: 13px; text-overflow: ellipsis; white-space: nowrap; }.teacher-metric-card__content strong { display: block; color: #1D2940; font-size: 27px; line-height: 1; }.teacher-metric-card__content small { margin-left: 3px; font-size: 12px; font-weight: 500; }.teacher-metric-card__trend { display: flex; align-items: center; gap: 2px; margin-top: 8px; font-size: 11px; }.teacher-metric-card__trend.is-up { color: #15956D; }.teacher-metric-card__trend.is-down { color: #D88716; }
.teacher-chart-grid { display: grid; grid-template-columns: minmax(0, 1.34fr) minmax(330px, .66fr); gap: 16px; }.teacher-panel { min-width: 0; background: #fff; border: 1px solid #E8EDF5; border-radius: 9px; }.teacher-panel__heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; padding: 18px 20px 6px; }.teacher-panel__heading h3 { margin: 0; color: #25324A; font-size: 15px; font-weight: 650; }.teacher-panel__heading span { display: block; margin-top: 5px; color: #778399; font-size: 12px; }.teacher-panel__heading > strong { padding-top: 2px; color: #165DFF; font-size: 14px; }
.teacher-review-list { margin-top: 16px; overflow: hidden; }.teacher-review-list__heading { align-items: center; padding-bottom: 12px; }.teacher-review-table::before { display: none; }.teacher-review-table :deep(th.el-table__cell) { color: #6B778C; font-size: 12px; font-weight: 500; background: #FAFCFF; }.teacher-review-table :deep(td.el-table__cell) { color: #344158; font-size: 13px; }.teacher-student { display: flex; align-items: center; gap: 8px; }.teacher-student .el-avatar { color: #2766CC; background: #EAF1FF; font-size: 12px; }
@media (max-width: 1180px) { .teacher-metrics { grid-template-columns: repeat(2, 1fr); }.teacher-metric-card:nth-child(2) { border-right: 0; }.teacher-metric-card:nth-child(-n + 2) { border-bottom: 1px solid #E8EDF5; }.teacher-chart-grid { grid-template-columns: 1fr; } }
@media (max-width: 700px) { .teacher-dashboard__heading { align-items: flex-start; flex-direction: column; }.teacher-dashboard__heading h2 { font-size: 21px; }.teacher-dashboard__heading > span { padding: 0; }.teacher-metrics { grid-template-columns: 1fr; }.teacher-metric-card { border-right: 0; border-bottom: 1px solid #E8EDF5; }.teacher-metric-card:nth-child(2) { border-right: 0; }.teacher-metric-card:last-child { border-bottom: 0; }.teacher-panel__heading { padding: 16px 16px 6px; }.teacher-review-list__heading { align-items: flex-start; flex-direction: column; }.teacher-review-table { overflow-x: auto; } }
</style>
