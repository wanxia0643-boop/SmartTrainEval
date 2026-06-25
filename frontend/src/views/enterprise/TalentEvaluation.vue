<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { listAchievements } from '../../api/achievements'
import { listIndicators } from '../../api/indicators'
import { createEvalResult } from '../../api/evalResults'

const ACH_STATUS = { 0: '草稿', 1: '已提交', 2: '评价中', 3: '已评价', 4: '退回重做' }
const ACH_TAG = { 0: 'info', 1: 'primary', 2: 'warning', 3: 'success', 4: 'danger' }

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10

const dialogVisible = ref(false)
const formRef = ref()
const submitting = ref(false)
const indicators = ref([])
const indLoading = ref(false)
const currentAch = ref(null)
const blankForm = () => ({ indicator_id: null, score: 80, comment: '', suggestion: '' })
const form = reactive(blankForm())
const rules = {
  indicator_id: [{ required: true, message: '请选择评价指标', trigger: 'change' }],
  score: [{ required: true, message: '请输入得分', trigger: 'blur' }],
}

async function fetchAchievements() {
  loading.value = true
  try {
    const data = await listAchievements({ page: page.value, page_size: pageSize })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function openEvaluate(row) {
  currentAch.value = row
  Object.assign(form, blankForm())
  dialogVisible.value = true
  indLoading.value = true
  try {
    const data = await listIndicators({ project_id: row.project_id, page: 1, page_size: 100 })
    indicators.value = data.items
  } finally {
    indLoading.value = false
  }
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await createEvalResult({
      achievement_id: currentAch.value.id,
      indicator_id: form.indicator_id,
      eval_type: 3, // 企业导师评价
      score: form.score,
      comment: form.comment || null,
      suggestion: form.suggestion || null,
    })
    ElMessage.success('评价已提交')
    dialogVisible.value = false
    fetchAchievements()
  } finally {
    submitting.value = false
  }
}

function handlePageChange(p) {
  page.value = p
  fetchAchievements()
}

onMounted(fetchAchievements)
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">ENTERPRISE · TALENT</p>
        <h2>人才评价</h2>
        <p>基于实训表现，形成企业侧人才评价。</p>
      </div>
      <el-button :icon="Refresh" @click="fetchAchievements" :loading="loading">刷新</el-button>
    </div>

    <article class="data-panel">
      <el-table :data="rows" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="成果标题" min-width="180" />
        <el-table-column prop="student_id" label="学生ID" width="90" />
        <el-table-column prop="project_id" label="项目ID" width="90" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="ACH_TAG[row.status]" effect="plain">{{ ACH_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="得分" width="90">
          <template #default="{ row }">{{ row.final_score ?? '—' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openEvaluate(row)">评价</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-pager">
        <el-pagination background layout="total, prev, pager, next" :total="total"
          :current-page="page" :page-size="pageSize" @current-change="handlePageChange" />
      </div>
    </article>

    <el-dialog v-model="dialogVisible" :title="`评价：${currentAch?.title || ''}`" width="520px">
      <div v-if="!indLoading && !indicators.length" class="ind-hint">
        当前项目尚未配置评价指标，请先由教师在评价指标中配置后再进行评价。
      </div>
      <el-form v-else ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="评价指标" prop="indicator_id">
          <el-select v-model="form.indicator_id" :loading="indLoading" placeholder="选择指标" style="width: 100%">
            <el-option v-for="i in indicators" :key="i.id"
              :label="`${i.indicator_name}（满分 ${i.max_score}）`" :value="i.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="得分" prop="score">
          <el-input-number v-model="form.score" :min="0" :max="100" controls-position="right" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="form.comment" type="textarea" :rows="3" placeholder="对成果表现的评价" />
        </el-form-item>
        <el-form-item label="改进建议">
          <el-input v-model="form.suggestion" type="textarea" :rows="3" placeholder="对学生的改进建议" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" :disabled="!indicators.length" @click="submit">提交评价</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.table-pager { display: flex; justify-content: flex-end; margin-top: 16px; }
.ind-hint { padding: 16px; color: var(--el-color-warning); background: var(--el-color-warning-light-9); border-radius: 8px; }
</style>
