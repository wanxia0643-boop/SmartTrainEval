<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { createProject, deleteProject, listProjects, updateProject } from '../../api/projects'
import { listOrgs } from '../../api/orgs'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

const DIFFICULTY = { 1: '初级', 2: '中级', 3: '高级' }
const STATUS = { 0: '未开始', 1: '进行中', 2: '已结束', 3: '已归档' }
const STATUS_TAG = { 0: 'info', 1: 'primary', 2: 'success', 3: 'warning' }

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10 })
const orgs = ref([])

const dialogVisible = ref(false)
const dialogMode = ref('create')
const formRef = ref()
const submitting = ref(false)
const blankForm = () => ({
  id: null, project_name: '', project_code: '', org_id: null, category: '',
  difficulty: 2, description: '', start_time: '', end_time: '', status: 0,
})
const form = reactive(blankForm())

const rules = {
  project_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  project_code: [{ required: true, message: '请输入项目编码', trigger: 'blur' }],
}

async function fetchOrgs() {
  const data = await listOrgs({ page: 1, page_size: 100 })
  orgs.value = data.items
}

async function fetchProjects() {
  loading.value = true
  try {
    const data = await listProjects({ page: query.page, page_size: query.page_size })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
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
    id: row.id, project_name: row.project_name, project_code: row.project_code,
    org_id: row.org_id, category: row.category || '', difficulty: row.difficulty,
    description: row.description || '', start_time: row.start_time || '',
    end_time: row.end_time || '', status: row.status,
  })
  dialogVisible.value = true
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await createProject({
        project_name: form.project_name, project_code: form.project_code,
        org_id: form.org_id, teacher_id: userStore.userId, category: form.category || null,
        difficulty: form.difficulty, description: form.description || null,
        start_time: form.start_time || null, end_time: form.end_time || null,
      })
      ElMessage.success('项目已创建')
    } else {
      await updateProject(form.id, {
        project_name: form.project_name, org_id: form.org_id, category: form.category || null,
        difficulty: form.difficulty, description: form.description || null,
        start_time: form.start_time || null, end_time: form.end_time || null, status: form.status,
      })
      ElMessage.success('项目已更新')
    }
    dialogVisible.value = false
    fetchProjects()
  } finally {
    submitting.value = false
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除项目「${row.project_name}」？`, '删除确认', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
  }).catch(() => Promise.reject('cancel'))
  await deleteProject(row.id)
  ElMessage.success('项目已删除')
  if (rows.value.length === 1 && query.page > 1) query.page -= 1
  fetchProjects()
}

function handlePageChange(page) {
  query.page = page
  fetchProjects()
}

onMounted(async () => {
  await fetchOrgs()
  await fetchProjects()
})
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">TEACHER · PROJECTS</p>
        <h2>实训管理</h2>
        <p>管理实训项目、班级安排与阶段任务。</p>
      </div>
      <div class="hero-actions">
        <el-button :icon="Refresh" @click="fetchProjects" :loading="loading">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建项目</el-button>
      </div>
    </div>

    <article class="data-panel">
      <el-table :data="rows" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="project_name" label="项目名称" min-width="160" />
        <el-table-column prop="project_code" label="编码" min-width="120" />
        <el-table-column label="类别" min-width="100">
          <template #default="{ row }">{{ row.category || '—' }}</template>
        </el-table-column>
        <el-table-column label="难度" width="80">
          <template #default="{ row }">{{ DIFFICULTY[row.difficulty] || '—' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="STATUS_TAG[row.status]" effect="plain">{{ STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-pager">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          :current-page="query.page"
          :page-size="query.page_size"
          @current-change="handlePageChange"
        />
      </div>
    </article>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建项目' : '编辑项目'"
      width="560px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="项目名称" prop="project_name">
          <el-input v-model="form.project_name" placeholder="项目名称" />
        </el-form-item>
        <el-form-item label="项目编码" prop="project_code">
          <el-input v-model="form.project_code" :disabled="dialogMode === 'edit'" placeholder="唯一编码" />
        </el-form-item>
        <el-form-item label="归属组织">
          <el-select v-model="form.org_id" clearable placeholder="选填" style="width: 100%">
            <el-option v-for="o in orgs" :key="o.id" :label="o.org_name" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="类别">
          <el-input v-model="form.category" placeholder="如：软件开发 / 数据分析" />
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="form.difficulty" style="width: 100%">
            <el-option :value="1" label="初级" />
            <el-option :value="2" label="中级" />
            <el-option :value="3" label="高级" />
          </el-select>
        </el-form-item>
        <el-form-item label="起止时间">
          <el-date-picker
            v-model="form.start_time" type="datetime" placeholder="开始时间"
            value-format="YYYY-MM-DDTHH:mm:ss" style="width: 47%"
          />
          <span style="margin: 0 6px">~</span>
          <el-date-picker
            v-model="form.end_time" type="datetime" placeholder="结束时间"
            value-format="YYYY-MM-DDTHH:mm:ss" style="width: 47%"
          />
        </el-form-item>
        <el-form-item v-if="dialogMode === 'edit'" label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option :value="0" label="未开始" />
            <el-option :value="1" label="进行中" />
            <el-option :value="2" label="已结束" />
            <el-option :value="3" label="已归档" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="实训要求与说明" />
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
.hero-actions { display: flex; gap: 12px; }
.table-pager { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
