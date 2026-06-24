<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { createReport, deleteReport, listReports } from '../../api/reports'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

const REPORT_TYPES = [
  { value: 1, label: '学生成绩报表' },
  { value: 2, label: '项目评价报表' },
  { value: 3, label: '组织汇总报表' },
  { value: 4, label: 'AI使用统计报表' },
]
const typeLabel = (v) => REPORT_TYPES.find((t) => t.value === v)?.label || '—'
const STATUS = { 0: '生成中', 1: '成功', 2: '失败' }
const STATUS_TAG = { 0: 'warning', 1: 'success', 2: 'danger' }

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10 })

const dialogVisible = ref(false)
const formRef = ref()
const submitting = ref(false)
const blankForm = () => ({ report_name: '', report_type: 1, project_id: null, file_format: 'PDF' })
const form = reactive(blankForm())
const rules = {
  report_name: [{ required: true, message: '请输入报表名称', trigger: 'blur' }],
}

async function fetchReports() {
  loading.value = true
  try {
    const data = await listReports({ page: query.page, page_size: query.page_size })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, blankForm())
  dialogVisible.value = true
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await createReport({
      report_name: form.report_name, report_type: form.report_type,
      project_id: form.project_id || null, file_format: form.file_format,
      generator_id: userStore.userId,
    })
    ElMessage.success('报表已生成')
    dialogVisible.value = false
    fetchReports()
  } finally {
    submitting.value = false
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除报表「${row.report_name}」？`, '删除确认', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
  }).catch(() => Promise.reject('cancel'))
  await deleteReport(row.id)
  ElMessage.success('报表已删除')
  if (rows.value.length === 1 && query.page > 1) query.page -= 1
  fetchReports()
}

function handlePageChange(page) {
  query.page = page
  fetchReports()
}

onMounted(fetchReports)
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">REPORTS</p>
        <h2>数据报表</h2>
        <p>分析评价进度、能力分布与质量趋势。</p>
      </div>
      <div class="hero-actions">
        <el-button :icon="Refresh" @click="fetchReports" :loading="loading">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">生成报表</el-button>
      </div>
    </div>

    <article class="data-panel">
      <el-table :data="rows" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="report_name" label="报表名称" min-width="160" />
        <el-table-column label="类型" min-width="130">
          <template #default="{ row }">{{ typeLabel(row.report_type) }}</template>
        </el-table-column>
        <el-table-column prop="file_format" label="格式" width="90" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="STATUS_TAG[row.status]" effect="plain">{{ STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
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

    <el-dialog v-model="dialogVisible" title="生成报表" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="报表名称" prop="report_name">
          <el-input v-model="form.report_name" placeholder="报表名称" />
        </el-form-item>
        <el-form-item label="报表类型">
          <el-select v-model="form.report_type" style="width: 100%">
            <el-option v-for="t in REPORT_TYPES" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联项目ID">
          <el-input-number v-model="form.project_id" :min="1" controls-position="right" placeholder="选填" />
        </el-form-item>
        <el-form-item label="文件格式">
          <el-select v-model="form.file_format" style="width: 100%">
            <el-option label="PDF" value="PDF" />
            <el-option label="EXCEL" value="EXCEL" />
            <el-option label="WORD" value="WORD" />
          </el-select>
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
