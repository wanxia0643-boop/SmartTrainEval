import {
  Briefcase, CollectionTag, DataAnalysis, DocumentChecked, FolderChecked,
  Monitor, OfficeBuilding, Reading, School, Setting, User, UserFilled,
} from '@element-plus/icons-vue'
import Dashboard from '../views/dashboard/index.vue'
import FeatureView from '../views/common/FeatureView.vue'
import Profile from '../views/profile/index.vue'
import UserManagement from '../views/admin/UserManagement.vue'

export const roleLabels = {
  student: '学生', teacher: '教师', enterprise: '企业导师', admin: '系统管理员',
}

export const roleCredentials = {
  student: { account: 'student', password: '123456', name: '林晓', department: '软件工程 2024 级' },
  teacher: { account: 'teacher', password: '123456', name: '张老师', department: '软件工程学院' },
  enterprise: { account: 'enterprise', password: '123456', name: '陈导师', department: '智云科技有限公司' },
  admin: { account: 'admin', password: '123456', name: '系统管理员', department: '智训评运营中心' },
}

const dashboard = {
  path: 'dashboard', name: 'dashboard', component: Dashboard,
  meta: { title: '工作台', icon: Monitor, roles: ['student', 'teacher', 'enterprise', 'admin'] },
}

const feature = (path, title, icon, roles, description) => ({
  path, name: path, component: FeatureView, props: { title, description },
  meta: { title, icon, roles },
})

export const protectedRoutes = [
  dashboard,
  feature('training', '实训中心', Reading, ['student'], '集中管理实训课程、项目与学习资源。'),
  feature('my-evaluation', '评价反馈', DocumentChecked, ['student'], '查看导师、同伴与 AI 评价的完整反馈。'),
  feature('growth', '成长档案', CollectionTag, ['student'], '沉淀能力图谱、学习轨迹与荣誉成果。'),
  feature('training-management', '实训管理', FolderChecked, ['teacher'], '管理实训项目、班级安排与阶段任务。'),
  feature('intelligent-evaluation', '智能评价', DocumentChecked, ['teacher'], '快速处理 AI 初评后的人工复核任务。'),
  feature('student-archive', '学生档案', UserFilled, ['teacher'], '查看学生能力证据与成长变化。'),
  feature('data-report', '数据报表', DataAnalysis, ['teacher', 'admin'], '分析评价进度、能力分布与质量趋势。'),
  feature('project-training', '项目实训', Briefcase, ['enterprise'], '跟进企业项目中的实训进度与实践产出。'),
  feature('talent-evaluation', '人才评价', DocumentChecked, ['enterprise'], '筛选实训表现，形成企业人才评价。'),
  feature('enterprise-mentor', '企业导师', UserFilled, ['enterprise'], '协同企业导师处理指导与反馈事项。'),
  feature('partner-schools', '合作院校', School, ['enterprise'], '维护合作院校与实训项目关系。'),
  feature('organization', '组织架构', OfficeBuilding, ['admin'], '配置院校、企业、院系与班级层级。'),
  {
    path: 'user-management', name: 'user-management', component: UserManagement,
    meta: { title: '用户管理', icon: User, roles: ['admin'] },
  },
  feature('system-settings', '系统设置', Setting, ['admin'], '配置评价规则、通知与系统基础参数。'),
  {
    path: 'profile', name: 'profile', component: Profile,
    meta: { title: '个人中心', icon: User, roles: ['student', 'teacher', 'enterprise', 'admin'], hidden: true },
  },
]

export const getAccessibleRoutes = (role) => protectedRoutes.filter((route) => route.meta.roles.includes(role))
export const getMenuRoutes = (role) => getAccessibleRoutes(role).filter((route) => !route.meta.hidden)
