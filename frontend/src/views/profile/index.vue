<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Lock, OfficeBuilding, User } from '@element-plus/icons-vue'
import { useUserStore } from '../../stores/user'
import { roleLabels } from '../../router/route-data'

const userStore = useUserStore()
const formRef = ref()
const form = reactive({ name: userStore.name, department: userStore.department, phone: '138****0862', email: 'user@smarttrain.edu.cn' })
const roleName = computed(() => roleLabels[userStore.role])
const rules = { name: [{ required: true, message: '请输入姓名', trigger: 'blur' }], email: [{ type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }] }
async function saveProfile() { if (await formRef.value.validate().catch(() => false)) { userStore.name = form.name; userStore.department = form.department; userStore.persist(); ElMessage.success('个人资料已保存') } }
function securityInfo(label) { ElMessage.info(`${label}管理待接入账号安全服务`) }
</script>

<template>
  <section class="profile-page">
    <div class="feature-hero"><div><p class="page-eyebrow">ACCOUNT</p><h2>个人中心</h2><p>维护个人资料、登录安全和平台通知偏好。</p></div></div>
    <div class="profile-grid"><article class="data-panel profile-summary"><el-avatar :size="76" class="profile-avatar">{{ userStore.initials }}</el-avatar><h3>{{ userStore.name }}</h3><el-tag effect="plain" type="primary">{{ roleName }}</el-tag><p>{{ userStore.department }}</p><dl><div><dt>完成项目</dt><dd>12</dd></div><div><dt>获得评价</dt><dd>38</dd></div><div><dt>累计学时</dt><dd>126</dd></div></dl></article><article class="data-panel profile-form"><div class="panel-heading"><div><h3>基础资料</h3><span>修改后将同步展示在评价记录中</span></div></div><el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="profile-el-form"><el-form-item label="姓名" prop="name"><el-input v-model="form.name" :prefix-icon="User" /></el-form-item><el-form-item label="所属组织" prop="department"><el-input v-model="form.department" :prefix-icon="OfficeBuilding" /></el-form-item><el-form-item label="手机号码"><el-input v-model="form.phone" /></el-form-item><el-form-item label="电子邮箱" prop="email"><el-input v-model="form.email" /></el-form-item><el-button type="primary" @click="saveProfile">保存资料</el-button></el-form></article><aside class="data-panel profile-security"><div class="panel-heading"><h3>账号安全</h3></div><div class="security-item"><el-icon><Lock /></el-icon><div><strong>登录密码</strong><span>建议定期更换高强度密码</span></div><el-button text type="primary" @click="securityInfo('密码')">修改</el-button></div><div class="security-item"><el-icon><User /></el-icon><div><strong>登录设备</strong><span>当前设备：Windows · 上海</span></div><el-button text type="primary" @click="securityInfo('登录设备')">管理</el-button></div></aside></div>
  </section>
</template>
