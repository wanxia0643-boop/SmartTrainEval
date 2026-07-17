<template>
  <div class="student-course-management">
    <div class="page-header">
      <div class="header-left">
        <el-button type="primary" class="btn-enroll" @click="enrollDialogVisible = true">
          <el-icon><Plus /></el-icon>
          加入课程
        </el-button>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索"
          clearable
          class="search-input"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <div v-loading="loading" class="course-grid">
      <div
        v-for="course in courseList"
        :key="course.id"
        class="course-card"
        @click="handleCardClick(course)"
      >
        <div class="card-cover">
          <img
            v-if="course.cover_image"
            :src="getImageUrl(course.cover_image)"
            :alt="course.course_name"
            class="cover-img"
          />
          <div v-else class="cover-default">
            <el-icon :size="48"><Picture /></el-icon>
          </div>
          <div class="card-hover-actions">
            <span class="hover-action-btn danger" @click.stop="handleDropCourse(course)">退课</span>
            <span class="hover-action-divider">|</span>
            <el-icon class="hover-action-btn drag-icon" @click.stop="handlePreviewCover(course)"><Expand /></el-icon>
          </div>
          <div v-if="course.progress !== undefined" class="progress-overlay">
            <span class="progress-text">任务点进度: {{ course.progress }}/{{ course.total }}</span>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: course.progressPercent + '%' }"></div>
            </div>
            <span class="progress-percent">{{ course.progressPercent }}%</span>
          </div>
        </div>
        <div class="card-body">
          <h3 class="course-title">{{ course.course_name }}</h3>
          <p class="course-teacher">{{ course.teacher_name || '-' }}</p>
        </div>
      </div>

      <div v-if="courseList.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无课程，点击「加入课程」开始学习" />
      </div>
    </div>

    <div v-if="total > pageSize" class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[6, 12, 24]"
        :total="total"
        layout="total, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 加入课程对话框 -->
    <el-dialog v-model="enrollDialogVisible" title="加入课程" width="400px">
      <el-form ref="enrollFormRef" :model="enrollFormData" :rules="enrollFormRules" label-width="80px">
        <el-form-item label="课程编码" prop="course_code">
          <el-input v-model="enrollFormData.course_code" placeholder="请输入课程编码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="enrollDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="enrollLoading" @click="handleEnroll">确定</el-button>
      </template>
    </el-dialog>

    <!-- 封面全屏预览 -->
    <el-dialog
      v-model="previewVisible"
      width="90vw"
      :show-close="true"
      class="cover-preview-dialog"
      append-to-body
    >
      <img
        v-if="previewImageUrl"
        :src="previewImageUrl"
        class="cover-preview-img"
        alt="封面预览"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Picture, Expand } from '@element-plus/icons-vue'
import {
  listStudentCourses,
  enrollCourse,
  dropCourse,
} from '../../api/studentCourses'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

// 课程列表数据
const courseList = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchKeyword = ref('')

// 加入课程对话框
const enrollDialogVisible = ref(false)
const enrollFormRef = ref(null)
const enrollLoading = ref(false)
const enrollFormData = reactive({
  course_code: '',
})

// 封面预览
const previewVisible = ref(false)
const previewImageUrl = ref('')

const enrollFormRules = {
  course_code: [
    { required: true, message: '请输入课程编码', trigger: 'blur' },
    { max: 64, message: '课程编码不能超过64个字符', trigger: 'blur' },
  ],
}

// 获取课程列表
const fetchCourses = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    const res = await listStudentCourses(params)
    courseList.value = (res.items || []).map(item => ({
      ...item,
      progress: item.progress || 0,
      total: item.total || 0,
      progressPercent: item.total ? Math.round((item.progress / item.total) * 100) : 0,
    }))
    total.value = res.total || 0
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchCourses()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchCourses()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchCourses()
}

const handleEnroll = async () => {
  if (!enrollFormRef.value) return
  await enrollFormRef.value.validate(async (valid) => {
    if (!valid) return
    enrollLoading.value = true
    try {
      await enrollCourse({ course_code: enrollFormData.course_code })
      ElMessage.success('加入课程成功')
      enrollDialogVisible.value = false
      enrollFormData.course_code = ''
      fetchCourses()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '加入课程失败')
    } finally {
      enrollLoading.value = false
    }
  })
}

const handleDropCourse = async (course) => {
  try {
    await ElMessageBox.confirm(
      `确定要退出课程「${course.course_name}」吗？`,
      '退课确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await dropCourse(course.enrollment_id)
    ElMessage.success(`已退出课程: ${course.course_name}`)
    fetchCourses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('退课失败')
    }
  }
}

const handleCardClick = (course) => {
  // TODO: 跳转到课程详情页
  ElMessage.info(`课程详情: ${course.course_name}`)
}

const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  // 上传文件路径直接返回，不走 /api 代理
  return path
}

const handlePreviewCover = (course) => {
  if (course.cover_image) {
    previewImageUrl.value = getImageUrl(course.cover_image)
    previewVisible.value = true
  } else {
    ElMessage.warning('该课程暂无封面图片')
  }
}

onMounted(() => {
  fetchCourses()
})
</script>

<style scoped>
.student-course-management {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-enroll {
  background: linear-gradient(135deg, #A8D8EA 0%, #7EC8E3 100%);
  border: none;
  border-radius: 24px;
  padding: 10px 24px;
  font-size: 15px;
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(126, 200, 227, 0.4);
  transition: all 0.3s;
}

.btn-enroll:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(126, 200, 227, 0.5);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-input {
  width: 200px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 24px;
}

/* 网格布局 */
.course-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

/* 课程卡片 */
.course-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: relative;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-cover {
  position: relative;
  width: 100%;
  height: 160px;
  overflow: hidden;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-default {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0e0e0 0%, #f5f5f5 100%);
  color: #999;
}

.card-hover-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: none;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 6px;
  padding: 4px 12px;
  font-size: 13px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.course-card:hover .card-hover-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hover-action-btn {
  cursor: pointer;
  color: #409eff;
  transition: color 0.2s;
}

.hover-action-btn:hover {
  color: #66b1ff;
}

.hover-action-btn.danger {
  color: #f56c6c;
}

.hover-action-btn.danger:hover {
  color: #f89898;
}

.hover-action-divider {
  color: #dcdfe6;
}

.drag-icon {
  font-size: 16px;
  cursor: pointer;
  color: #909399;
}

.drag-icon:hover {
  color: #409eff;
}

/* 进度条覆盖层 */
.progress-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  padding: 20px 12px 8px;
  color: #fff;
}

.progress-text {
  font-size: 12px;
  display: block;
  margin-bottom: 4px;
}

.progress-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  height: 100%;
  background: #409eff;
  border-radius: 2px;
  transition: width 0.3s;
}

.progress-percent {
  font-size: 14px;
  font-weight: bold;
  float: right;
}

.card-body {
  padding: 12px 16px;
}

.course-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-teacher {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  padding: 60px 0;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 封面全屏预览 */
.cover-preview-dialog :deep(.el-dialog__body) {
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.9);
}

.cover-preview-img {
  max-width: 100%;
  max-height: 85vh;
  object-fit: contain;
}
</style>
