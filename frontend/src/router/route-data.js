import {
  Briefcase, CollectionTag, DataAnalysis, DocumentChecked, FolderChecked,
  Histogram, Monitor, OfficeBuilding, Reading, School, Setting, User, UserFilled,
} from '@element-plus/icons-vue'
import Dashboard from '../views/dashboard/index.vue'
import Profile from '../views/profile/index.vue'
import UserManagement from '../views/admin/UserManagement.vue'
import OrgManagement from '../views/admin/OrgManagement.vue'
import TrainingManagement from '../views/teacher/TrainingManagement.vue'
import StudentArchive from '../views/teacher/StudentArchive.vue'
import IntelligentEvaluation from '../views/teacher/IntelligentEvaluation.vue'
import DataReport from '../views/teacher/DataReport.vue'
import TrainingReportScreen from '../views/report/TrainingReportScreen.vue'
import IndicatorManagement from '../views/teacher/IndicatorManagement.vue'
import CourseManagement from '../views/teacher/CourseManagement.vue'
import TrainingCenter from '../views/student/TrainingCenter.vue'
import MyEvaluation from '../views/student/MyEvaluation.vue'
import GrowthArchive from '../views/student/GrowthArchive.vue'
import StudentCourseManagement from '../views/student/StudentCourseManagement.vue'
import ProjectTraining from '../views/enterprise/ProjectTraining.vue'
import TalentEvaluation from '../views/enterprise/TalentEvaluation.vue'
import EnterpriseMentor from '../views/enterprise/EnterpriseMentor.vue'
import PartnerSchools from '../views/enterprise/PartnerSchools.vue'
import SystemSettings from '../views/admin/SystemSettings.vue'

export const roleLabels = {
  student: '学生',
  teacher: '教师',
  enterprise: '企业导师',
  admin: '系统管理员',
}

export const roleCredentials = {
  student: { account: 'student', password: '123456', name: '林晓', department: '软件工程 2024 级' },
  teacher: { account: 'teacher', password: '123456', name: '张老师', department: '软件工程学院' },
  enterprise: { account: 'enterprise', password: '123456', name: '陈导师', department: '龙芯中科技术股份有限公司' },
  admin: { account: 'admin', password: '123456', name: '系统管理员', department: '智训评运营中心' },
}

const dashboard = {
  path: 'dashboard',
  name: 'dashboard',
  component: Dashboard,
  meta: { title: '工作台', icon: Monitor, roles: ['student', 'teacher', 'enterprise', 'admin'] },
}

export const protectedRoutes = [
  dashboard,
  {
    path: 'training', name: 'training', component: TrainingCenter,
    meta: { title: '实训中心', icon: Reading, roles: ['student'] },
  },
  {
    path: 'my-evaluation', name: 'my-evaluation', component: MyEvaluation,
    meta: { title: '评价反馈', icon: DocumentChecked, roles: ['student'] },
  },
  {
    path: 'growth', name: 'growth', component: GrowthArchive,
    meta: { title: '成长档案', icon: CollectionTag, roles: ['student'] },
  },
  {
    path: 'student-course-management', name: 'student-course-management', component: StudentCourseManagement,
    meta: { title: '我的课程', icon: Reading, roles: ['student'] },
  },
  {
    path: 'training-management', name: 'training-management', component: TrainingManagement,
    meta: { title: '实训管理', icon: FolderChecked, roles: ['teacher', 'admin'] },
  },
  {
    path: 'course-management', name: 'course-management', component: CourseManagement,
    meta: { title: '课程管理', icon: Reading, roles: ['teacher', 'admin'] },
  },
  {
    path: 'indicator-management', name: 'indicator-management', component: IndicatorManagement,
    meta: { title: '评价指标', icon: Histogram, roles: ['teacher', 'admin'] },
  },
  {
    path: 'intelligent-evaluation', name: 'intelligent-evaluation', component: IntelligentEvaluation,
    meta: { title: '智能评价', icon: DocumentChecked, roles: ['teacher', 'admin'] },
  },
  {
    path: 'student-archive', name: 'student-archive', component: StudentArchive,
    meta: { title: '学生档案', icon: UserFilled, roles: ['teacher', 'admin'] },
  },
  {
    path: 'data-report', name: 'data-report', component: DataReport,
    meta: { title: '数据报表', icon: DataAnalysis, roles: ['teacher', 'admin'] },
  },
  {
    path: 'report-screen', name: 'report-screen', component: TrainingReportScreen,
    meta: { title: '实训大屏', icon: DataAnalysis, roles: ['teacher', 'enterprise', 'admin'] },
  },
  {
    path: 'project-training', name: 'project-training', component: ProjectTraining,
    meta: { title: '项目实训', icon: Briefcase, roles: ['enterprise'] },
  },
  {
    path: 'talent-evaluation', name: 'talent-evaluation', component: TalentEvaluation,
    meta: { title: '人才评价', icon: DocumentChecked, roles: ['enterprise'] },
  },
  {
    path: 'enterprise-mentor', name: 'enterprise-mentor', component: EnterpriseMentor,
    meta: { title: '企业导师', icon: UserFilled, roles: ['enterprise'] },
  },
  {
    path: 'partner-schools', name: 'partner-schools', component: PartnerSchools,
    meta: { title: '合作院校', icon: School, roles: ['enterprise'] },
  },
  {
    path: 'organization', name: 'organization', component: OrgManagement,
    meta: { title: '组织架构', icon: OfficeBuilding, roles: ['admin'] },
  },
  {
    path: 'user-management', name: 'user-management', component: UserManagement,
    meta: { title: '用户管理', icon: User, roles: ['admin'] },
  },
  {
    path: 'system-settings', name: 'system-settings', component: SystemSettings,
    meta: { title: '系统设置', icon: Setting, roles: ['admin'] },
  },
  {
    path: 'profile', name: 'profile', component: Profile,
    meta: { title: '个人中心', icon: User, roles: ['student', 'teacher', 'enterprise', 'admin'], hidden: true },
  },
]

export const getAccessibleRoutes = (role) => protectedRoutes.filter((route) => route.meta.roles.includes(role))
export const getMenuRoutes = (role) => getAccessibleRoutes(role).filter((route) => !route.meta.hidden)
