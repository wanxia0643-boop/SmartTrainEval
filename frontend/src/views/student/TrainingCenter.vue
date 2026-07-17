<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotRound, Check, DocumentChecked, MagicStick, Promotion, Refresh, UploadFilled,
} from '@element-plus/icons-vue'
import { listProjects } from '../../api/projects'
import { createAchievement, listAchievements, updateAchievement } from '../../api/achievements'
import { uploadAttachment } from '../../api/uploads'
import { coachChat, listAIAnalyses, precheckAchievement } from '../../api/aiAgent'
import { listWorkItems } from '../../api/workItems'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

const PROJECT_STATUS = {
  0: { label: '未开始', type: 'info' },
  1: { label: '进行中', type: 'success' },
  2: { label: '已结束', type: 'warning' },
  3: { label: '已归档', type: 'info' },
}
const ACHIEVEMENT_STATUS = {
  0: { label: '草稿', type: 'info' },
  1: { label: '已提交', type: 'primary' },
  2: { label: '评价中', type: 'warning' },
  3: { label: '已评价', type: 'success' },
  4: { label: '退回整改', type: 'danger' },
}
const PROMPTS = [
  '帮我把当前项目拆成今天可以完成的步骤',
  '根据项目要求，我现在最应该验证什么？',
  '检查我的成果说明还缺少哪些证据',
]

const loading = ref(false)
const saving = ref(false)
const uploadLoading = ref(false)
const coachLoading = ref(false)
const precheckLoading = ref(false)
const projects = ref([])
const achievements = ref([])
const workItems = ref([])
const selectedProjectId = ref(null)
const currentAchievement = ref(null)
const precheckCache = ref({})
const coachSessionId = ref(null)
const coachMessage = ref('')
const coachItems = ref([])
const formRef = ref()

const form = reactive({
  id: null,
  project_id: null,
  title: '',
  content: '',
  repo_url: '',
  attachment_url: '',
  status: 0,
})

const rules = {
  title: [{ required: true, message: '请填写成果标题', trigger: 'blur' }],
  content: [{ required: true, message: '请填写成果说明和关键过程证据', trigger: 'blur' }],
}

const selectedProject = computed(() => projects.value.find((item) => item.id === selectedProjectId.value))
const editable = computed(() => !currentAchievement.value || ![2, 3].includes(currentAchievement.value.status))
const currentPrecheck = computed(() => (form.id ? precheckCache.value[form.id] || null : null))
const selectedTasks = computed(() => workItems.value.filter((item) => (
  (item.biz_type === 'PROJECT' && item.biz_id === selectedProjectId.value)
  || (currentAchievement.value && item.biz_type === 'ACHIEVEMENT' && item.biz_id === currentAchievement.value.id)
)))
const counts = computed(() => ({
  projects: projects.value.length,
  tasks: workItems.value.length,
  drafts: achievements.value.filter((item) => [0, 4].includes(item.status)).length,
  evaluated: achievements.value.filter((item) => item.status === 3).length,
}))

function projectStatus(status) {
  return PROJECT_STATUS[status] || PROJECT_STATUS[0]
}

function achievementStatus(status) {
  return ACHIEVEMENT_STATUS[status] || ACHIEVEMENT_STATUS[0]
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '未设置'
}

function latestAchievement(projectId) {
  return achievements.value.find((item) => item.project_id === projectId) || null
}

function resetForm(project) {
  Object.assign(form, {
    id: null,
    project_id: project?.id || null,
    title: project ? `${project.project_name}成果` : '',
    content: '',
    repo_url: '',
    attachment_url: '',
    status: 0,
  })
}

function selectProject(project) {
  selectedProjectId.value = project?.id || null
  currentAchievement.value = project ? latestAchievement(project.id) : null
  if (currentAchievement.value) {
    Object.assign(form, {
      id: currentAchievement.value.id,
      project_id: currentAchievement.value.project_id,
      title: currentAchievement.value.title,
      content: currentAchievement.value.content || '',
      repo_url: currentAchievement.value.repo_url || '',
      attachment_url: currentAchievement.value.attachment_url || '',
      status: currentAchievement.value.status,
    })
  } else {
    resetForm(project)
  }
  coachSessionId.value = null
  coachItems.value = []
}

async function loadAll({ preserveProject = true } = {}) {
  loading.value = true
  try {
    const [projectData, achievementData, taskData, analysisData] = await Promise.all([
      listProjects({ page: 1, page_size: 100 }),
      listAchievements({ student_id: userStore.userId, page: 1, page_size: 100 }),
      listWorkItems({ status: 0, page: 1, page_size: 100 }),
      listAIAnalyses({ scene: 'ACHIEVEMENT_PRECHECK', page: 1, page_size: 100 }),
    ])
    projects.value = projectData.items
    achievements.value = achievementData.items
    workItems.value = taskData.items
    const cache = {}
    analysisData.items.forEach((item) => {
      if (!cache[item.biz_id]) {
        cache[item.biz_id] = {
          ...item.result,
          citations: item.citations || [],
          available: item.status === 1,
          analysis_id: item.id,
        }
      }
    })
    precheckCache.value = cache
    const next = preserveProject
      ? projects.value.find((item) => item.id === selectedProjectId.value)
      : null
    selectProject(next || projects.value.find((item) => item.status === 1) || projects.value[0] || null)
  } finally {
    loading.value = false
  }
}

async function refreshAchievementsAndTasks() {
  const [achievementData, taskData] = await Promise.all([
    listAchievements({ student_id: userStore.userId, page: 1, page_size: 100 }),
    listWorkItems({ status: 0, page: 1, page_size: 100 }),
  ])
  achievements.value = achievementData.items
  workItems.value = taskData.items
  if (form.id) currentAchievement.value = achievements.value.find((item) => item.id === form.id) || currentAchievement.value
}

async function handleUpload(file) {
  uploadLoading.value = true
  try {
    const data = await uploadAttachment(file)
    form.attachment_url = data.file_url
    if (data.extracted_text && !form.content.trim()) form.content = data.extracted_text.slice(0, 8000)
    ElMessage.success('附件已上传并提取可检索文本')
  } finally {
    uploadLoading.value = false
  }
  return false
}

async function persistAchievement(status, { silent = false } = {}) {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid || !selectedProject.value) return null
  saving.value = true
  try {
    const payload = {
      title: form.title,
      content: form.content || null,
      repo_url: form.repo_url || null,
      attachment_url: form.attachment_url || null,
      status,
    }
    const data = form.id
      ? await updateAchievement(form.id, payload)
      : await createAchievement({
        ...payload,
        project_id: selectedProject.value.id,
        student_id: userStore.userId,
      })
    form.id = data.id
    form.status = data.status
    currentAchievement.value = data
    await refreshAchievementsAndTasks()
    if (!silent) ElMessage.success(status === 0 ? '草稿已保存' : '成果已提交，评价任务已生成')
    return data
  } finally {
    saving.value = false
  }
}

async function saveDraft() {
  const status = currentAchievement.value?.status === 1 ? 1 : 0
  await persistAchievement(status)
}

async function submitAchievement() {
  const check = currentPrecheck.value
  const description = !check
    ? '尚未运行提交前自检，仍要提交吗？'
    : check.ready_to_submit
      ? `AI 自检完整度 ${check.completeness_score} 分，确认提交并进入多方评价？`
      : `AI 自检仍发现待改进项（完整度 ${check.completeness_score} 分），确认继续提交？`
  try {
    await ElMessageBox.confirm(description, '确认提交成果', {
      confirmButtonText: '确认提交', cancelButtonText: '继续完善', type: check?.ready_to_submit ? 'success' : 'warning',
    })
  } catch {
    return
  }
  await persistAchievement(1)
}

async function runPrecheck() {
  if (!editable.value) return
  precheckLoading.value = true
  try {
    const saveStatus = currentAchievement.value?.status === 1 ? 1 : 0
    const achievement = await persistAchievement(saveStatus, { silent: true })
    if (!achievement) return
    const data = await precheckAchievement(achievement.id)
    precheckCache.value = { ...precheckCache.value, [achievement.id]: data }
    ElMessage[data.available === false ? 'warning' : 'success'](
      data.available === false ? '模型不可用，已返回规则化自检清单' : '提交前自检完成',
    )
  } finally {
    precheckLoading.value = false
  }
}

async function sendCoach(preset = null) {
  const message = (preset || coachMessage.value).trim()
  if (!message || !selectedProject.value?.course_id) return
  coachItems.value.push({ role: 'user', content: message })
  coachMessage.value = ''
  coachLoading.value = true
  try {
    const data = await coachChat({
      course_id: selectedProject.value.course_id,
      project_id: selectedProject.value.id,
      achievement_id: form.id || null,
      session_id: coachSessionId.value,
      message,
    })
    coachSessionId.value = data.session_id
    coachItems.value.push({
      role: 'assistant', content: data.answer, hints: data.hints,
      citations: data.citations, nextActions: data.next_actions, available: data.available,
    })
  } finally {
    coachLoading.value = false
  }
}

onMounted(() => loadAll({ preserveProject: false }))
</script>

<template>
  <section class="feature-page student-training-page" v-loading="loading">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">STUDENT · GUIDED PRACTICE</p>
        <h2>AI 实训工作台</h2>
        <p>围绕真实项目完成任务拆解、过程辅导、成果草稿与提交前证据自检。</p>
      </div>
      <el-tag type="success" effect="plain">AI 辅助，不代写成果</el-tag>
    </div>

    <section class="stats-strip" aria-label="学生实训进度">
      <article><span>可参与项目</span><strong>{{ counts.projects }}</strong></article>
      <article><span>当前待办</span><strong>{{ counts.tasks }}</strong></article>
      <article><span>草稿与整改</span><strong>{{ counts.drafts }}</strong></article>
      <article><span>已完成评价</span><strong>{{ counts.evaluated }}</strong></article>
    </section>

    <div class="student-workspace">
      <aside class="data-panel project-rail">
        <div class="panel-heading">
          <div><h3>我的实训项目</h3><span>仅显示已选课程内项目</span></div>
          <el-button :icon="Refresh" circle title="刷新项目" @click="loadAll" />
        </div>
        <button
          v-for="project in projects"
          :key="project.id"
          type="button"
          class="project-row"
          :class="{ active: project.id === selectedProjectId }"
          @click="selectProject(project)"
        >
          <span class="project-index">{{ String(project.id).padStart(2, '0') }}</span>
          <span class="project-copy">
            <strong>{{ project.project_name }}</strong>
            <small>{{ project.project_code }} · {{ projectStatus(project.status).label }}</small>
          </span>
          <el-icon v-if="latestAchievement(project.id)?.status === 3" class="project-done"><Check /></el-icon>
          <span v-else-if="workItems.some((item) => item.biz_id === project.id)" class="task-dot" title="有待办任务" />
        </button>
        <el-empty v-if="!projects.length" :image-size="70" description="请先完成课程选课" />
      </aside>

      <main v-if="selectedProject" class="project-main">
        <article class="data-panel project-overview">
          <div class="panel-heading">
            <div>
              <h3>{{ selectedProject.project_name }}</h3>
              <span>{{ selectedProject.category || '软件实训' }} · {{ selectedProject.project_code }}</span>
            </div>
            <el-tag :type="projectStatus(selectedProject.status).type" effect="plain">{{ projectStatus(selectedProject.status).label }}</el-tag>
          </div>
          <p>{{ selectedProject.description || '教师尚未填写项目详细要求。' }}</p>
          <div class="project-meta">
            <span>截止时间 {{ formatDate(selectedProject.end_time) }}</span>
            <span v-for="item in selectedTasks" :key="item.id" class="task-chip">{{ item.title }}</span>
          </div>
        </article>

        <div class="practice-grid">
          <article class="data-panel editor-panel">
            <div class="panel-heading">
              <div><h3>成果草稿</h3><span>保存草稿不会生成教师或企业评价任务</span></div>
              <el-tag :type="achievementStatus(form.status).type" effect="plain">{{ achievementStatus(form.status).label }}</el-tag>
            </div>
            <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="achievement-form">
              <el-form-item label="成果标题" prop="title"><el-input v-model="form.title" :disabled="!editable" placeholder="明确描述本次实训产出" /></el-form-item>
              <el-form-item label="代码仓库"><el-input v-model="form.repo_url" :disabled="!editable" placeholder="Git 仓库或可访问的代码地址" /></el-form-item>
              <el-form-item label="成果说明与过程证据" prop="content">
                <el-input v-model="form.content" :disabled="!editable" type="textarea" :rows="9" placeholder="说明需求、方案、实现、测试、迭代过程及对应证据" />
              </el-form-item>
              <el-form-item label="成果附件">
                <div class="upload-row">
                  <el-upload :show-file-list="false" :before-upload="handleUpload" :disabled="!editable">
                    <el-button :icon="UploadFilled" :loading="uploadLoading" :disabled="!editable">上传附件</el-button>
                  </el-upload>
                  <a v-if="form.attachment_url" :href="form.attachment_url" target="_blank" rel="noreferrer">查看已上传附件</a>
                  <span v-else>支持文档、代码和压缩包</span>
                </div>
              </el-form-item>
            </el-form>
            <div class="editor-actions">
              <span v-if="!editable">成果已进入评价流程，当前为只读状态</span>
              <span v-else>正式提交后才会通知教师与企业导师</span>
              <div>
                <el-button :icon="DocumentChecked" :loading="saving" :disabled="!editable" @click="saveDraft">{{ form.status === 1 ? '保存修改' : '保存草稿' }}</el-button>
                <el-button type="primary" :icon="Promotion" :loading="saving" :disabled="!editable" @click="submitAchievement">{{ form.status === 4 ? '重新提交' : '提交成果' }}</el-button>
              </div>
            </div>
          </article>

          <article class="data-panel coach-panel">
            <div class="panel-heading">
              <div><h3>AI 实训学伴</h3><span>结合当前项目、成果草稿和课程资料启发式辅导</span></div>
              <ChatDotRound />
            </div>
            <div class="coach-list" v-loading="coachLoading">
              <div v-if="!coachItems.length" class="coach-welcome">
                <MagicStick />
                <strong>从一个具体问题开始</strong>
                <span>AI 会给出问题定位、分步提示、资料引用和下一步行动。</span>
                <button v-for="prompt in PROMPTS" :key="prompt" type="button" @click="sendCoach(prompt)">{{ prompt }}</button>
              </div>
              <div v-for="(item, index) in coachItems" :key="index" class="coach-message" :class="item.role">
                <strong>{{ item.role === 'user' ? '我' : 'AI 学伴' }}</strong>
                <p>{{ item.content }}</p>
                <template v-if="item.role === 'assistant'">
                  <div v-if="item.hints?.length" class="coach-section"><span>分步提示</span><ol><li v-for="hint in item.hints" :key="hint">{{ hint }}</li></ol></div>
                  <div v-if="item.nextActions?.length" class="next-actions"><span v-for="action in item.nextActions" :key="action">{{ action }}</span></div>
                  <div v-if="item.citations?.length" class="coach-citations"><small>引用资料</small><span v-for="citation in item.citations" :key="citation.chunk_id">{{ citation.title }} · {{ citation.source_label }}</span></div>
                </template>
              </div>
            </div>
            <div class="coach-input">
              <el-input v-model="coachMessage" type="textarea" :rows="3" placeholder="描述目标、已尝试的方法和卡住的位置" @keydown.ctrl.enter="sendCoach()" />
              <el-button type="primary" :icon="Promotion" :loading="coachLoading" :disabled="!coachMessage.trim()" @click="sendCoach()">发送</el-button>
            </div>
          </article>
        </div>

        <article class="data-panel precheck-panel">
          <div class="panel-heading">
            <div><h3>提交前 AI 自检</h3><span>依据项目量规和课程规范检查证据完整性，不计入最终成绩</span></div>
            <el-button type="primary" :icon="MagicStick" :loading="precheckLoading" :disabled="!editable" @click="runPrecheck">{{ currentPrecheck ? '重新自检' : '开始自检' }}</el-button>
          </div>
          <template v-if="currentPrecheck">
            <div class="precheck-summary">
              <div class="precheck-score" :class="{ ready: currentPrecheck.ready_to_submit }">{{ currentPrecheck.completeness_score }}</div>
              <div><strong>{{ currentPrecheck.ready_to_submit ? '已具备提交条件' : '建议继续完善证据' }}</strong><span>{{ currentPrecheck.available === false ? '规则降级结果' : 'DeepSeek 结构化自检' }}</span></div>
              <div class="context-badges">
                <span v-if="currentPrecheck.context_summary">量规 {{ currentPrecheck.context_summary.indicator_count }} 项</span>
                <span v-if="currentPrecheck.context_summary">资料 {{ currentPrecheck.context_summary.knowledge_source_count }} 条</span>
              </div>
            </div>
            <div class="precheck-grid">
              <section><h4>已有优势</h4><ul class="success-list"><li v-for="item in currentPrecheck.strengths || []" :key="item">{{ item }}</li></ul></section>
              <section><h4>待完善问题</h4><ul class="problem-list"><li v-for="item in currentPrecheck.problems || []" :key="item">{{ item }}</li></ul></section>
              <section><h4>下一步行动</h4><ol><li v-for="item in currentPrecheck.next_actions || []" :key="item">{{ item }}</li></ol></section>
            </div>
            <div v-if="currentPrecheck.citations?.length" class="precheck-citations">
              <strong>检查依据</strong><span v-for="item in currentPrecheck.citations" :key="item.chunk_id">{{ item.title }} · {{ item.source_label }}</span>
            </div>
          </template>
          <div v-else class="empty-precheck"><MagicStick /><span>先保存成果草稿，再运行自检定位缺失材料。</span></div>
        </article>
      </main>
      <article v-else class="data-panel empty-project"><el-empty description="暂无可参与项目，请先完成课程选课" /></article>
    </div>
  </section>
</template>

<style scoped>
.stats-strip { display: grid; grid-template-columns: repeat(4, 1fr); margin-bottom: 16px; background: #fff; border: 1px solid var(--ste-border); }
.stats-strip article { display: flex; align-items: baseline; justify-content: space-between; min-height: 78px; padding: 18px 20px; border-right: 1px solid var(--ste-border); }
.stats-strip article:last-child { border-right: 0; }.stats-strip span { color: var(--ste-muted); font-size: 13px; }.stats-strip strong { font-size: 26px; }
.student-workspace { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 16px; align-items: start; }
.project-rail { position: sticky; top: 88px; overflow: hidden; }.project-rail .panel-heading { align-items: center; }
.project-row { display: grid; grid-template-columns: 34px minmax(0, 1fr) 16px; gap: 10px; align-items: center; width: 100%; min-height: 68px; padding: 12px 16px; text-align: left; background: #fff; border: 0; border-top: 1px solid var(--ste-border); cursor: pointer; }
.project-row:hover { background: #f8faff; }.project-row.active { background: var(--ste-primary-soft); box-shadow: inset 3px 0 var(--ste-primary); }
.project-index { color: #8b97aa; font-size: 11px; font-weight: 700; }.project-copy { display: grid; gap: 5px; min-width: 0; }.project-copy strong { overflow: hidden; color: #26344a; font-size: 13px; text-overflow: ellipsis; white-space: nowrap; }.project-copy small { color: var(--ste-muted); font-size: 10px; }
.project-done { color: var(--ste-success); }.task-dot { width: 7px; height: 7px; background: var(--ste-warning); border-radius: 50%; }
.project-main { display: grid; gap: 16px; min-width: 0; }.project-overview { padding: 0 18px 16px; }.project-overview > p { margin: 4px 0 14px; color: #526176; font-size: 13px; line-height: 1.7; }.project-meta { display: flex; flex-wrap: wrap; gap: 8px; color: var(--ste-muted); font-size: 11px; }.project-meta > span { padding: 5px 8px; background: #f3f6fa; border-radius: 4px; }.project-meta .task-chip { color: #a46614; background: #fff6e8; }
.practice-grid { display: grid; grid-template-columns: minmax(430px, .9fr) minmax(420px, 1.1fr); gap: 16px; align-items: stretch; }
.editor-panel, .coach-panel, .precheck-panel { min-width: 0; overflow: hidden; }.achievement-form { padding: 4px 18px 0; }.achievement-form :deep(.el-form-item) { margin-bottom: 15px; }
.upload-row { display: flex; align-items: center; gap: 10px; min-width: 0; }.upload-row a { color: var(--ste-primary); font-size: 12px; text-decoration: none; }.upload-row > span { color: var(--ste-muted); font-size: 11px; }
.editor-actions { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 18px; border-top: 1px solid var(--ste-border); }.editor-actions > span { color: var(--ste-muted); font-size: 11px; }.editor-actions > div { display: flex; gap: 8px; }
.coach-panel { display: grid; grid-template-rows: auto minmax(360px, 1fr) auto; }.coach-panel .panel-heading > svg { width: 20px; color: var(--ste-primary); }.coach-list { max-height: 560px; min-height: 360px; overflow-y: auto; padding: 10px 18px; }
.coach-welcome { display: grid; justify-items: start; gap: 9px; padding: 20px 4px; color: var(--ste-muted); }.coach-welcome > svg { width: 24px; color: var(--ste-primary); }.coach-welcome strong { color: #2c394e; font-size: 14px; }.coach-welcome > span { font-size: 12px; }.coach-welcome button { padding: 8px 10px; color: #3c5d8d; font-size: 11px; text-align: left; background: #f3f7ff; border: 1px solid #e1e9f7; border-radius: 5px; cursor: pointer; }
.coach-message { display: grid; gap: 6px; margin-bottom: 14px; padding: 11px 12px; background: #f6f8fb; border-left: 3px solid #c5d2e6; }.coach-message.user { margin-left: 42px; background: #edf3ff; border-left-color: var(--ste-primary); }.coach-message strong { font-size: 11px; }.coach-message p { margin: 0; color: #46566e; font-size: 12px; line-height: 1.7; white-space: pre-wrap; }
.coach-section > span, .coach-citations small { color: var(--ste-muted); font-size: 10px; }.coach-section ol { margin: 5px 0 0; padding-left: 18px; color: #526176; font-size: 11px; line-height: 1.65; }.next-actions, .coach-citations { display: flex; flex-wrap: wrap; gap: 5px; }.next-actions span { padding: 4px 6px; color: #17674f; font-size: 10px; background: #eaf8f3; border-radius: 4px; }.coach-citations small { width: 100%; }.coach-citations span { color: #3d65a0; font-size: 10px; }
.coach-input { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 8px; align-items: end; padding: 14px 18px; border-top: 1px solid var(--ste-border); }
.precheck-panel { padding-bottom: 16px; }.precheck-summary { display: flex; align-items: center; gap: 12px; padding: 8px 18px 16px; }.precheck-score { display: grid; width: 58px; height: 58px; place-items: center; color: #fff; font-size: 22px; font-weight: 700; background: var(--ste-warning); border-radius: 50%; }.precheck-score.ready { background: var(--ste-success); }.precheck-summary > div:nth-child(2) { display: grid; gap: 4px; }.precheck-summary strong { font-size: 14px; }.precheck-summary span { color: var(--ste-muted); font-size: 11px; }.context-badges { display: flex !important; flex-flow: row wrap; gap: 6px; margin-left: auto; }.context-badges span { padding: 4px 7px; background: #f3f6fa; border-radius: 4px; }
.precheck-grid { display: grid; grid-template-columns: repeat(3, 1fr); border-top: 1px solid var(--ste-border); border-bottom: 1px solid var(--ste-border); }.precheck-grid section { padding: 15px 18px; border-right: 1px solid var(--ste-border); }.precheck-grid section:last-child { border-right: 0; }.precheck-grid h4 { margin: 0 0 8px; font-size: 12px; }.precheck-grid ul, .precheck-grid ol { margin: 0; padding-left: 18px; color: #526176; font-size: 11px; line-height: 1.75; }.success-list li::marker { color: var(--ste-success); }.problem-list li::marker { color: var(--ste-danger); }
.precheck-citations { display: flex; flex-wrap: wrap; gap: 8px; padding: 13px 18px 0; }.precheck-citations strong { width: 100%; font-size: 11px; }.precheck-citations span { color: #3d65a0; font-size: 10px; }.empty-precheck { display: flex; align-items: center; gap: 9px; min-height: 110px; padding: 0 18px; color: var(--ste-muted); font-size: 12px; }.empty-precheck svg { width: 20px; }.empty-project { display: grid; min-height: 520px; place-items: center; }
@media (max-width: 1280px) { .practice-grid { grid-template-columns: 1fr; }.coach-panel { grid-template-rows: auto minmax(280px, auto) auto; }.coach-list { min-height: 280px; } }
@media (max-width: 900px) { .student-workspace { grid-template-columns: 1fr; }.project-rail { position: static; }.precheck-grid { grid-template-columns: 1fr; }.precheck-grid section { border-right: 0; border-bottom: 1px solid var(--ste-border); } }
@media (max-width: 700px) { .stats-strip { grid-template-columns: repeat(2, 1fr); }.stats-strip article:nth-child(2) { border-right: 0; }.editor-actions { align-items: stretch; flex-direction: column; }.editor-actions > div { flex-direction: column; }.coach-input { grid-template-columns: 1fr; }.precheck-summary { align-items: flex-start; flex-wrap: wrap; }.context-badges { width: 100%; margin-left: 0; } }
</style>
