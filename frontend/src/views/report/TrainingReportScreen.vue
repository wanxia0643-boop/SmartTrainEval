<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import gsap from 'gsap'
import * as THREE from 'three'
import { CSS2DObject, CSS2DRenderer } from 'three/examples/jsm/renderers/CSS2DRenderer.js'
import { CSS3DObject, CSS3DRenderer } from 'three/examples/jsm/renderers/CSS3DRenderer.js'
import { ElMessage } from 'element-plus'
import {
  Aim,
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
import { getXingyunConfig } from '../../api/xingyun'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

const layerToggles = [
  { key: 'flight', label: '飞线', icon: Connection },
  { key: 'label', label: '标签', icon: DataAnalysis },
  { key: 'marker', label: '点位', icon: Aim },
  { key: 'heat', label: '热力层', icon: TrendCharts },
  { key: 'bar', label: '渐变柱', icon: MagicStick },
]

const focusModes = [
  { label: '总览', value: 'overview' },
  { label: '评分', value: 'score' },
  { label: '风险', value: 'risk' },
  { label: '企业', value: 'enterprise' },
]

const timeOptions = [
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '本学期', value: 'term' },
]

const demoProjects = [
  { id: 101, project_name: '大模型实训评价系统', status: 1, progress: 92 },
  { id: 102, project_name: '国产化适配工程', status: 1, progress: 78 },
  { id: 103, project_name: '企业真实任务协同', status: 1, progress: 86 },
  { id: 104, project_name: 'AI 核查质量画像', status: 0, progress: 64 },
  { id: 105, project_name: '报告自动生成与导出', status: 1, progress: 81 },
]

const demoAchievements = [
  { id: 201, project_id: 101, title: '评价闭环原型', status: 3, final_score: 94 },
  { id: 202, project_id: 101, title: 'AI 核查报告', status: 3, final_score: 90 },
  { id: 203, project_id: 102, title: 'LoongArch 适配说明', status: 1, final_score: 82 },
  { id: 204, project_id: 103, title: '企业导师验收材料', status: 3, final_score: 96 },
  { id: 205, project_id: 104, title: '缺陷检测脚本', status: 2, final_score: 74 },
  { id: 206, project_id: 105, title: '项目复盘文档', status: 1, final_score: null },
]

const demoEvalResults = [
  { id: 301, achievement_id: 201, eval_type: 2, score: 93, comments: '工程结构完整，指标证据清晰。' },
  { id: 302, achievement_id: 201, eval_type: 3, score: 91, comments: '贴近企业流程，可继续补充异常样例。' },
  { id: 303, achievement_id: 202, eval_type: 1, score: 88, comments: 'AI 建议已留痕，人工评分未被覆盖。' },
  { id: 304, achievement_id: 204, eval_type: 3, score: 96, comments: '交付节奏稳定，沟通记录完整。' },
]

const demoReports = [
  { id: 401, report_name: '项目评价总览', status: 1, report_type: 2 },
  { id: 402, report_name: '学生成绩明细', status: 1, report_type: 1 },
]

const fallbackGeoJson = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { name: '北部创新区', center: [111.5, 38.7], value: 92 },
      geometry: { type: 'Polygon', coordinates: [[[104, 38.6], [107.4, 40.8], [112.4, 40.7], [116, 38.8], [112.8, 37.5], [107.2, 37.4], [104, 38.6]]] },
    },
    {
      type: 'Feature',
      properties: { name: '西部实训区', center: [103.8, 34.5], value: 78 },
      geometry: { type: 'Polygon', coordinates: [[[98.5, 34.6], [101.2, 37.1], [106.8, 37.4], [107.3, 33.3], [102.6, 31.6], [98.5, 34.6]]] },
    },
    {
      type: 'Feature',
      properties: { name: '中部评价区', center: [111.8, 34.1], value: 86 },
      geometry: { type: 'Polygon', coordinates: [[[107.3, 33.3], [107.8, 37.4], [113, 37.4], [116.2, 35], [114.7, 31.8], [109.4, 31.2], [107.3, 33.3]]] },
    },
    {
      type: 'Feature',
      properties: { name: '东部协同区', center: [119.2, 33.8], value: 90 },
      geometry: { type: 'Polygon', coordinates: [[[115.5, 35.1], [119.5, 36.7], [123.4, 34.3], [122.5, 31], [118.7, 30.1], [114.7, 31.8], [115.5, 35.1]]] },
    },
    {
      type: 'Feature',
      properties: { name: '南部成果区', center: [111.6, 28.4], value: 84 },
      geometry: { type: 'Polygon', coordinates: [[[106.2, 29.4], [109.4, 31.2], [114.8, 31.8], [118.7, 30.1], [116.6, 26.5], [111.2, 25.6], [106.2, 29.4]]] },
    },
    {
      type: 'Feature',
      properties: { name: '湾区产业区', center: [116.2, 23.6], value: 95 },
      geometry: { type: 'Polygon', coordinates: [[[111.2, 25.6], [116.6, 26.5], [120.6, 23.8], [117.9, 20.9], [113.2, 20.8], [111.2, 25.6]]] },
    },
  ],
}

const loading = ref(false)
const focusMode = ref('overview')
const timeRange = ref('term')
const layers = ref({ flight: true, label: true, marker: true, heat: true, bar: true })
const isMuted = ref(false)
const isSpeaking = ref(true)
const briefingScript = ref('')
const selectedRegionId = ref('')
const hoveredInfo = ref(null)
const projects = ref([])
const achievements = ref([])
const evalResults = ref([])
const reports = ref([])
const llmLogs = ref([])
const geoJson = ref(fallbackGeoJson)

const stageRef = ref()
const canvasRef = ref()
const ringChartRef = ref()
const barChartRef = ref()
const lineChartRef = ref()
const mixChartRef = ref()

const xingyunSdkRef = ref()
const xingyunEnabled = ref(false)
const xingyunLoading = ref(false)
const xingyunReady = ref(false)
const xingyunError = ref('')
const xingyunProgress = ref(0)

let xingyunSdk
let xingyunReadyTimer

function markXingyunReady() {
  if (xingyunReady.value || !xingyunSdk) return
  clearTimeout(xingyunReadyTimer)
  xingyunReady.value = true
  xingyunLoading.value = false
  xingyunError.value = ''
  xingyunSdk.changeAvatarVisible?.(true)
  xingyunSdk.setVolume?.(isMuted.value ? 0 : 1)
  const text = briefingScript.value || narratorLines.value.join('。')
  if (text) {
    isSpeaking.value = true
    xingyunSdk.speak?.(text, true, true)
  }
}

function failXingyun(message) {
  clearTimeout(xingyunReadyTimer)
  xingyunReady.value = false
  xingyunLoading.value = false
  xingyunError.value = message || '魔珐星云数字人初始化失败'
}

let renderer
let labelRenderer
let css3dRenderer
let scene
let camera
let mapRoot
let regionGroup
let edgeGroup
let flightGroup
let heatGroup
let markerGroup
let barGroup
let labelGroup
let cardGroup
let rainGroup
let clock
let animationId = 0
let resizeObserver
let heatTexture
const charts = []
const regionMeshes = []
const interactiveObjects = []
const flightParticles = []
const css3dCards = []
const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()

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

async function loadGeoJson() {
  try {
    const response = await fetch('/geo/training-map.geojson', { cache: 'no-store' })
    if (!response.ok) throw new Error(`geojson ${response.status}`)
    geoJson.value = await response.json()
  } catch {
    geoJson.value = fallbackGeoJson
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
    await nextTick()
    refreshCharts()
    rebuildVisualLayers()
    if (!silent) ElMessage.success('大屏数据已刷新')
  } finally {
    loading.value = false
  }
}

const selectedTimeLabel = computed(() => timeOptions.find((item) => item.value === timeRange.value)?.label || '本学期')

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

const completionRate = computed(() => {
  const denominator = Math.max(achievements.value.length, 1)
  return Math.round((evaluatedAchievements.value.length / denominator) * 100)
})

const enterpriseEvalCount = computed(() =>
  evalResults.value.filter((item) => Number(item.eval_type) === 3).length,
)

const aiReviewCount = computed(() => {
  const evalAiCount = evalResults.value.filter((item) => Number(item.eval_type) === 1).length
  return Math.max(evalAiCount, llmLogs.value.length)
})

const riskCount = computed(() =>
  achievements.value.filter((item) => Number(item.status) === 2 || (item.final_score != null && Number(item.final_score) < 80)).length,
)

const statCards = computed(() => [
  { label: '运行项目', value: projects.value.length, unit: '项', trend: `${submittedAchievements.value.length} 份成果入库`, icon: Connection, tone: 'cyan' },
  { label: '综合均分', value: avgScore.value || '--', unit: avgScore.value ? '分' : '', trend: `评价完成率 ${completionRate.value}%`, icon: TrendCharts, tone: 'green' },
  { label: '企业评价', value: enterpriseEvalCount.value, unit: '条', trend: '导师证据链同步', icon: DataAnalysis, tone: 'gold' },
  { label: 'AI 核查', value: aiReviewCount.value, unit: '次', trend: '模型失败不阻断人工评分', icon: MagicStick, tone: 'violet' },
])

const focusCopy = computed(() => {
  const map = {
    overview: '项目、成果、评价、AI 核查和报表形成可演示闭环，现场优先展示稳定业务流。',
    score: '评分态突出教师评价、企业评价与 AI 建议的分层证据，不直接覆盖人工最终分。',
    risk: '风险态聚焦退回重做、低分成果、待评价成果和模型异常日志。',
    enterprise: '企业态只展示分配项目和验收证据，强调校企协同与人才能力画像。',
  }
  return map[focusMode.value]
})

const regionStats = computed(() => {
  const features = geoJson.value?.features || []
  return features.map((feature, index) => {
    const project = projects.value[index % Math.max(projects.value.length, 1)] || demoProjects[index % demoProjects.length]
    const related = achievements.value.filter((item) => item.project_id === project?.id)
    const scoreValues = related.map((item) => Number(item.final_score)).filter((score) => Number.isFinite(score))
    const baseScore = scoreValues.length
      ? Math.round(scoreValues.reduce((sum, value) => sum + value, 0) / scoreValues.length)
      : Number(feature.properties?.value || 76 + index * 4)
    return {
      id: `${feature.properties?.name || 'region'}-${index}`,
      name: feature.properties?.name || `区域 ${index + 1}`,
      center: feature.properties?.center,
      value: clamp(baseScore, 48, 99),
      projectName: project?.project_name || `实训项目 ${index + 1}`,
      count: related.length || 1 + index,
      risk: index === 2 ? riskCount.value : Math.max(0, Math.round((95 - baseScore) / 9)),
      color: scoreColor(baseScore),
      feature,
    }
  })
})

const topRegions = computed(() => [...regionStats.value].sort((a, b) => b.value - a.value).slice(0, 4))

const selectedRegion = computed(() =>
  regionStats.value.find((item) => item.id === selectedRegionId.value) || regionStats.value[0],
)

const abilityRows = computed(() => [
  { name: '工程实现', value: clamp(avgScore.value + 4, 0, 100), color: '#30e0c0' },
  { name: '文档规范', value: clamp(avgScore.value - 2, 0, 100), color: '#43a4ff' },
  { name: 'AI 核查响应', value: clamp(70 + aiReviewCount.value * 5, 0, 100), color: '#9d7cff' },
  { name: '企业协同', value: clamp(72 + enterpriseEvalCount.value * 6, 0, 100), color: '#ffbf54' },
])

const evidenceRows = computed(() =>
  achievements.value.slice(0, 5).map((item) => ({
    id: item.id,
    title: item.title || item.achievement_name || '未命名成果',
    score: item.final_score ?? '待评',
    status: statusLabel(item.status),
  })),
)

const narratorLines = computed(() => [
  briefingScript.value || `当前锁定：${selectedRegion.value?.name || '实训地图'}，关联 ${selectedRegion.value?.count || 0} 条成果证据。`,
  `项目总量 ${projects.value.length} 项，成果提交 ${submittedAchievements.value.length} 份，综合均分 ${avgScore.value || '--'}。`,
  focusCopy.value,
])

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, Number(value) || 0))
}

function scoreColor(score) {
  if (score >= 92) return 0x25f0d0
  if (score >= 84) return 0x3aa8ff
  if (score >= 76) return 0xffbf54
  return 0xff6878
}

function statusLabel(status) {
  const map = { 0: '草稿', 1: '已提交', 2: '退回', 3: '已评价' }
  return map[Number(status)] || '进行中'
}

function collectCoordinatePairs(value, output = []) {
  if (!Array.isArray(value)) return output
  if (value.length >= 2 && Number.isFinite(value[0]) && Number.isFinite(value[1])) {
    output.push(value)
    return output
  }
  value.forEach((child) => collectCoordinatePairs(child, output))
  return output
}

function getAllCoordinates(geo) {
  const points = []
  ;(geo?.features || []).forEach((feature) => {
    collectCoordinatePairs(feature.geometry?.coordinates, points)
  })
  return points
}

function createProjector(geo) {
  const points = getAllCoordinates(geo)
  if (!points.length) return () => new THREE.Vector3(0, 0, 0)
  const xs = points.map((point) => point[0])
  const ys = points.map((point) => point[1])
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const minY = Math.min(...ys)
  const maxY = Math.max(...ys)
  const width = maxX - minX || 1
  const height = maxY - minY || 1
  const scale = Math.min(7.3 / width, 4.35 / height)
  return ([x, y]) => new THREE.Vector3(
    (x - (minX + width / 2)) * scale,
    0,
    -((y - (minY + height / 2)) * scale),
  )
}

function featureCenter(feature, project) {
  const projectPoint = createProjector(geoJson.value)
  if (project.center) return projectPoint(project.center)
  const coordinates = feature.geometry?.coordinates?.[0] || []
  const sum = coordinates.reduce((acc, point) => [acc[0] + point[0], acc[1] + point[1]], [0, 0])
  const count = Math.max(coordinates.length, 1)
  return projectPoint([sum[0] / count, sum[1] / count])
}

function createMapMaterial(color, opacity = 0.9) {
  return new THREE.ShaderMaterial({
    transparent: true,
    uniforms: {
      uColor: { value: new THREE.Color(color) },
      uAccent: { value: new THREE.Color(0x6cf5ff) },
      uOpacity: { value: opacity },
    },
    vertexShader: `
      varying vec2 vUv;
      varying vec3 vPos;
      void main() {
        vUv = uv;
        vPos = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 uColor;
      uniform vec3 uAccent;
      uniform float uOpacity;
      varying vec2 vUv;
      varying vec3 vPos;
      void main() {
        float edge = smoothstep(0.08, 0.78, abs(vPos.y));
        vec3 color = mix(uColor * 0.56, uAccent, edge * 0.42);
        gl_FragColor = vec4(color, uOpacity);
      }
    `,
  })
}

function createBarMaterial(colorTop) {
  return new THREE.ShaderMaterial({
    transparent: true,
    uniforms: {
      uTime: { value: 0 },
      uColorTop: { value: new THREE.Color(colorTop) },
      uColorBottom: { value: new THREE.Color(0x0a2a5d) },
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uTime;
      uniform vec3 uColorTop;
      uniform vec3 uColorBottom;
      varying vec2 vUv;
      void main() {
        float scan = 0.35 + 0.65 * sin((vUv.y * 8.0) - uTime * 3.5);
        vec3 color = mix(uColorBottom, uColorTop, vUv.y);
        gl_FragColor = vec4(color + scan * 0.12, 0.72);
      }
    `,
  })
}

function createHeatTexture() {
  const canvas = document.createElement('canvas')
  canvas.width = 128
  canvas.height = 128
  const context = canvas.getContext('2d')
  const gradient = context.createRadialGradient(64, 64, 5, 64, 64, 64)
  gradient.addColorStop(0, 'rgba(255, 223, 111, 0.92)')
  gradient.addColorStop(0.38, 'rgba(31, 224, 196, 0.46)')
  gradient.addColorStop(0.72, 'rgba(51, 142, 255, 0.22)')
  gradient.addColorStop(1, 'rgba(51, 142, 255, 0)')
  context.fillStyle = gradient
  context.fillRect(0, 0, 128, 128)
  const texture = new THREE.CanvasTexture(canvas)
  texture.colorSpace = THREE.SRGBColorSpace
  return texture
}

function disposeObject(object) {
  if (!object) return
  object.traverse?.((child) => {
    child.geometry?.dispose?.()
    if (Array.isArray(child.material)) child.material.forEach((material) => material.dispose?.())
    else child.material?.dispose?.()
  })
}

function clearGroup(group) {
  if (!group) return
  group.children.forEach((child) => disposeObject(child))
  group.clear()
}

function initScene() {
  if (!canvasRef.value || !stageRef.value) return
  scene = new THREE.Scene()
  scene.fog = new THREE.FogExp2(0x031124, 0.062)
  camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100)
  camera.position.set(0, 6.6, 8.4)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: true,
    alpha: true,
    preserveDrawingBuffer: true,
  })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
  renderer.outputColorSpace = THREE.SRGBColorSpace

  labelRenderer = new CSS2DRenderer()
  labelRenderer.domElement.className = 'css2d-layer'
  labelRenderer.domElement.style.position = 'absolute'
  labelRenderer.domElement.style.inset = '0'
  labelRenderer.domElement.style.pointerEvents = 'none'
  stageRef.value.appendChild(labelRenderer.domElement)

  css3dRenderer = new CSS3DRenderer()
  css3dRenderer.domElement.className = 'css3d-layer'
  css3dRenderer.domElement.style.position = 'absolute'
  css3dRenderer.domElement.style.inset = '0'
  css3dRenderer.domElement.style.pointerEvents = 'none'
  stageRef.value.appendChild(css3dRenderer.domElement)

  clock = new THREE.Clock()
  mapRoot = new THREE.Group()
  regionGroup = new THREE.Group()
  edgeGroup = new THREE.Group()
  flightGroup = new THREE.Group()
  heatGroup = new THREE.Group()
  markerGroup = new THREE.Group()
  barGroup = new THREE.Group()
  labelGroup = new THREE.Group()
  cardGroup = new THREE.Group()
  rainGroup = new THREE.Group()
  mapRoot.add(regionGroup, edgeGroup, heatGroup, flightGroup, markerGroup, barGroup, labelGroup, cardGroup)
  scene.add(mapRoot, rainGroup)

  const ambient = new THREE.AmbientLight(0x9fe8ff, 1.35)
  const key = new THREE.DirectionalLight(0xffffff, 1.7)
  key.position.set(3.5, 7, 4)
  const rim = new THREE.PointLight(0x1ee4ff, 42, 18)
  rim.position.set(-4, 2, -2)
  const gold = new THREE.PointLight(0xffb94c, 22, 12)
  gold.position.set(3, 1.8, 2.8)
  scene.add(ambient, key, rim, gold)

  const grid = new THREE.GridHelper(9, 36, 0x1688ff, 0x12345d)
  grid.position.y = -0.22
  grid.material.transparent = true
  grid.material.opacity = 0.2
  scene.add(grid)

  createDigitalRain()
  heatTexture = createHeatTexture()
  rebuildMap()
  resizeScene()
  resizeObserver = new ResizeObserver(() => {
    resizeScene()
    resizeCharts()
  })
  resizeObserver.observe(stageRef.value)
  animateScene()
}

function createDigitalRain() {
  clearGroup(rainGroup)
  const lineMaterial = new THREE.LineBasicMaterial({ color: 0x6ce8ff, transparent: true, opacity: 0.22 })
  for (let i = 0; i < 42; i += 1) {
    const x = -4.8 + (i % 14) * 0.74
    const z = -2.9 + Math.floor(i / 14) * 2.1
    const y = 1.2 + (i % 5) * 0.42
    const geometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(x, y, z),
      new THREE.Vector3(x + 0.03, y - 1.1 - (i % 3) * 0.24, z + 0.02),
    ])
    const line = new THREE.Line(geometry, lineMaterial.clone())
    line.userData.speed = 0.2 + (i % 5) * 0.04
    rainGroup.add(line)
  }
}

function rebuildMap() {
  if (!scene || !geoJson.value) return
  clearGroup(regionGroup)
  clearGroup(edgeGroup)
  clearGroup(labelGroup)
  regionMeshes.length = 0
  interactiveObjects.length = 0

  const projector = createProjector(geoJson.value)
  regionStats.value.forEach((region, index) => {
    const polygon = region.feature.geometry?.coordinates?.[0] || []
    if (!polygon.length) return
    const shape = new THREE.Shape()
    polygon.forEach((point, pointIndex) => {
      const projected = projector(point)
      if (pointIndex === 0) shape.moveTo(projected.x, -projected.z)
      else shape.lineTo(projected.x, -projected.z)
    })
    const geometry = new THREE.ExtrudeGeometry(shape, {
      depth: 0.2 + region.value / 520,
      bevelEnabled: true,
      bevelThickness: 0.025,
      bevelSize: 0.018,
      bevelSegments: 1,
    })
    geometry.rotateX(-Math.PI / 2)
    geometry.center()
    const material = createMapMaterial(region.color, 0.88)
    const mesh = new THREE.Mesh(geometry, material)
    const center = featureCenter(region.feature, region)
    mesh.position.copy(center)
    mesh.position.y = 0.03 + index * 0.003
    mesh.userData = { type: 'region', id: region.id, region }
    regionGroup.add(mesh)
    regionMeshes.push(mesh)
    interactiveObjects.push(mesh)

    const edge = new THREE.LineSegments(
      new THREE.EdgesGeometry(geometry, 18),
      new THREE.LineBasicMaterial({ color: 0x84f4ff, transparent: true, opacity: 0.56 }),
    )
    edge.position.copy(mesh.position)
    edge.userData.regionId = region.id
    edgeGroup.add(edge)

    const halo = new THREE.LineSegments(
      new THREE.EdgesGeometry(geometry, 18),
      new THREE.LineBasicMaterial({ color: 0xffc75a, transparent: true, opacity: 0.2 }),
    )
    halo.position.copy(mesh.position)
    halo.position.y -= 0.18
    edgeGroup.add(halo)

    const label = document.createElement('div')
    label.className = 'map-label'
    label.innerHTML = `<strong>${region.name}</strong><span>${region.value} 分 / ${region.count} 份</span>`
    const labelObject = new CSS2DObject(label)
    labelObject.position.copy(center)
    labelObject.position.y = 0.55
    labelObject.userData.layer = 'label'
    labelGroup.add(labelObject)
  })

  mapRoot.rotation.x = -0.18
  mapRoot.rotation.z = -0.04
  mapRoot.scale.setScalar(1.02)
  selectedRegionId.value = regionStats.value[0]?.id || ''
  rebuildVisualLayers()
}

function rebuildVisualLayers() {
  if (!mapRoot || !geoJson.value) return
  clearGroup(flightGroup)
  clearGroup(heatGroup)
  clearGroup(markerGroup)
  clearGroup(barGroup)
  clearGroup(cardGroup)
  flightParticles.length = 0
  css3dCards.length = 0
  interactiveObjects.splice(regionMeshes.length)

  const regions = regionStats.value
  if (!regions.length) return
  const core = featureCenter(regions[0].feature, regions[0])
  core.y = 0.44

  regions.forEach((region, index) => {
    const center = featureCenter(region.feature, region)
    const scoreRatio = region.value / 100

    const heat = new THREE.Mesh(
      new THREE.PlaneGeometry(0.86 + scoreRatio * 0.7, 0.86 + scoreRatio * 0.7),
      new THREE.MeshBasicMaterial({
        map: heatTexture,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        opacity: 0.55,
      }),
    )
    heat.rotation.x = -Math.PI / 2
    heat.position.set(center.x, 0.055, center.z)
    heat.userData.layer = 'heat'
    heatGroup.add(heat)

    const barHeight = 0.45 + scoreRatio * 1.45
    const bar = new THREE.Mesh(
      new THREE.CylinderGeometry(0.055, 0.08, barHeight, 8, 1, true),
      createBarMaterial(region.color),
    )
    bar.position.set(center.x, barHeight / 2 + 0.22, center.z)
    bar.userData = { type: 'bar', id: region.id, region }
    barGroup.add(bar)
    interactiveObjects.push(bar)

    const cap = new THREE.Mesh(
      new THREE.ConeGeometry(0.18, 0.46, 4),
      new THREE.MeshStandardMaterial({
        color: region.color,
        emissive: region.color,
        emissiveIntensity: 0.72,
        roughness: 0.2,
        metalness: 0.2,
        transparent: true,
        opacity: 0.92,
      }),
    )
    cap.position.set(center.x, barHeight + 0.64, center.z)
    cap.rotation.y = Math.PI / 4
    cap.userData = { type: 'marker', id: region.id, region }
    markerGroup.add(cap)
    interactiveObjects.push(cap)
    gsap.to(cap.scale, {
      x: 1.22,
      y: 1.22,
      z: 1.22,
      duration: 1.2 + index * 0.08,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
    })
    gsap.to(cap.rotation, {
      y: Math.PI * 2 + Math.PI / 4,
      duration: 5 + index * 0.35,
      repeat: -1,
      ease: 'none',
    })

    const scatter = new THREE.Mesh(
      new THREE.SphereGeometry(0.055 + scoreRatio * 0.04, 18, 12),
      new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.88 }),
    )
    scatter.position.set(center.x + 0.18, 0.42 + scoreRatio * 0.32, center.z - 0.16)
    scatter.userData = { type: 'scatter', id: region.id, region }
    markerGroup.add(scatter)
    interactiveObjects.push(scatter)

    if (index > 0) {
      createFlightLine(core, new THREE.Vector3(center.x, 0.6 + index * 0.04, center.z), region, index)
    }

    if (index < 3) createCss3dCard(center, region, index)
  })
  applyLayerVisibility()
}

function createFlightLine(from, to, region, index) {
  const mid = from.clone().lerp(to, 0.5)
  mid.y += 1.2 + index * 0.1
  const curve = new THREE.CatmullRomCurve3([from.clone(), mid, to.clone()])
  const points = curve.getPoints(64)
  const geometry = new THREE.BufferGeometry().setFromPoints(points)
  const line = new THREE.Line(
    geometry,
    new THREE.LineBasicMaterial({
      color: region.color,
      transparent: true,
      opacity: 0.5,
      blending: THREE.AdditiveBlending,
    }),
  )
  line.userData.layer = 'flight'
  flightGroup.add(line)

  const particle = new THREE.Mesh(
    new THREE.SphereGeometry(0.045, 16, 8),
    new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.95 }),
  )
  particle.userData.layer = 'flight'
  flightGroup.add(particle)
  flightParticles.push({ mesh: particle, curve, offset: index * 0.18, speed: 0.16 + index * 0.018 })
}

function createCss3dCard(center, region, index) {
  const element = document.createElement('div')
  element.className = 'css3d-card'
  element.innerHTML = `
    <span>${region.projectName}</span>
    <strong>${region.value}</strong>
    <em>${region.name} / ${region.count} 份证据</em>
  `
  const object = new CSS3DObject(element)
  object.position.set(center.x + 0.45, 1.25 + index * 0.2, center.z - 0.35)
  object.scale.setScalar(0.0065)
  object.userData.layer = 'label'
  cardGroup.add(object)
  css3dCards.push(object)
}

function applyLayerVisibility() {
  if (!mapRoot) return
  flightGroup.visible = layers.value.flight
  labelGroup.visible = layers.value.label
  cardGroup.visible = layers.value.label
  markerGroup.visible = layers.value.marker
  heatGroup.visible = layers.value.heat
  barGroup.visible = layers.value.bar
}

function resizeScene() {
  if (!renderer || !camera || !stageRef.value) return
  const rect = stageRef.value.getBoundingClientRect()
  const width = Math.max(rect.width, 320)
  const height = Math.max(rect.height, 320)
  renderer.setSize(width, height, false)
  labelRenderer?.setSize(width, height)
  css3dRenderer?.setSize(width, height)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
}

function animateScene() {
  animationId = window.requestAnimationFrame(animateScene)
  const elapsed = clock?.getElapsedTime?.() || 0
  if (mapRoot) {
    mapRoot.rotation.y = Math.sin(elapsed * 0.18) * 0.09
    mapRoot.position.y = Math.sin(elapsed * 0.5) * 0.035
  }
  regionMeshes.forEach((mesh) => {
    const isActive = mesh.userData.id === selectedRegionId.value
    const isHovered = hoveredInfo.value?.id === mesh.userData.id
    mesh.material.uniforms.uOpacity.value = isActive || isHovered ? 0.98 : 0.78
    mesh.scale.setScalar(isActive ? 1.02 : 1)
  })
  flightParticles.forEach((item) => {
    const t = (elapsed * item.speed + item.offset) % 1
    item.mesh.position.copy(item.curve.getPointAt(t))
  })
  barGroup?.children.forEach((bar, index) => {
    if (bar.material?.uniforms?.uTime) bar.material.uniforms.uTime.value = elapsed + index * 0.4
  })
  heatGroup?.children.forEach((heat, index) => {
    const pulse = 1 + Math.sin(elapsed * 1.5 + index) * 0.06
    heat.scale.setScalar(pulse)
  })
  rainGroup?.children.forEach((line, index) => {
    line.position.y -= line.userData.speed * 0.018
    if (line.position.y < -1.5) line.position.y = 2.8 + index * 0.01
  })
  css3dCards.forEach((card) => card.quaternion.copy(camera.quaternion))
  renderer?.render(scene, camera)
  labelRenderer?.render(scene, camera)
  css3dRenderer?.render(scene, camera)
}

function resolveIntersection(event) {
  if (!renderer || !camera || !canvasRef.value) return null
  const rect = canvasRef.value.getBoundingClientRect()
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  raycaster.setFromCamera(pointer, camera)
  return raycaster.intersectObjects(interactiveObjects, false)[0]?.object || null
}

function handleSceneMove(event) {
  const target = resolveIntersection(event)
  if (!target?.userData?.region) {
    hoveredInfo.value = null
    if (canvasRef.value) canvasRef.value.style.cursor = 'default'
    return
  }
  const rect = stageRef.value.getBoundingClientRect()
  const region = target.userData.region
  hoveredInfo.value = {
    id: target.userData.id,
    name: region.name,
    value: region.value,
    projectName: region.projectName,
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  }
  if (canvasRef.value) canvasRef.value.style.cursor = 'pointer'
}

function handleSceneClick(event) {
  const target = resolveIntersection(event)
  if (target?.userData?.id) selectedRegionId.value = target.userData.id
}

function toggleLayer(key) {
  layers.value = { ...layers.value, [key]: !layers.value[key] }
  applyLayerVisibility()
}

function requestFullscreen() {
  const target = document.querySelector('.report-screen-page')
  target?.requestFullscreen?.()
}

function toggleSpeaking() {
  isSpeaking.value = !isSpeaking.value
  if (!xingyunSdk || !xingyunReady.value) return
  if (isSpeaking.value) {
    const text = briefingScript.value || narratorLines.value.join('。')
    xingyunSdk.speak?.(text, true, true)
  } else {
    xingyunSdk.stopSpeak?.()
    xingyunSdk.stop?.()
  }
}

function toggleMute() {
  isMuted.value = !isMuted.value
  xingyunSdk?.setVolume?.(isMuted.value ? 0 : 1)
}

function loadXingyunScript(src) {
  if (window.XmovAvatar) return Promise.resolve()
  const existed = document.querySelector(`script[src="${src}"]`)
  if (existed?.dataset.loaded === 'true') return Promise.resolve()
  if (existed) {
    return new Promise((resolve, reject) => {
      existed.addEventListener('load', resolve, { once: true })
      existed.addEventListener('error', reject, { once: true })
    })
  }
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = src
    script.async = true
    script.dataset.xingyunSdk = 'true'
    script.addEventListener('load', () => {
      script.dataset.loaded = 'true'
      resolve()
    }, { once: true })
    script.addEventListener('error', reject, { once: true })
    document.head.appendChild(script)
  })
}

async function initXingyunAvatar() {
  clearTimeout(xingyunReadyTimer)
  xingyunLoading.value = true
  xingyunReady.value = false
  xingyunProgress.value = 0
  xingyunError.value = ''
  try {
    const config = await getXingyunConfig()
    xingyunEnabled.value = Boolean(config.enabled)
    if (!config.enabled) {
      xingyunError.value = '未配置魔珐星云 App ID / Secret'
      return
    }
    await loadXingyunScript(config.sdk_url)
    if (!window.XmovAvatar) throw new Error('魔珐星云 SDK 加载后未暴露 XmovAvatar')
    await nextTick()
    if (!xingyunSdkRef.value) throw new Error('数字人容器未就绪')
    xingyunSdk = new window.XmovAvatar({
      containerId: '#xingyun-avatar-sdk',
      appId: config.app_id,
      appSecret: config.app_secret,
      gatewayServer: config.gateway_server || '',
      onMessage: (message) => {
        const code = Number(message?.code || 0)
        if ((message?.type === 'error' || (code && code !== 50002)) && !xingyunReady.value) {
          failXingyun(message?.message || `数字人连接异常（${code}）`)
        }
      },
      onVoiceStateChange: (status) => {
        if (status === 'start' || status === 'voice_start') isSpeaking.value = true
        if (status === 'end' || status === 'voice_end') isSpeaking.value = false
      },
      onStartSessionWarning: (message) => {
        if (!xingyunReady.value) failXingyun(message?.message || '数字人应用配置不可用')
      },
      hardwareAcceleration: 'prefer-hardware',
      enableLogger: import.meta.env.DEV,
    })
    const initResult = xingyunSdk.init?.({
      initModel: 'normal',
      onDownloadProgress: (progress) => {
        xingyunProgress.value = Math.round(Number(progress) || 0)
        if (xingyunProgress.value >= 100) markXingyunReady()
      },
    })
    if (initResult?.then) {
      await initResult
    }
    xingyunReadyTimer = window.setTimeout(() => {
      if (!xingyunReady.value) failXingyun('数字人资源加载超时，请检查应用配置或网络')
    }, 20_000)
  } catch (error) {
    xingyunEnabled.value = true
    failXingyun(error?.message)
  }
}

function refreshCharts() {
  if (!ringChartRef.value) return
  charts.forEach((chart) => chart.dispose())
  charts.length = 0
  const ringChart = echarts.init(ringChartRef.value)
  const barChart = echarts.init(barChartRef.value)
  const lineChart = echarts.init(lineChartRef.value)
  const mixChart = echarts.init(mixChartRef.value)
  charts.push(ringChart, barChart, lineChart, mixChart)

  ringChart.setOption({
    backgroundColor: 'transparent',
    color: ['#28f0d0', '#43a4ff', '#ffbf54', '#5f6fff'],
    series: [{
      type: 'pie',
      radius: ['54%', '78%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      label: { color: '#dff8ff', formatter: '{b}\n{d}%', fontSize: 11 },
      labelLine: { lineStyle: { color: '#4ccdfb' } },
      data: [
        { name: '已评价', value: evaluatedAchievements.value.length },
        { name: '已提交', value: submittedAchievements.value.length },
        { name: '退回', value: riskCount.value },
        { name: '待处理', value: Math.max(achievements.value.length - evaluatedAchievements.value.length, 0) },
      ],
    }],
  })

  barChart.setOption({
    grid: { left: 34, right: 12, top: 28, bottom: 24 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: topRegions.value.map((item) => item.name.replace('区', '')),
      axisLabel: { color: '#8fb6da', fontSize: 10 },
      axisLine: { lineStyle: { color: '#214b79' } },
    },
    yAxis: {
      type: 'value',
      max: 100,
      splitLine: { lineStyle: { color: 'rgba(76, 154, 255, .12)' } },
      axisLabel: { color: '#8fb6da', fontSize: 10 },
    },
    series: [{
      type: 'bar',
      data: topRegions.value.map((item) => item.value),
      barWidth: 14,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#2af7d5' },
          { offset: 0.6, color: '#248dff' },
          { offset: 1, color: '#123e85' },
        ]),
      },
    }],
  })

  lineChart.setOption({
    color: ['#26e8c8', '#4ba8ff'],
    tooltip: { trigger: 'axis' },
    legend: { top: 0, right: 4, textStyle: { color: '#bfe9ff', fontSize: 10 } },
    grid: { left: 35, right: 15, top: 34, bottom: 24 },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['03/24', '03/25', '03/26', '03/27', '03/28', '03/29', '03/30'],
      axisLabel: { color: '#8fb6da', fontSize: 10 },
      axisLine: { lineStyle: { color: '#214b79' } },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(76, 154, 255, .12)' } },
      axisLabel: { color: '#8fb6da', fontSize: 10 },
    },
    series: [
      {
        name: '成果提交',
        type: 'line',
        smooth: true,
        areaStyle: { color: 'rgba(38, 232, 200, .18)' },
        data: [12, 18, 14, 24, 28, 34, submittedAchievements.value.length + 31],
      },
      {
        name: 'AI 核查',
        type: 'line',
        smooth: true,
        areaStyle: { color: 'rgba(75, 168, 255, .14)' },
        data: [4, 8, 11, 16, 18, 22, aiReviewCount.value + 20],
      },
    ],
  })

  mixChart.setOption({
    color: ['#41d9ff', '#ffbf54', '#2df2c6'],
    tooltip: { trigger: 'axis' },
    legend: { top: 0, right: 4, textStyle: { color: '#bfe9ff', fontSize: 10 } },
    grid: { left: 34, right: 16, top: 34, bottom: 24 },
    xAxis: {
      type: 'category',
      data: ['一月', '二月', '三月', '四月', '五月', '六月'],
      axisLabel: { color: '#8fb6da', fontSize: 10 },
      axisLine: { lineStyle: { color: '#214b79' } },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(76, 154, 255, .12)' } },
      axisLabel: { color: '#8fb6da', fontSize: 10 },
    },
    series: [
      { name: '教师评分', type: 'bar', barWidth: 8, data: [58, 72, 92, 86, 104, avgScore.value + 20] },
      { name: '企业评分', type: 'bar', barWidth: 8, data: [42, 61, 88, 73, 95, enterpriseEvalCount.value * 18 + 48] },
      { name: '闭环指数', type: 'line', smooth: true, data: [40, 56, 71, 78, 89, completionRate.value] },
    ],
  })
}

function resizeCharts() {
  charts.forEach((chart) => chart.resize())
}

watch(layers, applyLayerVisibility, { deep: true })

watch([focusMode, timeRange], () => {
  refreshCharts()
})

watch(regionStats, () => {
  if (scene) {
    rebuildMap()
    refreshCharts()
  }
})

onMounted(async () => {
  briefingScript.value = localStorage.getItem('ste-briefing-script') || ''
  await Promise.all([loadGeoJson(), loadScreenData(true)])
  await nextTick()
  initScene()
  refreshCharts()
  initXingyunAvatar()
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  window.cancelAnimationFrame(animationId)
  window.removeEventListener('resize', resizeCharts)
  resizeObserver?.disconnect()
  charts.forEach((chart) => chart.dispose())
  clearGroup(regionGroup)
  clearGroup(edgeGroup)
  clearGroup(flightGroup)
  clearGroup(heatGroup)
  clearGroup(markerGroup)
  clearGroup(barGroup)
  clearGroup(labelGroup)
  clearGroup(cardGroup)
  clearGroup(rainGroup)
  heatTexture?.dispose?.()
  renderer?.dispose?.()
  labelRenderer?.domElement?.remove?.()
  css3dRenderer?.domElement?.remove?.()
  clearTimeout(xingyunReadyTimer)
  xingyunSdk?.destroy?.()
  xingyunSdk?.dispose?.()
  xingyunSdk?.uninit?.()
})
</script>

<template>
  <section class="report-screen-page">
    <div class="screen-background" aria-hidden="true"></div>

    <header class="screen-header">
      <div class="header-wing left-wing">
        <span>欢迎，{{ userStore.name }}</span>
        <strong>SmartTrainEval</strong>
      </div>
      <nav class="screen-tabs" aria-label="大屏场景">
        <button
          v-for="mode in focusModes"
          :key="mode.value"
          :class="{ active: focusMode === mode.value }"
          type="button"
          @click="focusMode = mode.value"
        >
          {{ mode.label }}
        </button>
      </nav>
      <div class="header-title">
        <p>软件实训智能评价系统</p>
        <h1>可视化实训报告大屏</h1>
      </div>
      <div class="screen-tabs right-tabs">
        <button
          v-for="option in timeOptions"
          :key="option.value"
          :class="{ active: timeRange === option.value }"
          type="button"
          @click="timeRange = option.value"
        >
          {{ option.label }}
        </button>
      </div>
      <div class="header-wing right-wing">
        <span>LIVE {{ selectedTimeLabel }}</span>
        <strong>2026-07-05</strong>
      </div>
    </header>

    <main class="screen-body">
      <aside class="screen-column left-column">
        <article class="hud-panel ring-panel">
          <div class="panel-title">
            <span>01</span>
            <strong>评价闭环占比</strong>
          </div>
          <div ref="ringChartRef" class="chart-box"></div>
        </article>

        <article class="hud-panel">
          <div class="panel-title">
            <span>02</span>
            <strong>区域评分柱状图</strong>
          </div>
          <div ref="barChartRef" class="chart-box slim-chart"></div>
        </article>

        <article class="hud-panel evidence-panel">
          <div class="panel-title">
            <span>03</span>
            <strong>最新成果证据</strong>
          </div>
          <ul class="evidence-list">
            <li v-for="item in evidenceRows" :key="item.id">
              <span>{{ item.title }}</span>
              <em>{{ item.status }}</em>
              <b>{{ item.score }}</b>
            </li>
          </ul>
        </article>
      </aside>

      <section class="center-stage">
        <div class="stage-shell">
          <div class="map-toolbar">
            <button
              v-for="layer in layerToggles"
              :key="layer.key"
              :class="{ active: layers[layer.key] }"
              type="button"
              @click="toggleLayer(layer.key)"
            >
              <component :is="layer.icon" />
              <span>{{ layer.label }}</span>
            </button>
          </div>

          <div
            ref="stageRef"
            class="three-stage"
            aria-label="geoJson 三维实训地图"
            @pointermove="handleSceneMove"
            @pointerleave="hoveredInfo = null"
            @click="handleSceneClick"
          >
            <canvas ref="canvasRef" class="webgl-canvas"></canvas>
            <div class="stage-reticle" aria-hidden="true"></div>
            <div class="china-badge">实训地图 / geoJson</div>

            <div
              v-if="hoveredInfo"
              class="hover-card"
              :style="{ left: `${hoveredInfo.x + 18}px`, top: `${hoveredInfo.y + 18}px` }"
            >
              <strong>{{ hoveredInfo.name }}</strong>
              <span>{{ hoveredInfo.projectName }}</span>
              <em>{{ hoveredInfo.value }} 分</em>
            </div>
          </div>

          <section class="digital-human">
            <div class="human-orbit" aria-hidden="true"></div>
            <div v-if="xingyunEnabled && !xingyunError" class="xingyun-embed" :class="{ ready: xingyunReady }">
              <div id="xingyun-avatar-sdk" ref="xingyunSdkRef" class="xingyun-sdk-container"></div>
              <div v-if="xingyunLoading" class="xingyun-status">
                <strong>魔珐星云加载中</strong>
                <span>资源下载 {{ xingyunProgress }}%</span>
              </div>
            </div>
            <div v-else class="human-fallback">
              <img src="/illus/educator.svg" alt="魔珐星云数字人演示形象" />
              <div class="voice-wave" :class="{ active: isSpeaking && !isMuted }">
                <i></i><i></i><i></i><i></i><i></i>
              </div>
              <div v-if="xingyunError" class="xingyun-status">
                <strong>数字人连接异常</strong>
                <span>{{ xingyunError }}</span>
              </div>
            </div>
            <div class="human-copy">
              <span>MOFA XINGYUN</span>
              <strong>{{ xingyunError ? '备用讲解员' : (xingyunReady ? '数字人已接入' : '数字人播报') }}</strong>
              <p>{{ narratorLines[0] }}</p>
            </div>
            <div class="human-actions">
              <button type="button" @click="toggleSpeaking">
                <VideoPlay />
                {{ isSpeaking ? '暂停' : '播报' }}
              </button>
              <button type="button" @click="toggleMute">
                <MuteNotification />
                {{ isMuted ? '开声' : '静音' }}
              </button>
            </div>
          </section>
        </div>

        <section class="bottom-metrics">
          <article v-for="card in statCards" :key="card.label" :class="['metric-tile', `tone-${card.tone}`]">
            <component :is="card.icon" />
            <div>
              <span>{{ card.label }}</span>
              <strong>{{ card.value }}<em>{{ card.unit }}</em></strong>
              <p>{{ card.trend }}</p>
            </div>
          </article>
        </section>
      </section>

      <aside class="screen-column right-column">
        <article class="hud-panel gauge-panel">
          <div class="panel-title">
            <span>04</span>
            <strong>关键指标</strong>
          </div>
          <div class="gauge-row">
            <div v-for="card in statCards.slice(1)" :key="card.label" class="mini-gauge">
              <strong>{{ card.value }}</strong>
              <span>{{ card.label }}</span>
              <em>{{ card.unit }}</em>
            </div>
          </div>
        </article>

        <article class="hud-panel">
          <div class="panel-title">
            <span>05</span>
            <strong>提交与 AI 核查趋势</strong>
          </div>
          <div ref="lineChartRef" class="chart-box slim-chart"></div>
        </article>

        <article class="hud-panel">
          <div class="panel-title">
            <span>06</span>
            <strong>评分综合态势</strong>
          </div>
          <div ref="mixChartRef" class="chart-box slim-chart"></div>
        </article>

        <article class="hud-panel ability-panel">
          <div class="panel-title">
            <span>07</span>
            <strong>能力画像</strong>
          </div>
          <div class="ability-list">
            <div v-for="item in abilityRows" :key="item.name" class="ability-line">
              <span>{{ item.name }}</span>
              <div><i :style="{ width: `${item.value}%`, background: item.color }"></i></div>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </article>
      </aside>
    </main>

    <footer class="screen-footer">
      <div class="footer-status">
        <span class="live-dot"></span>
        <strong>{{ focusCopy }}</strong>
      </div>
      <div class="footer-actions">
        <button type="button" @click="loadScreenData">
          <Refresh />
          {{ loading ? '刷新中' : '刷新数据' }}
        </button>
        <button type="button" @click="requestFullscreen">
          <FullScreen />
          全屏
        </button>
      </div>
    </footer>
  </section>
</template>

<style scoped>
:global(.app-shell:has(.report-screen-page) .sidebar),
:global(.app-shell:has(.report-screen-page) .app-header) {
  display: none;
}

:global(.app-shell:has(.report-screen-page) .content-stage) {
  min-height: 100vh;
  padding: 0;
  background: #020916;
}

:global(.app-shell:has(.report-screen-page) .app-main) {
  width: 100vw;
}

.report-screen-page {
  position: relative;
  isolation: isolate;
  min-height: 100vh;
  overflow: hidden;
  color: #e9f8ff;
  background:
    radial-gradient(circle at 50% 34%, rgba(22, 128, 255, .24), transparent 34%),
    radial-gradient(circle at 24% 76%, rgba(27, 236, 199, .12), transparent 28%),
    linear-gradient(180deg, #051224 0%, #020916 58%, #031022 100%);
  font-family: "DIN Alternate", "Microsoft YaHei", "PingFang SC", system-ui, sans-serif;
}

.screen-background {
  position: absolute;
  inset: 0;
  z-index: -1;
  background-image:
    linear-gradient(rgba(54, 165, 255, .05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(54, 165, 255, .05) 1px, transparent 1px),
    radial-gradient(circle at 50% 50%, transparent 0 37%, rgba(29, 142, 255, .15) 38%, transparent 39%);
  background-size: 64px 64px, 64px 64px, 100% 100%;
  mask-image: linear-gradient(to bottom, #000 0%, #000 82%, transparent 100%);
}

.screen-header {
  position: relative;
  z-index: 5;
  display: grid;
  grid-template-columns: 220px 300px minmax(300px, 1fr) 300px 220px;
  align-items: start;
  height: 84px;
  padding: 8px 14px 0;
  gap: 10px;
}

.screen-header::before,
.screen-header::after {
  content: "";
  position: absolute;
  left: 320px;
  right: 320px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(80, 198, 255, .72), transparent);
}

.screen-header::before { top: 7px; }
.screen-header::after { bottom: 9px; }

.header-title {
  position: relative;
  min-height: 72px;
  padding: 12px 28px 10px;
  text-align: center;
  background: linear-gradient(180deg, rgba(22, 98, 176, .54), rgba(7, 29, 55, .18));
  clip-path: polygon(8% 0, 92% 0, 100% 36%, 87% 100%, 13% 100%, 0 36%);
  border-top: 1px solid rgba(111, 218, 255, .75);
}

.header-title p {
  margin: 0 0 2px;
  color: #79dfff;
  font-size: 12px;
  font-weight: 700;
}

.header-title h1 {
  margin: 0;
  color: #fff;
  font-size: clamp(20px, 1.55vw, 29px);
  font-weight: 900;
  letter-spacing: .04em;
  white-space: nowrap;
  text-shadow: 0 0 20px rgba(63, 190, 255, .85);
}

.header-wing,
.screen-tabs {
  min-height: 48px;
  border: 1px solid rgba(66, 176, 255, .36);
  background: linear-gradient(180deg, rgba(12, 50, 91, .72), rgba(4, 20, 39, .42));
  box-shadow: inset 0 0 18px rgba(21, 130, 255, .18);
}

.header-wing {
  display: grid;
  align-content: center;
  gap: 3px;
  padding: 8px 14px;
  clip-path: polygon(0 0, 92% 0, 100% 50%, 92% 100%, 0 100%);
}

.right-wing {
  clip-path: polygon(8% 0, 100% 0, 100% 100%, 8% 100%, 0 50%);
  text-align: right;
}

.header-wing span {
  color: rgba(214, 239, 255, .72);
  font-size: 12px;
}

.header-wing strong {
  color: #fff;
  font-size: 17px;
}

.screen-tabs {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  padding: 5px;
  gap: 6px;
  clip-path: polygon(5% 0, 95% 0, 100% 50%, 95% 100%, 5% 100%, 0 50%);
}

.right-tabs {
  grid-template-columns: repeat(3, 1fr);
}

.screen-tabs button,
.map-toolbar button,
.footer-actions button,
.human-actions button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  color: #b9daf2;
  background: linear-gradient(180deg, rgba(26, 96, 162, .7), rgba(7, 26, 50, .75));
  border: 1px solid rgba(92, 194, 255, .28);
  cursor: pointer;
}

.screen-tabs button {
  min-height: 34px;
  padding: 0 10px;
  font-size: 14px;
  font-weight: 700;
  clip-path: polygon(9% 0, 100% 0, 91% 100%, 0 100%);
}

.screen-tabs button.active,
.screen-tabs button:hover,
.map-toolbar button.active,
.map-toolbar button:hover,
.footer-actions button:hover,
.human-actions button:hover {
  color: #fff;
  border-color: rgba(103, 229, 255, .88);
  background: linear-gradient(180deg, rgba(25, 166, 255, .86), rgba(8, 68, 128, .86));
  box-shadow: 0 0 18px rgba(35, 184, 255, .38), inset 0 0 16px rgba(104, 235, 255, .18);
}

.screen-body {
  display: grid;
  grid-template-columns: minmax(280px, 22vw) minmax(620px, 1fr) minmax(280px, 22vw);
  gap: 14px;
  height: calc(100vh - 132px);
  min-height: 690px;
  padding: 0 14px 0;
}

.screen-column,
.center-stage {
  min-width: 0;
}

.screen-column {
  display: grid;
  gap: 12px;
}

.hud-panel {
  position: relative;
  min-height: 0;
  padding: 10px 12px;
  overflow: hidden;
  border: 1px solid rgba(57, 164, 255, .34);
  background:
    linear-gradient(135deg, rgba(19, 85, 152, .44), transparent 28%),
    linear-gradient(180deg, rgba(5, 22, 43, .9), rgba(3, 14, 28, .76));
  box-shadow:
    inset 0 0 20px rgba(28, 136, 255, .16),
    0 0 26px rgba(5, 30, 70, .32);
}

.hud-panel::before,
.hud-panel::after,
.stage-shell::before,
.stage-shell::after {
  content: "";
  position: absolute;
  width: 28px;
  height: 12px;
  border-color: rgba(91, 215, 255, .78);
  pointer-events: none;
}

.hud-panel::before,
.stage-shell::before {
  top: -1px;
  left: -1px;
  border-top: 2px solid;
  border-left: 2px solid;
}

.hud-panel::after,
.stage-shell::after {
  right: -1px;
  bottom: -1px;
  border-right: 2px solid;
  border-bottom: 2px solid;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 9px;
  height: 24px;
  margin-bottom: 6px;
  color: #fff;
}

.panel-title span {
  display: grid;
  place-items: center;
  width: 30px;
  height: 20px;
  color: #65e9ff;
  font-size: 11px;
  font-weight: 800;
  background: rgba(31, 137, 255, .18);
  border: 1px solid rgba(66, 197, 255, .36);
}

.panel-title strong {
  font-size: 15px;
  letter-spacing: .03em;
}

.ring-panel {
  min-height: 230px;
}

.chart-box {
  width: 100%;
  height: 196px;
}

.slim-chart {
  height: 150px;
}

.evidence-panel {
  min-height: 210px;
}

.evidence-list {
  display: grid;
  gap: 8px;
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
}

.evidence-list li {
  display: grid;
  grid-template-columns: 1fr 58px 42px;
  gap: 8px;
  align-items: center;
  min-height: 35px;
  padding: 8px 10px;
  color: rgba(222, 244, 255, .84);
  background: linear-gradient(90deg, rgba(46, 146, 255, .14), rgba(18, 52, 92, .08));
  border: 1px solid rgba(80, 176, 255, .13);
}

.evidence-list span {
  min-width: 0;
  overflow: hidden;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.evidence-list em {
  color: #8ecfff;
  font-size: 11px;
  font-style: normal;
}

.evidence-list b {
  color: #35efd0;
  font-size: 16px;
  text-align: right;
}

.center-stage {
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto;
  gap: 12px;
}

.stage-shell {
  position: relative;
  min-height: 0;
  overflow: hidden;
  border: 1px solid rgba(56, 167, 255, .28);
  background:
    radial-gradient(circle at 50% 54%, rgba(34, 121, 255, .18), transparent 36%),
    linear-gradient(180deg, rgba(3, 14, 30, .24), rgba(1, 8, 20, .76));
}

.stage-shell::before,
.stage-shell::after {
  width: 46px;
  height: 22px;
}

.map-toolbar {
  position: absolute;
  z-index: 6;
  top: 78px;
  left: 18px;
  display: grid;
  gap: 10px;
  width: 108px;
}

.map-toolbar button {
  justify-content: flex-start;
  gap: 7px;
  height: 36px;
  padding: 0 10px;
  font-size: 12px;
  clip-path: polygon(0 0, 88% 0, 100% 50%, 88% 100%, 0 100%);
}

.map-toolbar svg,
.footer-actions svg,
.human-actions svg {
  width: 15px;
  height: 15px;
}

.three-stage {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.webgl-canvas {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
}

.stage-reticle {
  position: absolute;
  inset: 8% 6%;
  pointer-events: none;
  border-left: 2px solid rgba(36, 156, 255, .32);
  border-right: 2px solid rgba(36, 156, 255, .32);
  border-radius: 50%;
  box-shadow:
    inset 0 0 36px rgba(36, 156, 255, .08),
    0 0 40px rgba(36, 156, 255, .08);
}

.stage-reticle::before,
.stage-reticle::after {
  content: "";
  position: absolute;
  top: 50%;
  width: 34px;
  height: 2px;
  background: #36dfff;
  box-shadow: 0 0 12px #36dfff;
}

.stage-reticle::before { left: -2px; }
.stage-reticle::after { right: -2px; }

.china-badge {
  position: absolute;
  left: 50%;
  bottom: 17px;
  transform: translateX(-50%);
  min-width: 150px;
  padding: 7px 18px;
  color: #dff9ff;
  font-size: 13px;
  font-weight: 800;
  text-align: center;
  background: linear-gradient(180deg, rgba(42, 158, 255, .66), rgba(5, 44, 91, .88));
  border: 1px solid rgba(104, 217, 255, .58);
  clip-path: polygon(10% 0, 90% 0, 100% 50%, 90% 100%, 10% 100%, 0 50%);
}

.hover-card {
  position: absolute;
  z-index: 9;
  display: grid;
  gap: 4px;
  min-width: 180px;
  padding: 12px;
  pointer-events: none;
  background: rgba(2, 13, 28, .86);
  border: 1px solid rgba(83, 218, 255, .62);
  box-shadow: 0 14px 28px rgba(0, 0, 0, .28), inset 0 0 18px rgba(34, 154, 255, .18);
}

.hover-card strong {
  color: #fff;
}

.hover-card span {
  color: #8edcff;
  font-size: 12px;
}

.hover-card em {
  color: #35efd0;
  font-size: 18px;
  font-style: normal;
  font-weight: 900;
}

.digital-human {
  position: absolute;
  z-index: 7;
  left: 50%;
  bottom: 36px;
  display: block;
  width: min(420px, 54%);
  height: 350px;
  transform: translateX(-50%);
  pointer-events: none;
}

.digital-human::before {
  content: "";
  position: absolute;
  left: 50%;
  bottom: 50px;
  width: 292px;
  height: 82px;
  transform: translateX(-50%);
  background:
    radial-gradient(ellipse at center, rgba(52, 236, 216, .22), transparent 58%),
    radial-gradient(ellipse at center, rgba(49, 147, 255, .22), transparent 70%);
  border: 1px solid rgba(91, 223, 255, .18);
  border-radius: 50%;
  filter: blur(.2px);
}

.digital-human::after {
  content: "";
  position: absolute;
  left: 50%;
  bottom: 82px;
  width: 168px;
  height: 224px;
  transform: translateX(-50%);
  pointer-events: none;
  background: linear-gradient(180deg, rgba(98, 229, 255, .12), rgba(98, 229, 255, 0));
  mask-image: linear-gradient(to bottom, transparent, #000 18%, #000 74%, transparent);
}

.human-orbit {
  position: absolute;
  left: 50%;
  bottom: 56px;
  width: 218px;
  height: 48px;
  transform: translateX(-50%);
  border: 1px solid rgba(69, 213, 255, .48);
  border-radius: 50%;
  box-shadow: 0 0 28px rgba(36, 184, 255, .35), inset 0 0 20px rgba(43, 242, 206, .18);
  animation: orbit 4.2s linear infinite;
}

.xingyun-embed,
.human-fallback {
  position: absolute;
  z-index: 2;
  left: 50%;
  bottom: 38px;
  display: grid;
  place-items: center;
  width: 188px;
  height: 245px;
  overflow: visible;
  transform: translateX(-50%);
  background: transparent;
  border: 0;
  box-shadow: none;
  pointer-events: auto;
}

.xingyun-sdk-container {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 20px 24px rgba(0, 0, 0, .42)) drop-shadow(0 0 18px rgba(75, 211, 255, .22));
  transform: scale(1.01);
  transform-origin: center bottom;
}

.xingyun-sdk-container :deep(canvas) {
  display: block;
  width: 100% !important;
  height: 100% !important;
  object-fit: contain;
}

.xingyun-embed.ready {
  background: transparent;
}

.xingyun-embed.error {
  border-color: rgba(255, 104, 120, .5);
}

.xingyun-status {
  position: absolute;
  left: 50%;
  bottom: 14px;
  display: grid;
  gap: 4px;
  width: 220px;
  padding: 10px 12px;
  transform: translateX(-50%);
  background: rgba(2, 12, 27, .78);
  border: 1px solid rgba(96, 220, 255, .28);
}

.xingyun-status strong {
  color: #fff;
  font-size: 13px;
}

.xingyun-status span {
  color: #8edcff;
  font-size: 11px;
}

.human-fallback img {
  width: min(88%, 166px);
  max-height: 222px;
  object-fit: contain;
  filter: drop-shadow(0 14px 22px rgba(0, 0, 0, .35)) drop-shadow(0 0 16px rgba(58, 220, 255, .28));
}

.voice-wave {
  position: absolute;
  right: 18px;
  bottom: 18px;
  display: flex;
  align-items: center;
  gap: 4px;
  height: 34px;
  padding: 8px 10px;
  border: 1px solid rgba(96, 220, 255, .28);
  border-radius: 999px;
  background: rgba(2, 12, 27, .7);
}

.voice-wave i {
  display: block;
  width: 4px;
  height: 9px;
  border-radius: 9px;
  background: rgba(69, 236, 216, .6);
}

.voice-wave.active i {
  animation: wave 860ms ease-in-out infinite;
}

.voice-wave.active i:nth-child(2) { animation-delay: 100ms; }
.voice-wave.active i:nth-child(3) { animation-delay: 200ms; }
.voice-wave.active i:nth-child(4) { animation-delay: 300ms; }
.voice-wave.active i:nth-child(5) { animation-delay: 400ms; }

.human-copy {
  position: absolute;
  z-index: 3;
  left: 50%;
  bottom: 4px;
  width: min(340px, 100%);
  min-width: 0;
  padding: 7px 14px 8px;
  transform: translateX(-50%);
  text-align: center;
  background: linear-gradient(90deg, rgba(4, 17, 34, .2), rgba(4, 17, 34, .82) 20%, rgba(5, 43, 80, .82) 80%, rgba(4, 17, 34, .2));
  border-top: 1px solid rgba(77, 196, 255, .32);
  border-bottom: 1px solid rgba(77, 196, 255, .18);
  pointer-events: none;
}

.human-copy span {
  color: #68eaff;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: .12em;
}

.human-copy strong {
  display: block;
  margin: 2px 0 3px;
  color: #fff;
  font-size: 15px;
}

.human-copy p {
  margin: 0;
  color: rgba(224, 245, 255, .76);
  font-size: 11px;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.human-actions {
  position: absolute;
  z-index: 4;
  left: calc(50% + 124px);
  bottom: 76px;
  display: grid;
  gap: 6px;
  transform: none;
  pointer-events: auto;
}

.human-actions button {
  gap: 5px;
  min-height: 28px;
  padding: 0 9px;
  font-size: 11px;
  background: rgba(2, 15, 33, .72);
  backdrop-filter: blur(8px);
}

.bottom-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.metric-tile {
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
  min-height: 94px;
  padding: 12px;
  overflow: hidden;
  border: 1px solid rgba(59, 176, 255, .28);
  background: linear-gradient(180deg, rgba(10, 45, 81, .76), rgba(3, 15, 31, .76));
}

.metric-tile > svg {
  width: 34px;
  height: 34px;
  padding: 8px;
  border: 1px solid currentColor;
  background: rgba(255, 255, 255, .05);
}

.metric-tile span,
.metric-tile p {
  color: rgba(220, 241, 255, .64);
  font-size: 12px;
}

.metric-tile div {
  min-width: 0;
}

.metric-tile strong {
  display: block;
  margin: 3px 0;
  color: #fff;
  font-size: 28px;
  line-height: 1;
}

.metric-tile em {
  margin-left: 4px;
  color: rgba(220, 241, 255, .72);
  font-size: 12px;
  font-style: normal;
}

.metric-tile p {
  margin: 0;
  display: -webkit-box;
  overflow: hidden;
  line-height: 1.25;
  overflow-wrap: anywhere;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  white-space: normal;
}

.tone-cyan > svg { color: #4cecff; }
.tone-green > svg { color: #35efd0; }
.tone-gold > svg { color: #ffbf54; }
.tone-violet > svg { color: #9d83ff; }

.gauge-panel {
  min-height: 126px;
}

.gauge-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding-top: 8px;
}

.mini-gauge {
  position: relative;
  display: grid;
  justify-items: center;
  gap: 2px;
  min-height: 74px;
  padding: 12px 6px 7px;
  border: 1px solid rgba(84, 190, 255, .24);
  border-radius: 50% 50% 8px 8px;
  background: radial-gradient(circle at 50% 34%, rgba(48, 226, 206, .25), transparent 48%);
}

.mini-gauge::before {
  content: "";
  position: absolute;
  inset: 8px;
  border-top: 4px solid rgba(66, 213, 255, .8);
  border-right: 4px solid rgba(66, 213, 255, .28);
  border-radius: 50%;
}

.mini-gauge strong {
  position: relative;
  color: #fff;
  font-size: 22px;
  line-height: 1;
}

.mini-gauge span,
.mini-gauge em {
  position: relative;
  color: #9bd4f2;
  font-size: 11px;
  font-style: normal;
}

.ability-panel {
  min-height: 150px;
}

.ability-list {
  display: grid;
  gap: 9px;
  padding-top: 7px;
}

.ability-line {
  display: grid;
  grid-template-columns: 76px 1fr 35px;
  align-items: center;
  gap: 9px;
}

.ability-line span {
  color: #c9eaff;
  font-size: 12px;
}

.ability-line div {
  height: 9px;
  overflow: hidden;
  background: rgba(132, 198, 255, .12);
  border-radius: 999px;
}

.ability-line i {
  display: block;
  height: 100%;
  border-radius: inherit;
  box-shadow: 0 0 16px currentColor;
}

.ability-line strong {
  color: #fff;
  font-size: 13px;
  text-align: right;
}

.screen-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 18px 12px;
  gap: 14px;
}

.footer-status {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
  color: rgba(224, 245, 255, .74);
  font-size: 13px;
}

.footer-status strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.live-dot {
  width: 8px;
  height: 8px;
  flex: 0 0 8px;
  border-radius: 50%;
  background: #35efd0;
  box-shadow: 0 0 18px rgba(53, 239, 208, .84);
}

.footer-actions {
  display: flex;
  gap: 8px;
}

.footer-actions button {
  gap: 6px;
  height: 34px;
  padding: 0 12px;
}

:global(.map-label) {
  display: grid;
  gap: 2px;
  min-width: 98px;
  padding: 6px 8px;
  color: #eaffff;
  text-align: center;
  background: rgba(2, 12, 27, .72);
  border: 1px solid rgba(83, 218, 255, .48);
  box-shadow: 0 0 18px rgba(39, 169, 255, .18);
}

:global(.map-label strong) {
  font-size: 12px;
}

:global(.map-label span) {
  color: #80defc;
  font-size: 10px;
}

:global(.css3d-card) {
  width: 190px;
  padding: 12px;
  color: #eaffff;
  background: linear-gradient(135deg, rgba(7, 31, 62, .92), rgba(9, 70, 126, .74));
  border: 1px solid rgba(91, 223, 255, .72);
  box-shadow: 0 0 28px rgba(53, 190, 255, .35);
  transform-origin: center;
}

:global(.css3d-card span),
:global(.css3d-card em) {
  display: block;
  color: #91dfff;
  font-size: 11px;
  font-style: normal;
}

:global(.css3d-card strong) {
  display: block;
  margin: 5px 0;
  color: #35efd0;
  font-size: 28px;
  line-height: 1;
}

@keyframes wave {
  0%, 100% { height: 9px; opacity: .48; }
  50% { height: 24px; opacity: 1; }
}

@keyframes orbit {
  0%, 100% { transform: translateX(-50%) scale(1); opacity: .72; }
  50% { transform: translateX(-50%) scale(1.08); opacity: 1; }
}

@media (max-width: 1400px) {
  .screen-header {
    grid-template-columns: 180px 230px minmax(280px, 1fr) 230px 180px;
  }

  .screen-body {
    grid-template-columns: 280px minmax(520px, 1fr) 280px;
  }

  .digital-human {
    width: min(390px, 58%);
  }
}

@media (max-width: 1180px) {
  .screen-header {
    grid-template-columns: 1fr;
    height: auto;
    padding-bottom: 10px;
  }

  .screen-tabs,
  .header-wing {
    display: none;
  }

  .screen-body {
    grid-template-columns: 1fr;
    height: auto;
  }

  .screen-column {
    grid-template-columns: repeat(2, minmax(260px, 1fr));
  }

  .center-stage {
    min-height: 760px;
  }
}

@media (max-width: 760px) {
  .report-screen-page {
    overflow: auto;
  }

  .header-title h1 {
    font-size: 22px;
  }

  .screen-body {
    min-height: 0;
    padding: 0 10px;
  }

  .screen-column,
  .bottom-metrics {
    grid-template-columns: 1fr;
  }

  .digital-human {
    width: calc(100% - 24px);
    height: 310px;
    bottom: 52px;
  }

  .human-fallback,
  .xingyun-embed {
    width: 184px;
    height: 230px;
    bottom: 78px;
  }

  .map-toolbar {
    top: 16px;
    left: 12px;
  }
}
</style>
