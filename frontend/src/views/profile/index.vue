<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Lock, OfficeBuilding, User, Message as MessageIcon } from '@element-plus/icons-vue'
import { useUserStore } from '../../stores/user'
import { roleLabels } from '../../router/route-data'
import { getProfile, updateProfile } from '../../api/auth'
import { listOrgs } from '../../api/orgs'

const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const saving = ref(false)
const orgs = ref([])

const form = reactive({
  real_name: '',
  email: '',
  phone: '',
})

const rules = {
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }],
}

const roleName = computed(() => roleLabels[userStore.role])
const orgName = computed(() => {
  const org = orgs.value.find((o) => o.id === userStore.orgId)
  return org?.org_name || '未分配'
})

async function loadProfile() {
  loading.value = true
  try {
    const profile = await getProfile()
    form.real_name = profile.real_name || ''
    form.email = profile.email || ''
    form.phone = profile.phone || ''
    // 同步到 store
    userStore.name = profile.real_name || userStore.name
    userStore.email = profile.email || ''
    userStore.phone = profile.phone || ''
    userStore.orgId = profile.org_id || null
    userStore.studentNo = profile.student_no || ''
    userStore.persist()
  } catch (e) {
    ElMessage.error('获取个人资料失败')
  } finally {
    loading.value = false
  }
}

async function loadOrgs() {
  try {
    const data = await listOrgs({ page: 1, page_size: 100 })
    orgs.value = data.items || []
  } catch {
    orgs.value = []
  }
}

async function saveProfile() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    await updateProfile({
      real_name: form.real_name,
      email: form.email || null,
      phone: form.phone || null,
    })
    // 同步到 store
    userStore.name = form.real_name
    userStore.email = form.email || ''
    userStore.phone = form.phone || ''
    userStore.persist()
    ElMessage.success('个人资料已保存')
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

function securityInfo(label) {
  ElMessage.info(`${label}管理功能待接入账号安全服务`)
}

onMounted(async () => {
  await Promise.all([loadProfile(), loadOrgs()])
})
</script>

<template>
  <section class="profile-page" v-loading="loading">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">ACCOUNT</p>
        <h2>个人中心</h2>
        <p>维护个人资料、登录安全和平台通知偏好。</p>
      </div>
    </div>

    <div class="profile-grid">
      <!-- 用户摘要卡片 -->
      <article class="data-panel profile-summary">
        <el-avatar :size="76" class="profile-avatar">{{ userStore.initials }}</el-avatar>
        <h3>{{ userStore.name }}</h3>
        <el-tag effect="plain" type="primary">{{ roleName }}</el-tag>
        <p class="org-text">{{ orgName }}</p>
        <dl class="profile-stats">
          <div>
            <dt>账号</dt>
            <dd>{{ userStore.username }}</dd>
          </div>
          <div v-if="userStore.studentNo">
            <dt>学号/工号</dt>
            <dd>{{ userStore.studentNo }}</dd>
          </div>
          <div>
            <dt>邮箱</dt>
            <dd>{{ userStore.email || '未设置' }}</dd>
          </div>
        </dl>
      </article>

      <!-- 基础资料表单 -->
      <article class="data-panel profile-form">
        <div class="panel-heading">
          <div>
            <h3>基础资料</h3>
            <span>修改后将同步展示在评价记录中</span>
          </div>
        </div>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="profile-el-form"
        >
          <el-form-item label="姓名" prop="real_name">
            <el-input v-model="form.real_name" :prefix-icon="User" placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="所属组织">
            <el-input :model-value="orgName" :prefix-icon="OfficeBuilding" disabled />
          </el-form-item>
          <el-form-item label="手机号码">
            <el-input v-model="form.phone" placeholder="请输入手机号码" />
          </el-form-item>
          <el-form-item label="电子邮箱" prop="email">
            <el-input v-model="form.email" :prefix-icon="MessageIcon" placeholder="请输入邮箱地址" />
          </el-form-item>
          <el-button type="primary" :loading="saving" @click="saveProfile">保存资料</el-button>
        </el-form>
      </article>

      <!-- 账号安全 -->
      <aside class="data-panel profile-security">
        <div class="panel-heading">
          <h3>账号安全</h3>
        </div>
        <div class="security-item">
          <el-icon><Lock /></el-icon>
          <div>
            <strong>登录密码</strong>
            <span>建议定期更换高强度密码</span>
          </div>
          <el-button text type="primary" @click="securityInfo('密码')">修改</el-button>
        </div>
        <div class="security-item">
          <el-icon><User /></el-icon>
          <div>
            <strong>登录设备</strong>
            <span>当前设备：Windows · 上海</span>
          </div>
          <el-button text type="primary" @click="securityInfo('登录设备')">管理</el-button>
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.profile-page {
  max-width: 1200px;
  margin: 0 auto;
}

.profile-grid {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 20px;
  margin-top: 20px;
}

@media (max-width: 1100px) {
  .profile-grid {
    grid-template-columns: 1fr 1fr;
  }
  .profile-security {
    grid-column: 1 / -1;
  }
}

@media (max-width: 700px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

.profile-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 28px 20px;
}

.profile-avatar {
  background: var(--el-color-primary);
  color: #fff;
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 14px;
}

.profile-summary h3 {
  margin: 0 0 10px;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.org-text {
  margin: 8px 0 16px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.profile-stats {
  width: 100%;
  margin: 0;
  padding: 0;
  border-top: 1px solid var(--el-border-color-lighter);
  padding-top: 14px;
}

.profile-stats div {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
}

.profile-stats dt {
  color: var(--el-text-color-secondary);
}

.profile-stats dd {
  margin: 0;
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.profile-form {
  padding: 24px;
}

.panel-heading {
  margin-bottom: 20px;
}

.panel-heading h3 {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.panel-heading span {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.profile-el-form {
  max-width: 420px;
}

.profile-security {
  padding: 24px;
}

.security-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.security-item:last-child {
  border-bottom: none;
}

.security-item .el-icon {
  font-size: 20px;
  color: var(--el-text-color-secondary);
}

.security-item div {
  flex: 1;
  min-width: 0;
}

.security-item strong {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 2px;
}

.security-item span {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
