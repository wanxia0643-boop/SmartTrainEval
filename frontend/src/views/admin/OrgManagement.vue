<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { createOrg, deleteOrg, listOrgs, updateOrg } from '../../api/orgs'

const ORG_TYPES = [
  { value: 1, label: '学校' },
  { value: 2, label: '学院' },
  { value: 3, label: '专业' },
  { value: 4, label: '班级' },
  { value: 5, label: '企业' },
]
const typeLabel = (v) => ORG_TYPES.find((t) => t.value === v)?.label || '—'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10 })

const dialogVisible = ref(false)
const dialogMode = ref('create')
const formRef = ref()
const submitting = ref(false)
const blankForm = () => ({
  id: null, org_name: '', org_code: '', org_type: 1, parent_id: 0,
  leader: '', contact: '', sort: 0, status: 1,
})
const form = reactive(blankForm())

const rules = {
  org_name: [{ required: true, message: '请输入组织名称', trigger: 'blur' }],
  org_code: [{ required: true, message: '请输入组织编码', trigger: 'blur' }],
  org_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
}

async function fetchOrgs() {
  loading.value = true
  try {
    const data = await listOrgs({ page: query.page, page_size: query.page_size })
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
    id: row.id, org_name: row.org_name, org_code: row.org_code, org_type: row.org_type,
    parent_id: row.parent_id, leader: row.leader || '', contact: row.contact || '',
    sort: row.sort, status: row.status,
  })
  dialogVisible.value = true
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await createOrg({
        org_name: form.org_name, org_code: form.org_code, org_type: form.org_type,
        parent_id: form.parent_id, leader: form.leader || null, contact: form.contact || null,
        sort: form.sort,
      })
      ElMessage.success('组织已创建')
    } else {
      await updateOrg(form.id, {
        org_name: form.org_name, org_type: form.org_type, parent_id: form.parent_id,
        leader: form.leader || null, contact: form.contact || null, sort: form.sort, status: form.status,
      })
      ElMessage.success('组织已更新')
    }
    dialogVisible.value = false
    fetchOrgs()
  } finally {
    submitting.value = false
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除组织「${row.org_name}」？`, '删除确认', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
  }).catch(() => Promise.reject('cancel'))
  await deleteOrg(row.id)
  ElMessage.success('组织已删除')
  if (rows.value.length === 1 && query.page > 1) query.page -= 1
  fetchOrgs()
}

function handlePageChange(page) {
  query.page = page
  fetchOrgs()
}

onMounted(fetchOrgs)
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">SYSTEM · ORG</p>
        <h2>组织架构</h2>
        <p>配置院校、企业、院系与班级层级。</p>
      </div>
      <div class="hero-actions">
        <el-button :icon="Refresh" @click="fetchOrgs" :loading="loading">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建组织</el-button>
      </div>
    </div>

    <article class="data-panel">
      <el-table :data="rows" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="org_name" label="名称" min-width="140" />
        <el-table-column prop="org_code" label="编码" min-width="120" />
        <el-table-column label="类型" width="90">
          <template #default="{ row }">
            <el-tag effect="plain">{{ typeLabel(row.org_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="parent_id" label="上级ID" width="90" />
        <el-table-column label="负责人" min-width="100">
          <template #default="{ row }">{{ row.leader || '—' }}</template>
        </el-table-column>
        <el-table-column label="联系电话" min-width="120">
          <template #default="{ row }">{{ row.contact || '—' }}</template>
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
      :title="dialogMode === 'create' ? '新建组织' : '编辑组织'"
      width="520px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="名称" prop="org_name">
          <el-input v-model="form.org_name" placeholder="组织名称" />
        </el-form-item>
        <el-form-item label="编码" prop="org_code">
          <el-input v-model="form.org_code" :disabled="dialogMode === 'edit'" placeholder="唯一编码" />
        </el-form-item>
        <el-form-item label="类型" prop="org_type">
          <el-select v-model="form.org_type" style="width: 100%">
            <el-option v-for="t in ORG_TYPES" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="上级ID">
          <el-input-number v-model="form.parent_id" :min="0" controls-position="right" />
          <span class="form-hint">0 表示顶级</span>
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="form.leader" placeholder="选填" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact" placeholder="选填" />
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
.hero-actions { display: flex; gap: 12px; }
.table-pager { display: flex; justify-content: flex-end; margin-top: 16px; }
.form-hint { margin-left: 10px; color: var(--el-text-color-secondary); font-size: 12px; }
</style>
