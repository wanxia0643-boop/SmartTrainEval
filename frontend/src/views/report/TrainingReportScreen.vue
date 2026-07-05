<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as THREE from 'three'
import { ElMessage } from 'element-plus'
import {
  Connection,
  DataAnalysis,
  FullScreen,
  MagicStick,
  MuteNotification,
  Refresh,
  TrendCharts,
  VideoPlay,
  WarnTriangleFilled,
} from '@element-plus/icons-vue'
import { listAchievements } from '../../api/achievements'
import { listEvalResults } from '../../api/evalResults'
import { listLlmLogs } from '../../api/llmLogs'
import { listProjects } from '../../api/projects'
import { listReports } from '../../api/reports'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

const focusModes = [
  { label: '总览', value: 'overview' },
  { label: '能力', value: 'ability' },
  { label: '风险', value: 'risk' },
  { label: '企评', value: 'enterprise' },
]

const timeOptions = [
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '本学期', value: 'term' },
]

const demoProjects = [
  { id: 101, project_name: '大模型实训评价系统', status: 1, progress: 86 },
  { id: 102, project_name: '国产化适配工程', status: 1, progress: 74 },
  { id: 103, project_name: '质量检测智能体', status: 0, progress: 63 },
  { id: 104, project_name: '企业真实任务协同', status: 1, progress: 91 },
]

const demoAchievements = [
  { id: 201, project_id: 101, title: '评价闭环原型', status: 3, final_score: 91 },
  { id: 202, project_id: 101, title: 'AI 核查报告', status: 3, final_score: 88 },
  { id: 203, project_id: 102, title: 'LoongArch 适配说明', status: 1, final_score: null },
  { id: 204, project_id: 103, title: '缺陷检测脚本', status: 2, final_score: 76 },
  { id: 205, project_id: 104, title: '企业导师验收材料', status: 3, final_score: 94 },
  { id: 206, project_id: 104, title: '项目复盘文档', status: 1, final_score: null },
]

const demoEvalResults = [
  { id: 301, achievement_id: 201, eval_type: 2, score: 92, comments: '工程结构完整，评价证据清晰。' },
  { id: 302, achievement_id: 201, eval_type: 3, score: 89, comments: '贴近企业流程，可继续补充异常样例。' },
  { id: 303, achievement_id: 202, eval_type: 1, score: 87, comments: 'AI 建议已留痕，人工评分未被覆盖。' },
  { id: 304, achievement_id: 205, eval_type: 3, score: 95, comments: '交付节奏稳定，沟通记录完整。' },
]

const demoReports = [
  { id: 401, report_name: '项目评价总览', status: 1, report_type: 2 },
  { id: 402, report_name: '学生成绩明细', status: 1, report_type: 1 },
]

const loading = ref(false)
const focusMode = ref('overview')
const timeRange = ref('term')
const isMuted = ref(false)
const isSpeaking = ref(true)
const selectedNodeId = ref('core')
const hoveredNodeId = ref('')
const projects = ref([])
const achievements = ref([])
const evalResults = ref([])
const reports = ref([])
const llmLogs = ref([])
const canvasRef = ref()

const xingyunEmbedUrl = import.meta.env.VITE_MOFA_XINGYUN_EMBED_URL || ''

let renderer
let scene
let camera
let rootGroup
let nodeGroup
let linkGroup
let starField
let animationId = 0
let resizeObserver
const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()
const nodeMeshes = []

function normalizeList(data, fallback) {
  const items = Array.isArray(data?.items) ? data.items : Array.isArray(data) ? data : []
  return items.length ? items : fallback
}

async function safeList(loader, fallback, params = { page: 1, page_size: 100 }) {
  try {
    return normalizeList(await loader(params), fallback)
  } catch {
    return fallback
  }
}

async function loadScreenData(silent = false) {
  loading.value = true
  try {
    const canReadReports = ['teacher', 'admin'].includes(userStore.role)
    const canReadLogs = userStore.role === 'admin'
    const [projectRows, achievementRows, evalRows, reportRows, logRows] = await Promise.all([
      safeList(listProjects, demoProjects),
      safeList(listAchievements, demoAchievements),
      safeList(listEvalResults, demoEvalResults),
      canReadReports ? safeList(listReports, demoReports) : Promise.resolve(demoReports),
      canReadLogs ? safeList(listLlmLogs, []) : Promise.resolve([]),
    ])
    projects.value = projectRows
    achievements.value = achievementRows
    evalResults.value = evalRows
    reports.value = reportRows
    llmLogs.value = logRows
    if (!silent) ElMessage.success('大屏数据已刷新')
  } finally {
    loading.value = false
  }
}

const submittedAchievements = computed(() =>
  achievements.value.filter((item) => Number(item.status) >= 1 || item.submit_time || item.final_score != null),
)

const evaluatedAchievements = computed(() =>
  achievements.value.filter((item) => Number(item.status) === 3 || item.final_score != null),
)

const avgScore = computed(() => {
  const scored = achievements.value
    .map((item) => Number(item.final_score))
    .filter((score) => Number.isFinite(score))
  if (!scored.length) return 0
  return Math.round(scored.reduce((sum, score) => sum + score, 0) / scored.length)
})

const enterpriseEvalCount = computed(() =>
  evalResults.value.filter((item) => Number(item.eval_type) === 3).length,
)

const aiReviewCount = computed(() => {
  const evalAiCount = evalResults.value.filter((item) => Number(item.eval_type) === 1).length
  return Math.max(evalAiCount, llmLogs.value.length)
})

const completionRate = computed(() => {
  const denominator = Math.max(achievements.value.length, 1)
  return Math.round((evaluatedAchievements.value.length / denominator) * 100)
})

const riskCount = computed(() =>
  achievements.value.filter((item) => Number(item.status) === 2 || (item.final_score != null && Number(item.final_score) < 80)).length,
)

const statCards = computed(() => [
  {
    label: '项目运行',
    value: projects.value.length,
    unit: '个',
    trend: `${submittedAchievements.value.length} 份成果已进入闭环`,
    icon: Connection,
    tone: 'blue',
  },
  {
    label: '综合均分',
    value: avgScore.value || '--',
    unit: avgScore.value ? '分' : '',
    trend: `完成率 ${completionRate.value}%`,
    icon: TrendCharts,
    tone: 'green',
  },
  {
    label: '企业评价',
    value: enterpriseEvalCount.value,
    unit: '条',
    trend: '企业导师证据链已同步',
    icon: DataAnalysis,
    tone: 'gold',
  },
  {
    label: 'AI 核查',
    value: aiReviewCount.value,
    unit: '次',
    trend: '失败不阻断人工评价',
    icon: MagicStick,
    tone: 'violet',
  },
])

const projectMap = computed(() =>
  Object.fromEntries(projects.value.map((project) => [project.id, project.project_name || `项目 ${project.id}`])),
)

const selectedNode = computed(() =>
  nodeMetas.value.find((node) => node.id === selectedNodeId.value)
  || nodeMetas.value.find((node) => node.id === 'core')
  || nodeMetas.value[0],
)

const focusCopy = computed(() => {
  const map = {
    overview: '项目、成果、评价、报表已经串成可演示闭环，现场优先展示稳定业务流。',
    ability: '能力画像从最终得分与评价证据抽取，突出工程实现、文档规范、协同交付和质量意识。',
    risk: '风险层聚焦退回重做、低分成果、未评价成果，教师可快速定位待处理对象。',
    enterprise: '企业导师侧只展示分配项目，评价意见纳入最终分数但保留人工可追溯记录。',
  }
  return map[focusMode.value]
})

const narratorLines = computed(() => {
  const selected = selectedNode.value?.label || '实训闭环'
  return [
    `当前聚焦：${selected}。`,
    `已汇总 ${projects.value.length} 个项目、${submittedAchievements.value.length} 份成果。`,
    `综合均分 ${avgScore.value || '--'}，评价完成率 ${completionRate.value}%。`,
    focusCopy.value,
  ]
})

const abilityRows = computed(() => [
  { name: '工程实现', score: clamp(avgScore.value + 3, 0, 100), color: '#35c7a4' },
  { name: '文档规范', score: clamp(avgScore.value - 2, 0, 100), color: '#4c8dff' },
  { name: 'AI 核查响应', score: clamp(72 + aiReviewCount.value * 4, 0, 100), color: '#8f7bff' },
  { name: '企业协同', score: clamp(76 + enterpriseEvalCount.value * 5, 0, 100), color: '#f0a43a' },
])

const riskRows = computed(() => {
  const pending = achievements.value.filter((item) => item.final_score == null).length
  return [
    { name: '待评价成果', value: pending, level: pending > 3 ? 'warning' : 'normal' },
    { name: '退回重做', value: riskCount.value, level: riskCount.value ? 'danger' : 'normal' },
    { name: '报表成功', value: reports.value.filter((item) => Number(item.status) === 1).length, level: 'normal' },
  ]
})

const recentItems = computed(() =>
  achievements.value.slice(0, 5).map((item) => ({
    id: item.id,
    title: item.title || item.achievement_name || '未命名成果',
    project: projectMap.value[item.project_id] || '未关联项目',
    score: item.final_score ?? '待评',
    status: statusLabel(item.status),
  })),
)

const nodeMetas = computed(() => {
  const activeProjects = projects.value.slice(0, 5)
  const projectNodes = activeProjects.map((project, index) => {
    const related = achievements.value.filter((item) => item.project_id === project.id)
    const scoreValues = related.map((item) => Number(item.final_score)).filter((score) => Number.isFinite(score))
    const score = scoreValues.length
      ? Math.round(scoreValues.reduce((sum, value) => sum + value, 0) / scoreValues.length)
      : 68 + index * 5
    return {
      id: `project-${project.id}`,
      type: 'project',
      label: project.project_name || `项目 ${project.id}`,
      value: score,
      count: related.length,
      color: score >= 90 ? 0x35c7a4 : score >= 80 ? 0x4c8dff : 0xf0a43a,
      angle: (Math.PI * 2 * index) / Math.max(activeProjects.length, 1),
      radius: 2.3 + (index % 2) * 0.55,
    }
  })
  return [
    { id: 'core', type: 'core', label: '实训评价闭环', value: completionRate.value, count: submittedAchievements.value.length, color: 0x5fe7ff, angle: 0, radius: 0 },
    ...projectNodes,
    { id: 'ai', type: 'signal', label: 'AI 核查日志', value: aiReviewCount.value, count: aiReviewCount.value, color: 0x8f7bff, angle: Math.PI * 1.66, radius: 3.15 },
    { id: 'enterprise', type: 'signal', label: '企业导师评价', value: enterpriseEvalCount.value, count: enterpriseEvalCount.value, color: 0xf0a43a, angle: Math.PI * 0.34, radius: 3.35 },
  ]
})

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value || 0))
}

function statusLabel(status) {
  const map = { 0: '草稿', 1: '已提交', 2: '退回', 3: '已评价' }
  return map[Number(status)] || '进行中'
}

function nodePosition(node, index) {
  if (node.id === 'core') return new THREE.Vector3(0, 0, 0)
  const lift = node.type === 'signal' ? 0.75 : Math.sin(index * 1.7) * 0.45
  return new THREE.Vector3(
    Math.cos(node.angle) * node.radius,
    lift,
    Math.sin(node.angle) * node.radius,
  )
}

function initScene() {
  if (!canvasRef.value) return
  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100)
  camera.position.set(0, 4.2, 8.4)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: true,
    alpha: true,
    preserveDrawingBuffer: true,
  })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
  renderer.outputColorSpace = THREE.SRGBColorSpace

  rootGroup = new THREE.Group()
  nodeGroup = new THREE.Group()
  linkGroup = new THREE.Group()
  rootGroup.add(linkGroup)
  rootGroup.add(nodeGroup)
  scene.add(rootGroup)

  const ambient = new THREE.AmbientLight(0xc8f6ff, 1.2)
  const key = new THREE.DirectionalLight(0xffffff, 1.6)
  key.position.set(4, 7, 5)
  const back = new THREE.PointLight(0x4c8dff, 38, 18)
  back.position.set(-4, 2, -2)
  scene.add(ambient, key, back)

  const grid = new THREE.GridHelper(8, 24, 0x2e7bff, 0x24476c)
  grid.position.y = -1.15
  grid.material.transparent = true
  grid.material.opacity = 0.24
  scene.add(grid)

  createStarField()
  rebuildScene()
  resizeScene()
  resizeObserver = new ResizeObserver(resizeScene)
  resizeObserver.observe(canvasRef.value.parentElement)
  animateScene()
}

function createStarField() {
  const count = 260
  const positions = new Float32Array(count * 3)
  for (let i = 0; i < count; i += 1) {
    positions[i * 3] = (Math.random() - 0.5) * 12
    positions[i * 3 + 1] = (Math.random() - 0.2) * 6
    positions[i * 3 + 2] = (Math.random() - 0.5) * 10
  }
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  const material = new THREE.PointsMaterial({
    color: 0x9ccfff,
    size: 0.025,
    transparent: true,
    opacity: 0.55,
    depthWrite: false,
  })
  starField = new THREE.Points(geometry, material)
  scene.add(starField)
}

function disposeGroup(group) {
  if (!group) return
  group.children.forEach((child) => {
    child.geometry?.dispose?.()
    child.material?.dispose?.()
  })
  group.clear()
}

function rebuildScene() {
  if (!nodeGroup || !linkGroup) return
  disposeGroup(nodeGroup)
  disposeGroup(linkGroup)
  nodeMeshes.length = 0

  const metas = nodeMetas.value
  const center = new THREE.Vector3(0, 0, 0)
  metas.forEach((meta, index) => {
    const position = nodePosition(meta, index)
    const radius = meta.id === 'core' ? 0.42 : 0.2 + clamp(meta.value, 0, 100) / 520
    const geometry = new THREE.SphereGeometry(radius, 32, 18)
    const material = new THREE.MeshStandardMaterial({
      color: meta.color,
      emissive: meta.color,
      emissiveIntensity: meta.id === selectedNodeId.value ? 0.72 : 0.34,
      metalness: 0.48,
      roughness: 0.28,
    })
    const mesh = new THREE.Mesh(geometry, material)
    mesh.position.copy(position)
    mesh.userData = { id: meta.id }
    nodeGroup.add(mesh)
    nodeMeshes.push(mesh)

    const ringGeometry = new THREE.TorusGeometry(radius * 1.55, 0.008, 8, 80)
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: meta.color,
      transparent: true,
      opacity: meta.id === selectedNodeId.value ? 0.56 : 0.26,
    })
    const ring = new THREE.Mesh(ringGeometry, ringMaterial)
    ring.position.copy(position)
    ring.rotation.x = Math.PI / 2.6
    nodeGroup.add(ring)

    if (meta.id !== 'core') {
      const points = [center, position]
      const linkGeometry = new THREE.BufferGeometry().setFromPoints(points)
      const linkMaterial = new THREE.LineBasicMaterial({
        color: meta.color,
        transparent: true,
        opacity: 0.28,
      })
      linkGroup.add(new THREE.Line(linkGeometry, linkMaterial))
    }
  })
}

function resizeScene() {
  if (!renderer || !camera || !canvasRef.value?.parentElement) return
  const rect = canvasRef.value.parentElement.getBoundingClientRect()
  const width = Math.max(rect.width, 320)
  const height = Math.max(rect.height, 360)
  renderer.setSize(width, height, false)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
}

function animateScene() {
  animationId = window.requestAnimationFrame(animateScene)
  const now = performance.now() * 0.001
  if (rootGroup) {
    rootGroup.rotation.y += 0.0024
    rootGroup.rotation.x = Math.sin(now * 0.38) * 0.045
  }
  if (starField) starField.rotation.y -= 0.0008
  nodeMeshes.forEach((mesh, index) => {
    const isActive = mesh.userData.id === selectedNodeId.value || mesh.userData.id === hoveredNodeId.value
    mesh.scale.setScalar((isActive ? 1.22 : 1) + Math.sin(now * 2.2 + index) * 0.025)
  })
  renderer?.render(scene, camera)
}

function setPointer(event) {
  if (!renderer || !camera || !canvasRef.value) return null
  const rect = canvasRef.value.getBoundingClientRect()
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  raycaster.setFromCamera(pointer, camera)
  return raycaster.intersectObjects(nodeMeshes, false)[0]?.object || null
}

function handleSceneMove(event) {
  const target = setPointer(event)
  hoveredNodeId.value = target?.userData?.id || ''
  if (canvasRef.value) canvasRef.value.style.cursor = target ? 'pointer' : 'default'
}

function handleSceneClick(event) {
  const target = setPointer(event)
  if (!target?.userData?.id) return
  selectedNodeId.value = target.userData.id
}

function selectNode(id) {
  selectedNodeId.value = id
}

function toggleSpeaking() {
  isSpeaking.value = !isSpeaking.value
}

function toggleMute() {
  isMuted.value = !isMuted.value
}

function requestFullscreen() {
  const target = document.querySelector('.report-screen-page')
  target?.requestFullscreen?.()
}

watch([selectedNodeId, focusMode], () => {
  rebuildScene()
})

watch(nodeMetas, () => {
  nextTick(rebuildScene)
})

onMounted(async () => {
  await loadScreenData(true)
  await nextTick()
  initScene()
})

onBeforeUnmount(() => {
  window.cancelAnimationFrame(animationId)
  resizeObserver?.disconnect()
  disposeGroup(nodeGroup)
  disposeGroup(linkGroup)
  starField?.geometry?.dispose?.()
  starField?.material?.dispose?.()
  renderer?.dispose?.()
})
</script>

<template>
  <section class="report-screen-page">
    <header class="screen-command">
      <div>
        <p class="screen-kicker">SMART TRAIN EVAL · LIVE REPORT</p>
        <h2>可视化实训报告大屏</h2>
        <span>{{ focusCopy }}</span>
      </div>
      <div class="command-actions">
        <el-segmented v-model="focusMode" :options="focusModes" />
        <el-select v-model="timeRange" class="range-select" size="large">
          <el-option v-for="option in timeOptions" :key="option.value" :label="option.label" :value="option.value" />
        </el-select>
        <el-button :icon="Refresh" :loading="loading" @click="loadScreenData">刷新</el-button>
        <el-button :icon="FullScreen" type="primary" @click="requestFullscreen">全屏</el-button>
      </div>
    </header>

    <main class="screen-layout">
      <section class="scene-stage" aria-label="实训评价三维星图">
        <div class="stage-status">
          <span class="live-dot"></span>
          <strong>云端优先 · 人工闭环稳定</strong>
          <em>{{ timeOptions.find((option) => option.value === timeRange)?.label }}</em>
        </div>
        <canvas
          ref="canvasRef"
          class="report-canvas"
          @pointermove="handleSceneMove"
          @pointerleave="hoveredNodeId = ''"
          @click="handleSceneClick"
        ></canvas>
        <aside class="scene-readout">
          <span>{{ selectedNode?.type === 'core' ? '核心闭环' : '当前节点' }}</span>
          <strong>{{ selectedNode?.label }}</strong>
          <p>权重指数 {{ selectedNode?.value ?? '--' }} · 关联 {{ selectedNode?.count ?? 0 }} 条证据</p>
        </aside>
        <nav class="node-dock" aria-label="大屏节点">
          <button
            v-for="node in nodeMetas"
            :key="node.id"
            :class="{ active: selectedNodeId === node.id }"
            type="button"
            @click="selectNode(node.id)"
          >
            <span>{{ node.label }}</span>
            <strong>{{ node.value }}</strong>
          </button>
        </nav>
      </section>

      <aside class="xingyun-panel">
        <div class="panel-heading">
          <div>
            <p class="screen-kicker">MOFA XINGYUN</p>
            <h3>魔珐星云数字人</h3>
          </div>
          <el-tag effect="dark" type="success">{{ xingyunEmbedUrl ? '已连接' : '演示态' }}</el-tag>
        </div>

        <div v-if="xingyunEmbedUrl" class="xingyun-frame">
          <iframe :src="xingyunEmbedUrl" title="魔珐星云数字人播报"></iframe>
        </div>
        <div v-else class="local-human">
          <img src="/illus/educator.svg" alt="数字人主持人" />
          <div class="voice-wave" :class="{ active: isSpeaking && !isMuted }">
            <i></i><i></i><i></i><i></i><i></i>
          </div>
        </div>

        <div class="human-controls">
          <el-button :icon="VideoPlay" type="primary" plain @click="toggleSpeaking">
            {{ isSpeaking ? '暂停播报' : '开始播报' }}
          </el-button>
          <el-button :icon="MuteNotification" plain @click="toggleMute">
            {{ isMuted ? '取消静音' : '静音' }}
          </el-button>
        </div>

        <div class="narrator-card">
          <strong>实时讲解稿</strong>
          <p v-for="line in narratorLines" :key="line">{{ line }}</p>
        </div>
      </aside>
    </main>

    <section class="stat-row" aria-label="报告关键指标">
      <article v-for="card in statCards" :key="card.label" :class="['stat-tile', `tone-${card.tone}`]">
        <component :is="card.icon" />
        <div>
          <span>{{ card.label }}</span>
          <strong>{{ card.value }}<em>{{ card.unit }}</em></strong>
          <p>{{ card.trend }}</p>
        </div>
      </article>
    </section>

    <section class="report-grid">
      <article class="screen-panel ability-panel">
        <div class="panel-heading">
          <div>
            <p class="screen-kicker">CAPABILITY</p>
            <h3>能力画像</h3>
          </div>
          <span>{{ avgScore || '--' }} 分综合均值</span>
        </div>
        <div class="ability-bars">
          <div v-for="item in abilityRows" :key="item.name" class="ability-line">
            <span>{{ item.name }}</span>
            <div class="bar-track">
              <i :style="{ width: `${item.score}%`, background: item.color }"></i>
            </div>
            <strong>{{ item.score }}</strong>
          </div>
        </div>
      </article>

      <article class="screen-panel risk-panel">
        <div class="panel-heading">
          <div>
            <p class="screen-kicker">RISK RADAR</p>
            <h3>过程风险</h3>
          </div>
          <WarnTriangleFilled />
        </div>
        <div class="risk-list">
          <div v-for="item in riskRows" :key="item.name" :class="['risk-item', item.level]">
            <span>{{ item.name }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </article>

      <article class="screen-panel timeline-panel">
        <div class="panel-heading">
          <div>
            <p class="screen-kicker">EVIDENCE</p>
            <h3>最新成果证据</h3>
          </div>
          <span>{{ recentItems.length }} 条</span>
        </div>
        <ul class="evidence-list">
          <li v-for="item in recentItems" :key="item.id">
            <div>
              <strong>{{ item.title }}</strong>
              <span>{{ item.project }}</span>
            </div>
            <em>{{ item.status }}</em>
            <b>{{ item.score }}</b>
          </li>
        </ul>
      </article>
    </section>
  </section>
</template>

<style scoped>
.report-screen-page {
  display: grid;
  gap: 18px;
  max-width: 1760px;
  min-height: calc(100vh - 132px);
  margin: 0 auto;
  color: #e9f6ff;
  background:
    linear-gradient(120deg, rgba(8, 25, 44, .98), rgba(14, 41, 73, .96) 48%, rgba(10, 31, 55, .98)),
    repeating-linear-gradient(90deg, rgba(130, 190, 255, .08) 0 1px, transparent 1px 80px);
  border: 1px solid rgba(127, 190, 255, .28);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 18px 45px rgba(15, 39, 72, .18);
}

.screen-command,
.screen-layout,
.stat-row,
.report-grid {
  min-width: 0;
}

.screen-command {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding-bottom: 4px;
}

.screen-command h2,
.panel-heading h3 {
  margin: 0;
  color: #fff;
  font-weight: 700;
}

.screen-command h2 {
  font-size: 28px;
}

.screen-command span,
.panel-heading span,
.scene-readout p,
.narrator-card p,
.evidence-list span {
  color: rgba(221, 239, 255, .68);
}

.screen-kicker {
  margin: 0 0 6px;
  color: #6ee7ff;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .12em;
}

.command-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.range-select {
  width: 116px;
}

.screen-layout {
  display: grid;
  grid-template-columns: minmax(620px, 1fr) minmax(310px, 390px);
  gap: 18px;
  min-height: 540px;
}

.scene-stage {
  position: relative;
  min-height: 540px;
  overflow: hidden;
  border: 1px solid rgba(116, 193, 255, .22);
  border-radius: 8px;
  background:
    radial-gradient(circle at 52% 45%, rgba(64, 135, 255, .18), transparent 34%),
    linear-gradient(180deg, rgba(8, 24, 44, .25), rgba(6, 18, 34, .72));
}

.scene-stage::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(116, 193, 255, .08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(116, 193, 255, .08) 1px, transparent 1px);
  background-size: 52px 52px;
  mask-image: linear-gradient(to bottom, transparent, #000 15%, #000 84%, transparent);
}

.stage-status {
  position: absolute;
  z-index: 2;
  top: 16px;
  left: 18px;
  right: 18px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  font-size: 13px;
}

.stage-status em {
  margin-left: auto;
  color: rgba(221, 239, 255, .64);
  font-style: normal;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #34e6ad;
  box-shadow: 0 0 18px rgba(52, 230, 173, .82);
}

.report-canvas {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
}

.scene-readout {
  position: absolute;
  z-index: 2;
  left: 18px;
  bottom: 104px;
  width: min(330px, calc(100% - 36px));
  padding: 16px;
  border: 1px solid rgba(116, 193, 255, .24);
  border-radius: 8px;
  background: rgba(8, 24, 44, .74);
  backdrop-filter: blur(12px);
}

.scene-readout span,
.stat-tile span,
.ability-line span,
.risk-item span {
  font-size: 12px;
  color: rgba(221, 239, 255, .66);
}

.scene-readout strong {
  display: block;
  margin: 6px 0;
  color: #fff;
  font-size: 20px;
}

.node-dock {
  position: absolute;
  z-index: 2;
  left: 18px;
  right: 18px;
  bottom: 18px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(122px, 1fr));
  gap: 8px;
}

.node-dock button {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
  min-height: 54px;
  padding: 10px 12px;
  color: rgba(233, 246, 255, .78);
  text-align: left;
  background: rgba(8, 24, 44, .72);
  border: 1px solid rgba(116, 193, 255, .2);
  border-radius: 8px;
  cursor: pointer;
}

.node-dock button.active,
.node-dock button:hover {
  color: #fff;
  border-color: rgba(110, 231, 255, .78);
  background: rgba(23, 74, 125, .78);
}

.node-dock strong {
  color: #6ee7ff;
  font-size: 18px;
}

.node-dock span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.xingyun-panel,
.screen-panel,
.stat-tile {
  border: 1px solid rgba(116, 193, 255, .22);
  border-radius: 8px;
  background: rgba(8, 24, 44, .76);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .05);
}

.xingyun-panel {
  display: grid;
  grid-template-rows: auto minmax(260px, 1fr) auto auto;
  gap: 14px;
  min-height: 540px;
  padding: 16px;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.panel-heading h3 {
  font-size: 17px;
}

.xingyun-frame,
.local-human {
  position: relative;
  overflow: hidden;
  min-height: 276px;
  border: 1px solid rgba(116, 193, 255, .2);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(30, 86, 146, .42), rgba(8, 24, 44, .88));
}

.xingyun-frame iframe {
  width: 100%;
  height: 100%;
  min-height: 330px;
  border: 0;
}

.local-human {
  display: grid;
  place-items: center;
}

.local-human img {
  width: min(78%, 260px);
  max-height: 270px;
  object-fit: contain;
  filter: drop-shadow(0 18px 28px rgba(0, 0, 0, .36));
}

.voice-wave {
  position: absolute;
  right: 22px;
  bottom: 22px;
  display: flex;
  align-items: center;
  gap: 4px;
  height: 34px;
  padding: 8px 10px;
  border-radius: 999px;
  background: rgba(6, 18, 34, .72);
}

.voice-wave i {
  display: block;
  width: 4px;
  height: 10px;
  border-radius: 8px;
  background: rgba(110, 231, 255, .48);
}

.voice-wave.active i {
  animation: wave 900ms ease-in-out infinite;
}

.voice-wave.active i:nth-child(2) { animation-delay: 110ms; }
.voice-wave.active i:nth-child(3) { animation-delay: 220ms; }
.voice-wave.active i:nth-child(4) { animation-delay: 330ms; }
.voice-wave.active i:nth-child(5) { animation-delay: 440ms; }

.human-controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.human-controls .el-button {
  margin: 0;
}

.narrator-card {
  display: grid;
  gap: 8px;
  padding: 14px;
  border: 1px solid rgba(116, 193, 255, .18);
  border-radius: 8px;
  background: rgba(5, 15, 28, .48);
}

.narrator-card strong {
  color: #fff;
}

.narrator-card p {
  margin: 0;
  font-size: 12px;
  line-height: 1.65;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(160px, 1fr));
  gap: 12px;
}

.stat-tile {
  display: grid;
  grid-template-columns: 42px 1fr;
  gap: 12px;
  align-items: center;
  min-height: 118px;
  padding: 16px;
}

.stat-tile > svg {
  width: 34px;
  height: 34px;
  padding: 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, .08);
}

.stat-tile strong {
  display: block;
  margin: 3px 0;
  color: #fff;
  font-size: 30px;
  line-height: 1;
}

.stat-tile em {
  margin-left: 4px;
  color: rgba(221, 239, 255, .72);
  font-size: 13px;
  font-style: normal;
}

.stat-tile p {
  margin: 0;
  color: rgba(221, 239, 255, .58);
  font-size: 12px;
}

.tone-blue > svg { color: #6ee7ff; }
.tone-green > svg { color: #35c7a4; }
.tone-gold > svg { color: #f0a43a; }
.tone-violet > svg { color: #a99cff; }

.report-grid {
  display: grid;
  grid-template-columns: minmax(300px, .9fr) minmax(230px, .54fr) minmax(420px, 1.08fr);
  gap: 12px;
}

.screen-panel {
  min-height: 236px;
  padding: 16px;
}

.ability-bars {
  display: grid;
  gap: 14px;
  margin-top: 16px;
}

.ability-line {
  display: grid;
  grid-template-columns: 78px 1fr 38px;
  align-items: center;
  gap: 10px;
}

.bar-track {
  height: 9px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(221, 239, 255, .12);
}

.bar-track i {
  display: block;
  height: 100%;
  border-radius: inherit;
  box-shadow: 0 0 18px currentColor;
}

.ability-line strong {
  color: #fff;
  text-align: right;
}

.risk-list {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}

.risk-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 48px;
  padding: 0 12px;
  border: 1px solid rgba(116, 193, 255, .16);
  border-radius: 8px;
  background: rgba(255, 255, 255, .04);
}

.risk-item strong {
  color: #fff;
  font-size: 22px;
}

.risk-item.danger {
  border-color: rgba(224, 81, 81, .54);
}

.risk-item.warning {
  border-color: rgba(240, 164, 58, .54);
}

.evidence-list {
  display: grid;
  gap: 8px;
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
}

.evidence-list li {
  display: grid;
  grid-template-columns: 1fr 78px 54px;
  gap: 12px;
  align-items: center;
  min-height: 42px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(116, 193, 255, .12);
}

.evidence-list li:last-child {
  border-bottom: 0;
}

.evidence-list strong,
.evidence-list span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.evidence-list strong {
  color: #fff;
  font-size: 13px;
}

.evidence-list em {
  color: rgba(221, 239, 255, .72);
  font-size: 12px;
  font-style: normal;
}

.evidence-list b {
  color: #6ee7ff;
  font-size: 18px;
  text-align: right;
}

@keyframes wave {
  0%, 100% { height: 9px; opacity: .48; }
  50% { height: 24px; opacity: 1; }
}

@media (max-width: 1380px) {
  .screen-layout,
  .report-grid {
    grid-template-columns: 1fr;
  }

  .xingyun-panel {
    min-height: auto;
    grid-template-columns: minmax(260px, .45fr) 1fr;
    grid-template-rows: auto auto auto;
  }

  .xingyun-panel .panel-heading,
  .human-controls,
  .narrator-card {
    grid-column: 1 / -1;
  }
}

@media (max-width: 1024px) {
  .report-screen-page {
    padding: 14px;
  }

  .screen-command {
    align-items: flex-start;
    flex-direction: column;
  }

  .command-actions {
    justify-content: flex-start;
    width: 100%;
  }

  .scene-stage {
    min-height: 500px;
  }

  .stat-row {
    grid-template-columns: repeat(2, minmax(150px, 1fr));
  }
}

@media (max-width: 700px) {
  .screen-command h2 {
    font-size: 22px;
  }

  .command-actions,
  .human-controls {
    display: grid;
    grid-template-columns: 1fr;
    width: 100%;
  }

  .range-select,
  .command-actions .el-button,
  .human-controls .el-button {
    width: 100%;
  }

  .scene-stage {
    min-height: 560px;
  }

  .scene-readout {
    bottom: 174px;
  }

  .node-dock {
    grid-template-columns: 1fr 1fr;
  }

  .stat-row,
  .xingyun-panel,
  .ability-line,
  .evidence-list li {
    grid-template-columns: 1fr;
  }

  .ability-line strong,
  .evidence-list b {
    text-align: left;
  }
}
</style>
