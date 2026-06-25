<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { listProjects } from '../../api/projects'
import { createAchievement, listAchievements, updateAchievement } from '../../api/achievements'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

const DIFFICULTY = { 1: '初级', 2: '中级', 3: '高级' }
const PROJ_STATUS = { 0: '未开始', 1: '进行中', 2: '已结束', 3: '已归档' }
const ACH_STATUS = { 0: '草稿', 1: '已提交', 2: '评价中', 3: '已评价', 4: '退回重做' }
const ACH_TAG = { 0: 'info', 1: 'primary', 2: 'warning', 3: 'success', 4: 'danger' }

const projects = ref([])
const projLoading = ref(false)
const achievements = ref([])
const achLoading = ref(false)

const dialogVisible = ref(false)
const dialogMode = ref('create')
const formRef = ref()
const submitting = ref(false)
const blankForm = () => ({ id: null, project_id: null, title: '', content: '', repo_url: '', attachment_url: '' })
const form = reactive(blankForm())
const rules = {
  project_id: [{ required: true, message: '请选择实训项目', trigger: 'change' }],
  title: [{ required: true, message: '请输入成果标题', trigger: 'blur' }],
}

async function fetchProjects() {
  projLoading.value = true
  try {
    const data = await listProjects({ page: 1, page_size: 100 })
    projects.value = data.items
  } finally {
    projLoading.value = false
  }
}

async function fetchAchievements() {
  achLoading.value = true
  try {
    const data = await listAchievements({ student_id: userStore.userId, page: 1, page_size: 100 })
    achievements.value = data.items
  } finally {
    achLoading.value = false
  }
}

function openCreate() {
  dialogMode.value = 'create'
  Object.assign(form, blankForm())
  dialogVisible.value = true
}

function openEdit(row) {
  dialogMode.value = 'edit'
  Object.assign(form, blankForm(), {
    id: row.id, project_id: row.project_id, title: row.title,
    content: row.content || '', repo_url: row.repo_url || '', attachment_url: row.attachment_url || '',
  })
  dialogVisible.value = true
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await createAchievement({
        project_id: form.project_id, student_id: userStore.userId, title: form.title,
        content: form.content || null, repo_url: form.repo_url || null,
        attachment_url: form.attachment_url || null,
      })
      ElMessage.success('成果已提交')
    } else {
      await updateAchievement(form.id, {
        title: form.title, content: form.content || null,
        repo_url: form.repo_url || null, attachment_url: form.attachment_url || null,
      })
      ElMessage.success('成果已更新')
    }
    dialogVisible.value = false
    fetchAchievements()
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await fetchProjects()
  await fetchAchievements()
})
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">STUDENT · TRAINING</p>
        <h2>实训中心</h2>
        <p>查看实训项目，提交并管理你的实训成果。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreate">提交成果</el-button>
    </div>

    <article class="data-panel">
      <div class="panel-head"><strong>可参与的实训项目</strong>
        <el-button text :icon="Refresh" @click="fetchProjects" :loading="projLoading">刷新</el-button>
      </div>
      <el-table :data="projects" v-loading="projLoading" stripe style="width: 100%">
        <el-table-column prop="project_name" label="项目名称" min-width="160" />
        <el-table-column prop="project_code" label="编码" min-width="120" />
        <el-table-column label="难度" width="80">
          <template #default="{ row }">{{ DIFFICULTY[row.difficulty] || '—' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag effect="plain">{{ PROJ_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </article>

    <article class="data-panel">
      <div class="panel-head"><strong>我的实训成果</strong>
        <el-button text :icon="Refresh" @click="fetchAchievements" :loading="achLoading">刷新</el-button>
      </div>
      <el-table :data="achievements" v-loading="achLoading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="成果标题" min-width="180" />
        <el-table-column prop="project_id" label="项目ID" width="90" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="ACH_TAG[row.status]" effect="plain">{{ ACH_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最终得分" width="100">
          <template #default="{ row }">{{ row.final_score ?? '—' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" :disabled="row.status === 3" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!achLoading && !achievements.length" description="还没有提交成果" />
    </article>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '提交实训成果' : '编辑实训成果'"
      width="560px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="实训项目" prop="project_id">
          <el-select v-model="form.project_id" :disabled="dialogMode === 'edit'" placeholder="选择项目" style="width: 100%">
            <el-option v-for="p in projects" :key="p.id" :label="p.project_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="成果标题" prop="title">
          <el-input v-model="form.title" placeholder="如：电商系统后端实现" />
        </el-form-item>
        <el-form-item label="代码仓库">
          <el-input v-model="form.repo_url" placeholder="选填，Git 仓库地址" />
        </el-form-item>
        <el-form-item label="附件地址">
          <el-input v-model="form.attachment_url" placeholder="选填，文档/压缩包链接" />
        </el-form-item>
        <el-form-item label="成果说明">
          <el-input v-model="form.content" type="textarea" :rows="5" placeholder="实训报告 / 代码说明…" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">确定</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.panel-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.panel-head strong { font-size: 15px; }
.data-panel + .data-panel { margin-top: 16px; }
</style>
