<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, CirclePlus, DataAnalysis, Delete, DocumentChecked, MagicStick, Promotion, UploadFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { listCourses } from '../../api/courses'
import { listStudentCourses } from '../../api/studentCourses'
import { listProjects } from '../../api/projects'
import { listAchievements } from '../../api/achievements'
import {
  analyzeClass, applyProjectDraft, coachChat, generateEnterpriseEvidence, generateProjectBriefing,
  generateProjectDraft, getAIHealth, listAIAnalyses, precheckAchievement,
} from '../../api/aiAgent'
import { deleteKnowledgeDocument, listKnowledgeDocuments, uploadKnowledgeDocument } from '../../api/knowledge'

const userStore = useUserStore()
const router = useRouter()
const loading = ref(false)
const courses = ref([])
const projects = ref([])
const achievements = ref([])
const selectedCourseId = ref(null)
const selectedProjectId = ref(null)
const selectedAchievementId = ref(null)
const result = ref(null)
const resultVisible = ref(false)
const resultTitle = ref('')
const health = ref(null)
const analyses = ref([])
const documents = ref([])

const chatMessage = ref('')
const sessionId = ref(null)
const chatItems = ref([])
const objective = ref('完成一个具备需求分析、工程实现、自动化测试和成果汇报的软件项目')
const uploadFile = ref(null)
const uploadTitle = ref('')
const draftForm = ref(null)
const applyingDraft = ref(false)
const appliedProject = ref(null)
const difficultyOptions = [
  { label: '基础', value: 1 },
  { label: '进阶', value: 2 },
  { label: '挑战', value: 3 },
]

const roleTitle = computed(() => ({
  student: '实训学伴', teacher: '教学设计助手', enterprise: '岗位评价助手', admin: '智能服务治理',
}[userStore.role] || '教学助手'))
const roleCaption = computed(() => ({
  student: '基于课程资料进行启发式辅导、任务拆解和提交前自检。',
  teacher: '生成项目与评价草案，分析班级学情并形成教学干预建议。',
  enterprise: '从真实成果提取岗位能力证据，并生成追问问题和项目播报。',
  admin: '查看模型健康、知识库覆盖、调用质量和全部 AI 分析记录。',
}[userStore.role]))
const selectedProject = computed(() => projects.value.find((item) => item.id === selectedProjectId.value))
const draftWeightTotal = computed(() => (
  draftForm.value?.indicators || []
).reduce((sum, item) => sum + Number(item.weight || 0), 0))
const canApplyDraft = computed(() => Boolean(
  draftForm.value?.project_name?.trim()
  && draftForm.value?.project_code?.trim()
  && draftForm.value?.description?.trim()
  && draftForm.value?.milestones?.every((item) => item.trim())
  && draftForm.value?.submission_requirements?.every((item) => item.trim())
  && draftForm.value?.indicators?.every((item) => item.name.trim() && item.rule.trim())
  && draftWeightTotal.value === 100
))

function hydrateProjectDraft(data) {
  const suffix = String(data.analysis_id || Date.now()).slice(-6)
  const normalizeTextItems = (items, fallback) => (
    Array.isArray(items) && items.length ? items : fallback
  ).map((item) => typeof item === 'string' ? item : String(item?.event || item?.title || item?.name || item?.description || ''))
  draftForm.value = {
    analysis_id: data.analysis_id,
    course_id: selectedCourseId.value,
    project_name: data.project_name || '软件实训综合项目',
    project_code: `AI-${selectedCourseId.value}-${suffix}`,
    category: '软件开发',
    difficulty: 2,
    duration_days: 14,
    description: data.description || objective.value,
    milestones: normalizeTextItems(data.milestones, ['需求分析与方案设计', '核心功能实现', '测试与成果汇报']),
    submission_requirements: normalizeTextItems(data.submission_requirements, ['源代码或仓库地址', '设计与测试报告', '关键运行截图']),
    indicators: (Array.isArray(data.indicators) && data.indicators.length ? data.indicators : [
      { name: '需求完成度', weight: 30, rule: '核心流程可运行并覆盖项目目标' },
      { name: '代码质量', weight: 25, rule: '结构清晰、异常处理完整' },
      { name: '过程完整性', weight: 25, rule: '体现设计、实现、测试和迭代' },
      { name: '文档与表达', weight: 20, rule: '结论有材料和证据支撑' },
    ]).map((item) => ({ name: item.name || '', weight: Number(item.weight || 0), rule: item.rule || '' })),
  }
  appliedProject.value = null
}

function addDraftItem(key) {
  if (key === 'indicators') draftForm.value.indicators.push({ name: '', weight: 0, rule: '' })
  else draftForm.value[key].push('')
}

function removeDraftItem(key, index) {
  if (draftForm.value[key].length <= 1) return ElMessage.warning('至少保留一项')
  draftForm.value[key].splice(index, 1)
}

async function confirmProjectDraft() {
  if (!canApplyDraft.value) return ElMessage.warning('请补全草案，并确保指标权重合计为 100')
  applyingDraft.value = true
  try {
    const data = await applyProjectDraft(draftForm.value)
    appliedProject.value = data.project
    ElMessage.success('项目与评价量规已创建为未发布草稿')
    await loadContext()
  } finally {
    applyingDraft.value = false
  }
}

async function loadContext() {
  loading.value = true
  try {
    const projectData = await listProjects({ page: 1, page_size: 100 })
    projects.value = projectData.items
    if (userStore.role === 'student') {
      const courseData = await listStudentCourses({ page: 1, page_size: 100 })
      courses.value = courseData.items
    } else if (userStore.role !== 'enterprise') {
      const courseData = await listCourses({ page: 1, page_size: 100 })
      courses.value = courseData.items
    }
    if (!selectedCourseId.value) selectedCourseId.value = courses.value[0]?.id || projects.value[0]?.course_id || null
    if (!selectedProjectId.value) selectedProjectId.value = projects.value.find((item) => !selectedCourseId.value || item.course_id === selectedCourseId.value)?.id || projects.value[0]?.id || null
    await loadAchievements()
    if (userStore.role === 'admin') await loadGovernance()
    await loadDocuments()
  } finally {
    loading.value = false
  }
}

async function loadAchievements() {
  const params = { page: 1, page_size: 100 }
  if (selectedProjectId.value) params.project_id = selectedProjectId.value
  const data = await listAchievements(params)
  achievements.value = data.items
  if (!achievements.value.some((item) => item.id === selectedAchievementId.value)) selectedAchievementId.value = achievements.value[0]?.id || null
}

async function loadDocuments() {
  if (!selectedCourseId.value) { documents.value = []; return }
  try {
    documents.value = await listKnowledgeDocuments({ course_id: selectedCourseId.value, project_id: selectedProjectId.value || undefined })
  } catch { documents.value = [] }
}

async function loadGovernance() {
  health.value = await getAIHealth()
  const data = await listAIAnalyses({ page: 1, page_size: 20 })
  analyses.value = data.items
}

async function sendChat() {
  if (!selectedCourseId.value || !chatMessage.value.trim()) return
  const message = chatMessage.value.trim()
  chatItems.value.push({ role: 'user', content: message })
  chatMessage.value = ''
  loading.value = true
  try {
    const data = await coachChat({ course_id: selectedCourseId.value, project_id: selectedProjectId.value, session_id: sessionId.value, message })
    sessionId.value = data.session_id
    chatItems.value.push({ role: 'assistant', content: data.answer, hints: data.hints, citations: data.citations, nextActions: data.next_actions, available: data.available })
  } finally { loading.value = false }
}

async function runAction(type) {
  loading.value = true
  try {
    if (type === 'draft') {
      if (!selectedCourseId.value) return ElMessage.warning('请先选择课程')
      result.value = await generateProjectDraft({ course_id: selectedCourseId.value, objective: objective.value, difficulty: 2, duration_days: 14 })
      hydrateProjectDraft(result.value)
      resultTitle.value = 'AI 项目与量规草案'
    } else if (type === 'precheck') {
      if (!selectedAchievementId.value) return ElMessage.warning('请选择成果')
      result.value = await precheckAchievement(selectedAchievementId.value)
      resultTitle.value = '提交前自检结果'
    } else if (type === 'class') {
      if (!selectedProjectId.value) return ElMessage.warning('请选择项目')
      result.value = await analyzeClass(selectedProjectId.value)
      resultTitle.value = '班级学情分析'
    } else if (type === 'evidence') {
      if (!selectedAchievementId.value) return ElMessage.warning('请选择成果')
      result.value = await generateEnterpriseEvidence(selectedAchievementId.value)
      resultTitle.value = '岗位能力证据'
    } else if (type === 'briefing') {
      if (!selectedProjectId.value) return ElMessage.warning('请选择项目')
      result.value = await generateProjectBriefing(selectedProjectId.value)
      resultTitle.value = '数字人项目播报'
      localStorage.setItem('ste-briefing-script', result.value.script || '')
    }
    resultVisible.value = true
  } finally { loading.value = false }
}

function chooseUpload(file) { uploadFile.value = file.raw }
async function uploadDocument() {
  if (!selectedCourseId.value || !uploadFile.value) return ElMessage.warning('请选择课程和资料文件')
  loading.value = true
  try {
    await uploadKnowledgeDocument({ courseId: selectedCourseId.value, projectId: selectedProjectId.value, title: uploadTitle.value, file: uploadFile.value })
    uploadFile.value = null; uploadTitle.value = ''
    ElMessage.success('资料已解析并加入知识库')
    await loadDocuments()
  } finally { loading.value = false }
}
async function removeDocument(id) { await deleteKnowledgeDocument(id); await loadDocuments() }
function openReport() { router.push({ name: 'report-screen' }) }
function pretty(value) { return JSON.stringify(value, null, 2) }

watch(selectedCourseId, () => {
  const project = projects.value.find((item) => item.course_id === selectedCourseId.value)
  selectedProjectId.value = project?.id || null
  loadDocuments()
})
watch(selectedProjectId, () => { loadAchievements(); loadDocuments() })
onMounted(loadContext)
</script>

<template>
  <section class="feature-page ai-page">
    <div class="feature-hero">
      <div><p class="page-eyebrow">ASSISTANT</p><h2>{{ roleTitle }}</h2><p>{{ roleCaption }}</p></div>
      <el-tag :type="health?.configured === false ? 'warning' : 'success'" effect="plain">{{ health?.configured === false ? '基础规则可用' : '结果需人工确认' }}</el-tag>
    </div>

    <div class="context-bar data-panel">
      <el-select v-if="userStore.role !== 'enterprise'" v-model="selectedCourseId" placeholder="选择课程" filterable><el-option v-for="c in courses" :key="c.id" :label="c.course_name" :value="c.id" /></el-select>
      <el-select v-model="selectedProjectId" placeholder="选择项目" clearable filterable><el-option v-for="p in projects.filter((item) => !selectedCourseId || item.course_id === selectedCourseId)" :key="p.id" :label="p.project_name" :value="p.id" /></el-select>
      <el-select v-if="['student', 'enterprise'].includes(userStore.role)" v-model="selectedAchievementId" placeholder="选择成果" clearable filterable><el-option v-for="a in achievements" :key="a.id" :label="a.title" :value="a.id" /></el-select>
      <span>{{ selectedProject?.project_name || '选择上下文后开始' }}</span>
    </div>

    <div v-if="userStore.role === 'student'" class="ai-grid student-grid">
      <article class="data-panel chat-panel">
        <div class="panel-heading"><div><h3>启发式实训学伴</h3><span>回答会引用课程资料，不生成可直接提交的完整项目</span></div></div>
        <div class="chat-list" v-loading="loading">
          <div v-if="!chatItems.length" class="coach-welcome"><el-icon><MagicStick /></el-icon><strong>把你卡住的地方告诉我</strong><span>例如：我应该怎样拆解登录模块的异常处理？</span></div>
          <div v-for="(item, index) in chatItems" :key="index" :class="['chat-item', item.role]">
            <p>{{ item.content }}</p>
            <ul v-if="item.hints?.length"><li v-for="hint in item.hints" :key="hint">{{ hint }}</li></ul>
            <div v-if="item.citations?.length" class="citation-list"><span v-for="cite in item.citations" :key="cite.chunk_id">{{ cite.title }} · {{ cite.source_label }}</span></div>
          </div>
        </div>
        <div class="chat-input"><el-input v-model="chatMessage" type="textarea" :rows="3" placeholder="描述当前目标、已尝试的方法和遇到的问题" @keydown.ctrl.enter="sendChat" /><el-button type="primary" :icon="Promotion" :loading="loading" @click="sendChat">发送</el-button></div>
      </article>
      <aside class="data-panel action-panel"><div class="panel-heading"><h3>提交前自检</h3></div><p>从完整性、测试证据和材料可访问性检查当前成果。</p><el-button type="primary" :icon="DocumentChecked" :disabled="!selectedAchievementId" @click="runAction('precheck')">开始自检</el-button></aside>
    </div>

    <div v-else-if="userStore.role === 'teacher'" class="ai-grid">
      <article class="data-panel tool-panel project-designer">
        <div class="panel-heading"><div><h3>项目设计</h3><span>根据教学目标整理项目、里程碑、提交要求和评价量规</span></div></div>
        <el-input v-model="objective" type="textarea" :rows="5" placeholder="描述课程目标、学生基础、希望完成的真实任务和最终产出" />
        <div class="design-actions">
          <span>草案先由教师审核，不会直接向学生发布。</span>
          <el-button type="primary" :icon="MagicStick" :loading="loading" @click="runAction('draft')">生成可编辑草案</el-button>
        </div>
      </article>
      <article class="data-panel tool-panel"><div class="panel-heading"><div><h3>班级学情分析</h3><span>聚合成果状态、薄弱能力与教学干预建议</span></div></div><p>当前项目共有 {{ achievements.length }} 份成果。</p><el-button type="primary" :icon="DataAnalysis" @click="runAction('class')">生成学情分析</el-button><el-button @click="runAction('briefing')">生成数字人播报</el-button></article>
    </div>

    <div v-else-if="userStore.role === 'enterprise'" class="ai-grid">
      <article class="data-panel tool-panel"><div class="panel-heading"><div><h3>岗位能力证据</h3><span>仅依据成果材料整理，不作录用结论</span></div></div><p>选择成果后提取工程实现、质量意识和表达协作证据。</p><el-button type="primary" :icon="DocumentChecked" @click="runAction('evidence')">提取证据与追问</el-button></article>
      <article class="data-panel tool-panel"><div class="panel-heading"><div><h3>项目数据播报</h3><span>为魔珐星云数字人生成真实数据讲稿</span></div></div><el-button type="primary" :icon="MagicStick" @click="runAction('briefing')">生成播报稿</el-button><el-button @click="openReport">打开实训大屏</el-button></article>
    </div>

    <div v-else class="governance-grid" v-loading="loading">
      <article v-for="item in [{label:'模型状态',value:health?.configured?'已配置':'降级模式'},{label:'调用成功率',value:`${health?.success_rate||0}%`},{label:'平均耗时',value:`${health?.average_duration_ms||0}ms`},{label:'知识资料',value:health?.knowledge_documents_ready||0}]" :key="item.label" class="data-panel governance-card"><span>{{ item.label }}</span><strong>{{ item.value }}</strong></article>
      <article class="data-panel governance-table"><div class="panel-heading"><h3>AI 分析审计记录</h3></div><el-table :data="analyses"><el-table-column prop="scene" label="场景" min-width="150" /><el-table-column prop="biz_type" label="业务" width="120" /><el-table-column prop="model_name" label="模型" min-width="130" /><el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="row.status===1?'success':'warning'" effect="plain">{{ row.status===1?'成功':'降级' }}</el-tag></template></el-table-column><el-table-column prop="create_time" label="时间" min-width="170" /></el-table></article>
    </div>

    <article v-if="['teacher', 'enterprise', 'admin'].includes(userStore.role)" class="data-panel knowledge-panel">
      <div class="panel-heading"><div><h3>课程与岗位知识库</h3><span>PDF、Word、文本和代码资料会分段检索并作为 AI 回答依据</span></div></div>
      <div class="knowledge-toolbar"><el-input v-model="uploadTitle" placeholder="资料标题（选填）" /><el-upload :auto-upload="false" :limit="1" :on-change="chooseUpload" :show-file-list="true"><el-button :icon="UploadFilled">选择资料</el-button></el-upload><el-button type="primary" :disabled="!uploadFile || !selectedCourseId" @click="uploadDocument">加入知识库</el-button></div>
      <el-table :data="documents"><el-table-column prop="title" label="资料" min-width="180" /><el-table-column prop="file_name" label="文件" min-width="180" show-overflow-tooltip /><el-table-column label="状态" width="100"><template #default="{row}"><el-tag :type="row.status===1?'success':'warning'" effect="plain">{{ row.status===1?'可检索':'解析失败' }}</el-tag></template></el-table-column><el-table-column label="操作" width="90"><template #default="{row}"><el-button text type="danger" @click="removeDocument(row.id)">删除</el-button></template></el-table-column></el-table>
    </article>

    <el-drawer v-model="resultVisible" :title="resultTitle" :size="draftForm && resultTitle.includes('草案') ? '68%' : '48%'">
      <template v-if="draftForm && resultTitle.includes('草案')">
        <div v-if="appliedProject" class="draft-success">
          <el-icon><Check /></el-icon>
          <div><strong>项目与量规已创建</strong><span>{{ appliedProject.project_code }} · 当前为未发布状态</span></div>
          <el-button type="primary" @click="router.push({ name: 'training-management' })">继续配置并发布</el-button>
        </div>
        <div class="result-summary">
          <el-tag :type="result?.available===false ? 'warning' : 'success'" effect="plain">{{ result?.available===false ? '规则降级草案' : 'AI 草案已生成' }}</el-tag>
          <span>所有内容均可编辑，确认后才写入业务数据</span>
        </div>
        <el-form v-if="draftForm" label-position="top" class="draft-form">
          <div class="draft-grid">
            <el-form-item label="项目名称"><el-input v-model="draftForm.project_name" maxlength="150" /></el-form-item>
            <el-form-item label="项目编码"><el-input v-model="draftForm.project_code" maxlength="64" /></el-form-item>
            <el-form-item label="项目类别"><el-input v-model="draftForm.category" maxlength="50" /></el-form-item>
            <el-form-item label="实施周期"><el-input-number v-model="draftForm.duration_days" :min="1" :max="180" /><span class="field-unit">天</span></el-form-item>
          </div>
          <el-form-item label="项目背景与目标"><el-input v-model="draftForm.description" type="textarea" :rows="4" maxlength="5000" show-word-limit /></el-form-item>
          <el-form-item label="难度"><el-segmented v-model="draftForm.difficulty" :options="difficultyOptions" /></el-form-item>

          <section class="draft-section">
            <div class="draft-section-title"><div><strong>项目里程碑</strong><span>学生按阶段推进的关键检查点</span></div><el-button text type="primary" :icon="CirclePlus" @click="addDraftItem('milestones')">添加</el-button></div>
            <div v-for="(_item, index) in draftForm.milestones" :key="`milestone-${index}`" class="draft-list-row"><span>{{ index + 1 }}</span><el-input v-model="draftForm.milestones[index]" /><el-button text :icon="Delete" title="删除里程碑" @click="removeDraftItem('milestones', index)" /></div>
          </section>

          <section class="draft-section">
            <div class="draft-section-title"><div><strong>提交要求</strong><span>学生最终需要提交的证据材料</span></div><el-button text type="primary" :icon="CirclePlus" @click="addDraftItem('submission_requirements')">添加</el-button></div>
            <div v-for="(_item, index) in draftForm.submission_requirements" :key="`requirement-${index}`" class="draft-list-row"><span>{{ index + 1 }}</span><el-input v-model="draftForm.submission_requirements[index]" /><el-button text :icon="Delete" title="删除提交要求" @click="removeDraftItem('submission_requirements', index)" /></div>
          </section>

          <section class="draft-section rubric-section">
            <div class="draft-section-title"><div><strong>评价量规</strong><span>AI 预评和人工评价共同参考，最终成绩仍由教师和企业导师决定</span></div><div><el-tag :type="draftWeightTotal === 100 ? 'success' : 'warning'" effect="plain">权重 {{ draftWeightTotal }} / 100</el-tag><el-button text type="primary" :icon="CirclePlus" @click="addDraftItem('indicators')">添加</el-button></div></div>
            <div v-for="(_item, index) in draftForm.indicators" :key="`indicator-${index}`" class="rubric-row">
              <span>{{ index + 1 }}</span>
              <el-input v-model="draftForm.indicators[index].name" placeholder="指标名称" />
              <el-input-number v-model="draftForm.indicators[index].weight" :min="1" :max="100" controls-position="right" />
              <el-input v-model="draftForm.indicators[index].rule" type="textarea" :rows="2" placeholder="可观察、可举证的评分规则" />
              <el-button text :icon="Delete" title="删除评价指标" @click="removeDraftItem('indicators', index)" />
            </div>
          </section>
        </el-form>
        <div class="draft-footer">
          <span>创建后状态为“未开始”，学生不可见，也不会生成提交任务。</span>
          <el-button type="primary" :icon="Check" :loading="applyingDraft" :disabled="!canApplyDraft || Boolean(appliedProject)" @click="confirmProjectDraft">确认创建项目与量规</el-button>
        </div>
      </template>
      <template v-else>
        <div class="result-summary"><el-tag :type="result?.available===false?'warning':'success'" effect="plain">{{ result?.available===false?'规则降级结果':'AI 分析完成' }}</el-tag><el-button v-if="resultTitle.includes('播报')" type="primary" @click="openReport">交给数字人讲解</el-button></div>
        <pre>{{ pretty(result) }}</pre>
      </template>
    </el-drawer>
  </section>
</template>

<style scoped>
.context-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; padding: 14px 16px; }.context-bar .el-select { width: 240px; }.context-bar > span { margin-left: auto; color: var(--ste-muted); font-size: 12px; }
.ai-grid { display: grid; grid-template-columns: 1.25fr .75fr; gap: 16px; margin-bottom: 16px; }.chat-panel { overflow: hidden; }.chat-list { min-height: 360px; max-height: 500px; overflow-y: auto; padding: 16px; background: #fafcff; }.coach-welcome { display: grid; justify-items: center; gap: 8px; padding: 80px 20px; color: var(--ste-muted); }.coach-welcome .el-icon { color: var(--ste-primary); font-size: 28px; }.chat-item { max-width: 84%; margin-bottom: 12px; padding: 11px 13px; border: 1px solid var(--ste-border); border-radius: 8px; background: #fff; }.chat-item.user { margin-left: auto; color: #fff; background: var(--ste-primary); border-color: var(--ste-primary); }.chat-item p { margin: 0; line-height: 1.7; }.chat-item ul { margin: 9px 0 0; padding-left: 18px; color: #4c5a71; font-size: 13px; }.citation-list { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }.citation-list span { padding: 4px 7px; color: #315d9e; font-size: 11px; background: #edf3ff; border-radius: 4px; }.chat-input { display: grid; grid-template-columns: 1fr auto; gap: 10px; padding: 14px; border-top: 1px solid var(--ste-border); }.action-panel, .tool-panel { padding: 0 18px 20px; }.action-panel p, .tool-panel p { color: var(--ste-muted); font-size: 13px; line-height: 1.7; }.tool-panel > .el-textarea { margin-bottom: 14px; }
.project-designer { display: flex; flex-direction: column; }.design-actions { display: flex; align-items: center; justify-content: space-between; gap: 12px; }.design-actions span { color: var(--ste-muted); font-size: 12px; }
.draft-success { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 12px; margin-bottom: 16px; padding: 14px; color: #1f6b45; background: #eef9f3; border: 1px solid #bfe7cf; border-radius: 6px; }.draft-success .el-icon { font-size: 22px; }.draft-success div { display: grid; gap: 3px; }.draft-success span { color: #5d796a; font-size: 12px; }.result-summary > span { color: var(--ste-muted); font-size: 12px; }.draft-form { padding-bottom: 78px; }.draft-grid { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr; gap: 12px; }.field-unit { margin-left: 8px; color: var(--ste-muted); font-size: 12px; }.draft-section { margin-top: 18px; padding-top: 16px; border-top: 1px solid var(--ste-border); }.draft-section-title { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px; }.draft-section-title > div { display: flex; align-items: center; gap: 10px; }.draft-section-title span { color: var(--ste-muted); font-size: 12px; }.draft-list-row { display: grid; grid-template-columns: 24px minmax(0, 1fr) 34px; align-items: center; gap: 8px; margin-bottom: 8px; }.draft-list-row > span, .rubric-row > span { display: grid; place-items: center; width: 24px; height: 24px; color: #526176; font-size: 11px; background: #eef2f7; border-radius: 50%; }.rubric-row { display: grid; grid-template-columns: 24px minmax(130px, .75fr) 130px minmax(240px, 1.5fr) 34px; align-items: center; gap: 8px; margin-bottom: 9px; }.rubric-row .el-input-number { width: 130px; }.draft-footer { position: absolute; right: 20px; bottom: 0; left: 20px; z-index: 2; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 0 18px; background: #fff; border-top: 1px solid var(--ste-border); }.draft-footer span { color: var(--ste-muted); font-size: 12px; }
.knowledge-panel { margin-top: 16px; overflow: hidden; }.knowledge-toolbar { display: grid; grid-template-columns: minmax(180px, 1fr) auto auto; gap: 10px; padding: 10px 18px 18px; }.knowledge-panel .el-table { padding: 0 10px 10px; }
.governance-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }.governance-card { display: grid; gap: 9px; padding: 20px; }.governance-card span { color: var(--ste-muted); font-size: 12px; }.governance-card strong { font-size: 24px; }.governance-table { grid-column: 1 / -1; overflow: hidden; }.governance-table .el-table { padding: 0 10px 12px; }.result-summary { display: flex; justify-content: space-between; margin-bottom: 16px; }.result-summary + pre { overflow: auto; padding: 16px; color: #d9e8ff; line-height: 1.65; white-space: pre-wrap; background: #10243f; border-radius: 8px; }
@media (max-width: 1024px) { .ai-grid { grid-template-columns: 1fr; }.governance-grid { grid-template-columns: repeat(2, 1fr); }.draft-grid { grid-template-columns: repeat(2, 1fr); }.rubric-row { grid-template-columns: 24px 1fr 120px 34px; }.rubric-row .el-textarea { grid-column: 2 / 4; } }
@media (max-width: 700px) { .context-bar, .knowledge-toolbar { align-items: stretch; grid-template-columns: 1fr; flex-direction: column; }.context-bar .el-select { width: 100%; }.context-bar > span { margin-left: 0; }.governance-grid, .draft-grid { grid-template-columns: 1fr; }.chat-input { grid-template-columns: 1fr; }.design-actions, .draft-section-title, .draft-footer { align-items: stretch; flex-direction: column; }.rubric-row { grid-template-columns: 24px minmax(0, 1fr) 34px; }.rubric-row .el-input-number, .rubric-row .el-textarea { grid-column: 2 / 3; width: 100%; } }
</style>
