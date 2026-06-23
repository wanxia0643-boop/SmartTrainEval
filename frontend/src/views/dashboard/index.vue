<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { ArrowRight, Bell, CircleCheck, DocumentChecked, Histogram, Timer, UserFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const trendElement = ref()
const abilityElement = ref()
let trendChart
let abilityChart

const roleCopy = {
  student: { greeting: '今天的实训目标，稳稳推进', caption: '按计划完成任务，及时吸收评价反馈。', queue: '待完成任务', role: '学生工作台' },
  teacher: { greeting: '评价节奏清晰，班级进展可控', caption: '优先处理待复核任务，及时关注异常学习进度。', queue: '待评阅列表', role: '评价指挥中心' },
  enterprise: { greeting: '人才培养正在发生在项目现场', caption: '关注优先事项，把企业反馈变成学习者成长的下一步。', queue: '导师待办', role: '成长工作室' },
  admin: { greeting: '平台运行平稳，组织协同在线', caption: '关注系统使用与评价质量，及时完成平台基础配置。', queue: '运营待办', role: '运营工作台' },
}
const copy = computed(() => roleCopy[userStore.role] || roleCopy.teacher)
const metrics = computed(() => userStore.role === 'teacher'
  ? [
      { label: '待我评阅', value: '48', unit: '份', delta: '较昨日 +12', tone: 'primary', icon: DocumentChecked },
      { label: 'AI 初评完成', value: '126', unit: '份', delta: '较昨日 +28', tone: 'success', icon: CircleCheck },
      { label: '已完成评阅', value: '258', unit: '份', delta: '较昨日 +36', tone: 'warning', icon: Histogram },
      { label: '评阅进度', value: '68', unit: '%', delta: '较昨日 +9%', tone: 'primary', icon: Timer },
    ]
  : [
      { label: '进行中项目', value: '6', unit: '个', delta: '本周 +1', tone: 'primary', icon: DocumentChecked },
      { label: '本周完成', value: '18', unit: '项', delta: '较上周 +4', tone: 'success', icon: CircleCheck },
      { label: '待处理事项', value: '12', unit: '项', delta: '优先处理 3 项', tone: 'warning', icon: Timer },
      { label: '综合达成率', value: '86', unit: '%', delta: '本月 +5%', tone: 'primary', icon: Histogram },
    ])
const rows = [
  { name: '李明轩', id: '2024120101', project: '电商系统开发实训', task: '系统设计文档', time: '2024-06-12 14:23', score: '82', status: 'AI 初评完成' },
  { name: '王思雨', id: '2024120102', project: '电商系统开发实训', task: '代码实现', time: '2024-06-12 13:58', score: '76', status: 'AI 初评完成' },
  { name: '张子豪', id: '2024120104', project: '数据平台综合实训', task: '测试报告', time: '2024-06-12 13:47', score: '—', status: '待评阅' },
  { name: '刘雨桐', id: '2024120105', project: '企业应用开发实训', task: '需求分析说明', time: '2024-06-12 13:27', score: '—', status: '待评阅' },
]
const queue = [
  ['代码实现', '18 份'], ['系统设计文档', '12 份'], ['测试报告', '9 份'], ['需求分析说明', '6 份'],
]
const activeTab = ref('all')

function initCharts() {
  trendChart?.dispose(); abilityChart?.dispose()
  trendChart = echarts.init(trendElement.value)
  abilityChart = echarts.init(abilityElement.value)
  trendChart.setOption({
    grid: { left: 34, right: 18, top: 34, bottom: 28 }, tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['05-12', '05-19', '05-26', '06-02', '06-09', '06-12'], axisTick: { show: false }, axisLine: { lineStyle: { color: '#E9EDF5' } }, axisLabel: { color: '#7A8499', fontSize: 11 } },
    yAxis: { type: 'value', min: 40, max: 100, splitLine: { lineStyle: { color: '#F0F2F6' } }, axisLabel: { color: '#7A8499', fontSize: 11 } },
    series: [
      { name: '班级平均分', type: 'line', smooth: true, data: [71, 74, 73, 77, 79, 84], symbolSize: 6, lineStyle: { color: '#165DFF', width: 2.5 }, itemStyle: { color: '#165DFF' } },
      { name: '优秀率', type: 'line', smooth: true, data: [49, 44, 52, 50, 56, 62], symbolSize: 6, lineStyle: { color: '#14B8A6', width: 2.5 }, itemStyle: { color: '#14B8A6' } },
    ],
  })
  abilityChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{ type: 'pie', radius: ['52%', '73%'], center: ['45%', '51%'], label: { show: false }, data: [
      { value: 82.4, name: '需求分析', itemStyle: { color: '#165DFF' } }, { value: 76.1, name: '系统设计', itemStyle: { color: '#14B8A6' } },
      { value: 81.3, name: '编码实现', itemStyle: { color: '#5E84F4' } }, { value: 69.8, name: '测试调试', itemStyle: { color: '#F6B94B' } },
      { value: 74.6, name: '文档编写', itemStyle: { color: '#8B6FE8' } }, { value: 88.2, name: '工程规范', itemStyle: { color: '#F58B55' } },
    ] }],
  })
}
function resizeCharts() { trendChart?.resize(); abilityChart?.resize() }
function startReview(row) { ElMessage.success(`已打开 ${row.name} 的${row.task}评阅任务`) }
function showInfo(label) { ElMessage.info(`${label}功能即将开放`) }
function markAllRead() { ElMessage.success('系统通知已全部标记为已读') }

onMounted(async () => { await nextTick(); initCharts(); window.addEventListener('resize', resizeCharts) })
onBeforeUnmount(() => { window.removeEventListener('resize', resizeCharts); trendChart?.dispose(); abilityChart?.dispose() })
watch(() => userStore.role, () => nextTick(initCharts))
</script>

<template>
  <section class="dashboard-page">
    <div class="dashboard-hero">
      <div>
        <p class="page-eyebrow">{{ copy.role }}</p>
        <h2>{{ copy.greeting }}，{{ userStore.name }}</h2>
        <p>{{ copy.caption }}</p>
      </div>
      <div class="hero-date"><el-icon><Timer /></el-icon> 2026 年 6 月 23 日 · 星期二</div>
    </div>

    <section class="dashboard-filter" aria-label="数据筛选">
      <el-select model-value="2024软件工程1班" aria-label="选择教学班"><el-option label="2024软件工程1班" value="2024软件工程1班" /></el-select>
      <el-select model-value="全部项目" aria-label="选择实训项目"><el-option label="全部项目" value="全部项目" /></el-select>
      <el-date-picker model-value="2026-06-23" type="date" value-format="YYYY-MM-DD" aria-label="选择统计日期" />
      <el-button text type="primary"><el-icon><Timer /></el-icon> 重置筛选</el-button>
    </section>

    <div class="metric-strip">
      <article v-for="metric in metrics" :key="metric.label" class="metric-item">
        <span class="metric-icon" :class="`tone-${metric.tone}`"><el-icon><component :is="metric.icon" /></el-icon></span>
        <div><p>{{ metric.label }}</p><strong>{{ metric.value }}<small>{{ metric.unit }}</small></strong><span class="metric-delta">{{ metric.delta }}</span></div>
      </article>
      <div class="metric-actions">
        <el-button type="primary" plain @click="ElMessage.success('已创建新的评价任务')">新建评价任务</el-button>
        <el-button @click="ElMessage.info('批量评阅功能已就绪')">批量评阅</el-button>
      </div>
    </div>

    <div class="dashboard-grid top-grid">
      <article class="data-panel trend-panel">
        <div class="panel-heading"><div><h3>班级整体表现趋势</h3><span>近六周学习表现变化</span></div><el-button text type="primary" @click="showInfo('趋势详情')">查看详情 <el-icon><ArrowRight /></el-icon></el-button></div>
        <div ref="trendElement" class="chart-region" aria-label="班级整体表现趋势图"></div>
        <div class="stat-foot"><div><span>班级平均分</span><strong>78.6 分</strong></div><div><span>优秀率</span><strong>48.6 %</strong></div><div><span>及格率</span><strong>92.1 %</strong></div><div><span>低分率</span><strong>7.9 %</strong></div></div>
      </article>

      <article class="data-panel ability-panel">
        <div class="panel-heading"><div><h3>能力维度分布</h3><span>评价能力项平均得分</span></div><el-button text type="primary" @click="showInfo('能力详情')">查看详情 <el-icon><ArrowRight /></el-icon></el-button></div>
        <div class="ability-body"><div ref="abilityElement" class="ability-chart" aria-label="能力维度分布图"></div><dl class="ability-list"><template v-for="item in [['需求分析','82.4'],['系统设计','76.1'],['编码实现','81.3'],['测试调试','69.8'],['文档编写','74.6'],['工程规范','88.2']]" :key="item[0]"><dt>{{ item[0] }}</dt><dd>{{ item[1] }}</dd></template></dl></div>
      </article>

      <aside class="side-rail">
        <article class="data-panel compact-panel"><div class="panel-heading"><h3>快捷操作</h3></div><div class="quick-actions"><el-button @click="ElMessage.success('评价任务创建成功')"><el-icon><DocumentChecked /></el-icon>新建评价任务</el-button><el-button @click="ElMessage.info('已进入批量评阅')"><el-icon><CircleCheck /></el-icon>批量评阅</el-button><el-button @click="showInfo('评分规则管理')"><el-icon><Histogram /></el-icon>评分规则管理</el-button><el-button @click="showInfo('评阅进度')"><el-icon><Timer /></el-icon>评阅进度</el-button></div></article>
        <article class="data-panel compact-panel queue-panel"><div class="panel-heading"><h3>评估队列分布</h3><el-button text type="primary" @click="showInfo('评估队列')">查看全部</el-button></div><ul><li v-for="item in queue" :key="item[0]"><span><el-icon><DocumentChecked /></el-icon>{{ item[0] }}</span><strong>{{ item[1] }}</strong></li></ul></article>
      </aside>
    </div>

    <div class="dashboard-grid bottom-grid">
      <article class="data-panel review-panel">
        <div class="panel-heading review-heading"><div><h3>{{ copy.queue }}</h3><el-tabs v-model="activeTab" class="review-tabs"><el-tab-pane label="全部 (48)" name="all" /><el-tab-pane label="AI 初评完成 (28)" name="ai" /><el-tab-pane label="超时未评 (7)" name="late" /></el-tabs></div><div><el-select size="small" model-value="全部" aria-label="评价状态"><el-option label="全部" value="全部" /></el-select><el-button size="small" @click="showInfo('批量操作')">批量操作</el-button></div></div>
        <el-table :data="rows" class="review-table" table-layout="auto">
          <el-table-column label="学生姓名" min-width="120"><template #default="{ row }"><div class="student-cell"><el-avatar :size="26">{{ row.name.slice(0, 1) }}</el-avatar><span>{{ row.name }}</span></div></template></el-table-column>
          <el-table-column prop="project" label="实训项目" min-width="150" show-overflow-tooltip />
          <el-table-column prop="task" label="任务名称" min-width="120" />
          <el-table-column prop="time" label="提交时间" min-width="142" />
          <el-table-column prop="score" label="AI初评得分" min-width="98" />
          <el-table-column label="状态" min-width="108"><template #default="{ row }"><el-tag size="small" :type="row.status.includes('AI') ? 'success' : 'primary'" effect="plain">{{ row.status }}</el-tag></template></el-table-column>
          <el-table-column label="操作" width="84" fixed="right"><template #default="{ row }"><el-button text type="primary" @click="startReview(row)">开始评阅</el-button></template></el-table-column>
        </el-table>
        <div class="table-footer"><span>共 48 条</span><el-pagination background layout="prev, pager, next" :total="48" :page-size="10" /></div>
      </article>
      <aside class="data-panel notification-panel"><div class="panel-heading"><h3>系统通知</h3><el-button text type="primary" @click="markAllRead">全部已读</el-button></div><ul class="notice-list"><li><span class="notice-dot is-danger"></span><div><strong>有 7 份评阅任务已超时</strong><p>请尽快完成评阅，避免影响学生成绩统计。</p></div><time>10:30</time></li><li><span class="notice-dot"></span><div><strong>智能评价规则已更新</strong><p>代码规范检测规则已升级，点击查看详情。</p></div><time>09:15</time></li><li><span class="notice-dot"></span><div><strong>实训项目阶段提醒</strong><p>“电商系统开发实训”已进入总结评价阶段。</p></div><time>昨天</time></li></ul></aside>
    </div>
  </section>
</template>
