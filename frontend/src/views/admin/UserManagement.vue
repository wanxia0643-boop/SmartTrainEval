<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { createUser, deleteUser, listUsers, updateUser } from '../../api/users'
import { listRoles } from '../../api/roles'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10 })
const roles = ref([])

const roleMap = computed(() => Object.fromEntries(roles.value.map((r) => [r.id, r.role_name])))
const genderText = (g) => ({ 0: '未知', 1: '男', 2: '女' }[g] ?? '未知')

const dialogVisible = ref(false)
const dialogMode = ref('create') // create | edit
const formRef = ref()
const submitting = ref(false)
const blankForm = () => ({
  id: null, username: '', password: '', real_name: '', role_id: null,
  email: '', phone: '', gender: 0, student_no: '', status: 1,
})
const form = reactive(blankForm())

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少 6 位', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role_id: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

async function fetchRoles() {
  roles.value = await listRoles()
}

async function fetchUsers() {
  loading.value = true
  try {
    const data = await listUsers({ page: query.page, page_size: query.page_size })
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
    id: row.id, username: row.username, real_name: row.real_name, role_id: row.role_id,
    email: row.email || '', phone: row.phone || '', gender: row.gender, status: row.status,
  })
  dialogVisible.value = true
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await createUser({
        username: form.username, password: form.password, real_name: form.real_name,
        role_id: form.role_id, email: form.email || null, phone: form.phone || null,
        gender: form.gender, student_no: form.student_no || null,
      })
      ElMessage.success('用户已创建')
    } else {
      await updateUser(form.id, {
        real_name: form.real_name, role_id: form.role_id, email: form.email || null,
        phone: form.phone || null, status: form.status,
      })
      ElMessage.success('用户已更新')
    }
    dialogVisible.value = false
    fetchUsers()
  } finally {
    submitting.value = false
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除用户「${row.real_name}（${row.username}）」？`, '删除确认', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
  }).catch(() => Promise.reject('cancel'))
  await deleteUser(row.id)
  ElMessage.success('用户已删除')
  if (rows.value.length === 1 && query.page > 1) query.page -= 1
  fetchUsers()
}

function handlePageChange(page) {
  query.page = page
  fetchUsers()
}

onMounted(async () => {
  await fetchRoles()
  await fetchUsers()
})
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">SYSTEM · USERS</p>
        <h2>用户管理</h2>
        <p>统一维护平台用户、角色与账号状态。</p>
      </div>
      <div class="hero-actions">
        <el-button :icon="Refresh" @click="fetchUsers" :loading="loading">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建用户</el-button>
      </div>
    </div>

    <article class="data-panel">
      <el-table :data="rows" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="账号" min-width="120" />
        <el-table-column prop="real_name" label="姓名" min-width="100" />
        <el-table-column label="角色" min-width="110">
          <template #default="{ row }">
            <el-tag effect="plain">{{ roleMap[row.role_id] || '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="性别" width="80">
          <template #default="{ row }">{{ genderText(row.gender) }}</template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" min-width="120">
          <template #default="{ row }">{{ row.phone || '—' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" effect="plain">
              {{ row.status === 1 ? '正常' : '禁用' }}
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
      :title="dialogMode === 'create' ? '新建用户' : '编辑用户'"
      width="520px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="账号" prop="username">
          <el-input v-model="form.username" :disabled="dialogMode === 'edit'" placeholder="登录账号" />
        </el-form-item>
        <el-form-item v-if="dialogMode === 'create'" label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="初始密码（≥6位）" />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="form.role_id" placeholder="请选择角色" style="width: 100%">
            <el-option v-for="r in roles" :key="r.id" :label="r.role_name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio :value="0">未知</el-radio>
            <el-radio :value="1">男</el-radio>
            <el-radio :value="2">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="选填" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="选填" />
        </el-form-item>
        <el-form-item v-if="dialogMode === 'edit'" label="状态">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="正常" inactive-text="禁用" />
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
