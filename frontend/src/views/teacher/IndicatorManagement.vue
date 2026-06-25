<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { listProjects } from '../../api/projects'
import { createIndicator, deleteIndicator, listIndicators, updateIndicator } from '../../api/indicators'

const projects = ref([])
const currentProjectId = ref(null)

const loading = ref(false)
const rows = ref([])

const weightSum = computed(() =>
  rows.value.filter((r) => r.parent_id === 0).reduce((s, r) => s + Number(r.weight), 0),
)

const dialogVisible = ref(false)
const dialogMode = ref('create')
const formRef = ref()
const submitting = ref(false)
const blankForm = () => ({
  id: null, indicator_name: '', indicator_code: '', weight: 0, max_score: 100,
  scoring_rule: '', sort: 0, status: 1,
})
const form = reactive(blankForm())
const rules = {
  indicator_name: [{ required: true, message: '请输入指标名称', trigger: 'blur' }],
  indicator_code: [{ required: true, message: '请输入指标编码', trigger: 'blur' }],
}

async function fetchProjects() {
  const data = await listProjects({ page: 1, page_size: 100 })
  projects.value = data.items
  if (!currentProjectId.value && projects.value.length) {
    currentProjectId.value = projects.value[0].id
  }
}

async function fetchIndicators() {
  if (!currentProjectId.value) { rows.value = []; return }
  loading.value = true
  try {
    const data = await listIndicators({ project_id: currentProjectId.value, page: 1, page_size: 200 })
    rows.value = data.items
  } finally {
    loading.value = false
  }
}

function onProjectChange() {
  fetchIndicators()
}

function openCreate() {
  dialogMode.value = 'create'
  Object.assign(form, blankForm())
  dialogVisible.value = true
}

function openEdit(row) {
  dialogMode.value = 'edit'
  Object.assign(form, blankForm(), {
    id: row.id, indicator_name: row.indicator_name, indicator_code: row.indicator_code,
    weight: Number(row.weight), max_score: Number(row.max_score),
    scoring_rule: row.scoring_rule || '', sort: row.sort, status: row.status,
  })
  dialogVisible.value = true
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await createIndicator({
        project_id: currentProjectId.value, parent_id: 0,
        indicator_name: form.indicator_name, indicator_code: form.indicator_code,
        weight: form.weight, max_score: form.max_score,
        scoring_rule: form.scoring_rule || null, sort: form.sort,
      })
      ElMessage.success('指标已创建')
    } else {
      await updateIndicator(form.id, {
        indicator_name: form.indicator_name, weight: form.weight, max_score: form.max_score,
        scoring_rule: form.scoring_rule || null, sort: form.sort, status: form.status,
      })
      ElMessage.success('指标已更新')
    }
    dialogVisible.value = false
    fetchIndicators()
  } finally {
    submitting.value = false
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除指标「${row.indicator_name}」？`, '删除确认', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
  }).catch(() => Promise.reject('cancel'))
  await deleteIndicator(row.id)
  ElMessage.success('指标已删除')
  fetchIndicators()
}

onMounted(async () => {
  await fetchProjects()
  await fetchIndicators()
})
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">TEACHER · INDICATORS</p>
        <h2>评价指标</h2>
        <p>按项目配置评价指标体系，供 AI 与人工评分使用。</p>
      </div>
      <el-button type="primary" :icon="Plus" :disabled="!currentProjectId" @click="openCreate">新建指标</el-button>
    </div>

    <article class="data-panel">
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="t-label">实训项目</span>
          <el-select v-model="currentProjectId" placeholder="选择项目" style="width: 260px" @change="onProjectChange">
            <el-option v-for="p in projects" :key="p.id" :label="p.project_name" :value="p.id" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-tag :type="weightSum === 100 ? 'success' : 'warning'" effect="plain">
            一级指标权重合计 {{ weightSum }} / 100
          </el-tag>
          <el-button text :icon="Refresh" @click="fetchIndicators" :loading="loading">刷新</el-button>
        </div>
      </div>

      <el-table :data="rows" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="indicator_name" label="指标名称" min-width="140" />
        <el-table-column prop="indicator_code" label="编码" min-width="110" />
        <el-table-column label="权重(%)" width="100">
          <template #default="{ row }">{{ row.weight }}</template>
        </el-table-column>
        <el-table-column label="满分" width="90">
          <template #default="{ row }">{{ row.max_score }}</template>
        </el-table-column>
        <el-table-column label="评分标准" min-width="180">
          <template #default="{ row }">{{ row.scoring_rule || '—' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" effect="plain">
              {{ row.status === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !rows.length" description="该项目暂无评价指标，点击「新建指标」开始配置" />
    </article>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建评价指标' : '编辑评价指标'"
      width="520px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="指标名称" prop="indicator_name">
          <el-input v-model="form.indicator_name" placeholder="如：功能完整性" />
        </el-form-item>
        <el-form-item label="指标编码" prop="indicator_code">
          <el-input v-model="form.indicator_code" :disabled="dialogMode === 'edit'" placeholder="项目内唯一，如 FUNC_1" />
        </el-form-item>
        <el-form-item label="权重(%)">
          <el-input-number v-model="form.weight" :min="0" :max="100" controls-position="right" />
          <span class="form-hint">同级合计应为 100</span>
        </el-form-item>
        <el-form-item label="满分">
          <el-input-number v-model="form.max_score" :min="1" :max="1000" controls-position="right" />
        </el-form-item>
        <el-form-item label="评分标准">
          <el-input v-model="form.scoring_rule" type="textarea" :rows="3" placeholder="供 AI 与人工参考的评分细则" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" controls-position="right" />
        </el-form-item>
        <el-form-item v-if="dialogMode === 'edit'" label="状态">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="启用" inactive-text="停用" />
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
.toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; flex-wrap: wrap; gap: 12px; }
.toolbar-left { display: flex; align-items: center; gap: 10px; }
.toolbar-right { display: flex; align-items: center; gap: 12px; }
.t-label { color: var(--el-text-color-secondary); font-size: 14px; }
.form-hint { margin-left: 10px; color: var(--el-text-color-secondary); font-size: 12px; }
</style>
