<template>
  <div class="course-management">
    <div class="page-header">
      <div class="header-left">
        <el-button type="primary" class="btn-add" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加课程
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
      <!-- 文件夹卡片 -->
      <div
        v-for="folder in folderList"
        :key="'folder-' + folder.id"
        class="folder-card"
      >
        <div class="folder-cover">
          <svg viewBox="0 0 120 90" class="folder-icon">
            <path d="M10 20 L10 75 Q10 80 15 80 L105 80 Q110 80 110 75 L110 30 Q110 25 105 25 L55 25 L45 15 L15 15 Q10 15 10 20 Z" fill="#2c2c2c" />
            <path d="M10 20 L10 25 Q10 20 15 20 L55 20 L45 15 L15 15 Q10 15 10 20 Z" fill="#1a1a1a" />
          </svg>
          <span class="folder-name">{{ folder.folder_name }}</span>
        </div>
        <div class="folder-hover-actions">
          <span class="hover-action-btn" @click.stop="handleRenameFolder(folder)">重命名</span>
          <span class="hover-action-divider">|</span>
          <span class="hover-action-btn danger" @click.stop="handleDeleteFolder(folder)">删除</span>
        </div>
      </div>

      <!-- 课程卡片 -->
      <div
        v-for="course in courseList"
        :key="'course-' + course.id"
        class="course-card"
        :class="{ 'course-card-pinned': course.sort_order === -1 }"
        @click="handleCardClick(course)"
      >
        <div v-if="course.sort_order === -1" class="pinned-badge">
          <el-icon><Rank /></el-icon>
          <span>置顶</span>
        </div>
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
            <span class="hover-action-btn" @click.stop="handleEdit(course)">编辑</span>
            <span class="hover-action-divider">|</span>
            <span class="hover-action-btn" @click.stop="handleQuitCourse(course)">退课</span>
            <span class="hover-action-divider">|</span>
            <span class="hover-action-btn" @click.stop="handlePinCourse(course)">{{ course.sort_order === -1 ? '取消置顶' : '置顶' }}</span>
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

      <div v-if="courseList.length === 0 && folderList.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无课程，点击「添加课程」开始创建" />
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

    <!-- 添加/编辑课程对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'add' ? '添加课程' : '编辑课程'"
      width="650px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="课程封面">
          <div class="cover-upload">
            <el-upload
              class="cover-uploader"
              action="/api/uploads"
              :headers="uploadHeaders"
              :show-file-list="false"
              :before-upload="beforeUpload"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
            >
              <img v-if="formData.cover_image" :src="getImageUrl(formData.cover_image)" class="cover-image" />
              <div v-else class="cover-placeholder">
                <el-icon class="upload-icon"><Plus /></el-icon>
                <div class="upload-text">点击上传封面</div>
              </div>
            </el-upload>
            <el-button
              v-if="formData.cover_image"
              type="danger"
              link
              size="small"
              @click="handleRemoveCover"
            >
              移除封面
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="课程名称" prop="course_name">
          <el-input v-model="formData.course_name" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="课程编码" prop="course_code">
          <el-input
            v-model="formData.course_code"
            placeholder="请输入课程编码"
            :disabled="dialogMode === 'edit'"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-input v-model="formData.category" placeholder="请输入课程分类" />
        </el-form-item>
        <el-form-item label="学分" prop="credits">
          <el-input-number
            v-model="formData.credits"
            :min="1"
            :max="10"
            placeholder="请输入学分"
          />
        </el-form-item>
        <el-form-item label="最大人数" prop="max_students">
          <el-input-number
            v-model="formData.max_students"
            :min="1"
            :max="500"
            placeholder="请输入最大人数"
          />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_date">
          <el-date-picker
            v-model="formData.start_date"
            type="datetime"
            placeholder="选择开始时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_date">
          <el-date-picker
            v-model="formData.end_date"
            type="datetime"
            placeholder="选择结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态">
            <el-option label="禁用" :value="0" />
            <el-option label="启用" :value="1" />
            <el-option label="结束" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入课程描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 重命名文件夹对话框 -->
    <el-dialog v-model="renameDialogVisible" title="重命名文件夹" width="400px">
      <el-form ref="renameFormRef" :model="renameFormData" :rules="folderFormRules" label-width="80px">
        <el-form-item label="文件夹名" prop="folder_name">
          <el-input v-model="renameFormData.folder_name" placeholder="请输入新的文件夹名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmRenameFolder">确定</el-button>
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
import { Plus, Search, Picture, MagicStick, Rank, Expand } from '@element-plus/icons-vue'
import {
  listCourses,
  createCourse,
  updateCourse,
  deleteCourse,
  pinCourse,
} from '../../api/courses'
import {
  listFolders,
  updateFolder,
  deleteFolder,
} from '../../api/courseFolders'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

// 课程列表数据
const courseList = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchKeyword = ref('')

// 文件夹列表数据
const folderList = ref([])

// 课程对话框
const dialogVisible = ref(false)
const dialogMode = ref('add')
const submitLoading = ref(false)
const formRef = ref(null)
const formData = reactive({
  id: null,
  course_name: '',
  course_code: '',
  teacher_id: null,
  org_id: null,
  category: '',
  description: '',
  start_date: '',
  end_date: '',
  status: 1,
  max_students: 50,
  credits: 2,
  cover_image: '',
})

// 重命名文件夹对话框
const renameDialogVisible = ref(false)
const renameFormRef = ref(null)
const renameFormData = reactive({
  id: null,
  folder_name: '',
})

// 封面预览
const previewVisible = ref(false)
const previewImageUrl = ref('')

const uploadHeaders = computed(() => {
  const session = JSON.parse(localStorage.getItem('ste-user-session') || '{}')
  return { Authorization: `Bearer ${session.token}` }
})

const formRules = {
  course_name: [
    { required: true, message: '请输入课程名称', trigger: 'blur' },
    { max: 150, message: '课程名称不能超过150个字符', trigger: 'blur' },
  ],
  course_code: [
    { required: true, message: '请输入课程编码', trigger: 'blur' },
    { max: 64, message: '课程编码不能超过64个字符', trigger: 'blur' },
  ],
  credits: [
    { required: true, message: '请输入学分', trigger: 'blur' },
  ],
  max_students: [
    { required: true, message: '请输入最大人数', trigger: 'blur' },
  ],
}

const folderFormRules = {
  folder_name: [
    { required: true, message: '请输入文件夹名称', trigger: 'blur' },
    { max: 100, message: '文件夹名称不能超过100个字符', trigger: 'blur' },
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
    const res = await listCourses(params)
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

// 获取文件夹列表
const fetchFolders = async () => {
  try {
    const res = await listFolders({ page: 1, page_size: 200 })
    folderList.value = res.items || []
  } catch (error) {
    // 静默失败
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchCourses()
}

const handleReset = () => {
  searchKeyword.value = ''
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

const handleAdd = () => {
  dialogMode.value = 'add'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogMode.value = 'edit'
  Object.assign(formData, {
    id: row.id,
    course_name: row.course_name,
    course_code: row.course_code,
    teacher_id: row.teacher_id,
    org_id: row.org_id,
    category: row.category || '',
    description: row.description || '',
    start_date: row.start_date || '',
    end_date: row.end_date || '',
    status: row.status,
    max_students: row.max_students || 50,
    credits: row.credits || 2,
    cover_image: row.cover_image || '',
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除课程"${row.course_name}"吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await deleteCourse(row.id)
    ElMessage.success('删除成功')
    fetchCourses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleCardClick = (course) => {
  // 点击卡片可以进入课程详情
}

const handleMoveTo = (course) => {
  ElMessage.info(`移动到: ${course.course_name}`)
}

const handleQuitCourse = async (course) => {
  try {
    await ElMessageBox.confirm(
      `确定要退出课程"${course.course_name}"吗？退课后课程将被删除。`,
      '退课确认',
      {
        confirmButtonText: '确定退课',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await deleteCourse(course.id)
    ElMessage.success(`已退出课程: ${course.course_name}`)
    fetchCourses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('退课失败')
    }
  }
}

const handlePinCourse = async (course) => {
  const isPinned = course.sort_order === -1
  try {
    if (isPinned) {
      // 取消置顶：sort_order 恢复为 0
      await updateCourse(course.id, { sort_order: 0 })
      ElMessage.success(`已取消置顶: ${course.course_name}`)
    } else {
      // 置顶
      await pinCourse(course.id)
      ElMessage.success(`已置顶课程: ${course.course_name}`)
    }
    fetchCourses()
  } catch (error) {
    ElMessage.error(isPinned ? '取消置顶失败' : '置顶失败')
  }
}

const handlePreviewCover = (course) => {
  if (course.cover_image) {
    previewImageUrl.value = getImageUrl(course.cover_image)
    previewVisible.value = true
  } else {
    ElMessage.warning('该课程暂无封面图片')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      const submitData = {
        ...formData,
        teacher_id: userStore.userId,
      }

      if (dialogMode.value === 'add') {
        await createCourse(submitData)
        ElMessage.success('添加成功')
      } else {
        await updateCourse(formData.id, submitData)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      fetchCourses()
    } catch (error) {
      ElMessage.error(dialogMode.value === 'add' ? '添加失败' : '更新失败')
    } finally {
      submitLoading.value = false
    }
  })
}

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    course_name: '',
    course_code: '',
    teacher_id: null,
    org_id: null,
    category: '',
    description: '',
    start_date: '',
    end_date: '',
    status: 1,
    max_students: 50,
    credits: 2,
    cover_image: '',
  })
  formRef.value?.clearValidate()
}

const handleDialogClose = () => {
  resetForm()
}

// 文件夹相关
const handleRenameFolder = (folder) => {
  renameFormData.id = folder.id
  renameFormData.folder_name = folder.folder_name
  renameDialogVisible.value = true
}

const handleConfirmRenameFolder = async () => {
  if (!renameFormRef.value) return
  await renameFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await updateFolder(renameFormData.id, { folder_name: renameFormData.folder_name })
      ElMessage.success('重命名成功')
      renameDialogVisible.value = false
      fetchFolders()
    } catch (error) {
      ElMessage.error('重命名失败')
    }
  })
}

const handleDeleteFolder = async (folder) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件夹"${folder.folder_name}"吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await deleteFolder(folder.id)
    ElMessage.success('删除成功')
    fetchFolders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return url
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB')
    return false
  }
  return true
}

const handleUploadSuccess = (response) => {
  const fileUrl = response?.file_url || response?.data?.file_url
  if (fileUrl) {
    formData.cover_image = fileUrl
    ElMessage.success('封面上传成功')
  } else {
    ElMessage.error('封面上传失败')
  }
}

const handleUploadError = () => {
  ElMessage.error('封面上传失败，请重试')
}

const handleRemoveCover = () => {
  formData.cover_image = ''
}

onMounted(() => {
  fetchCourses()
  fetchFolders()
})
</script>

<style scoped>
.course-management {
  padding: 24px 32px;
  background: #f5f7fa;
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-add {
  background: linear-gradient(135deg, #A8D8EA 0%, #7EC8E3 100%);
  border: none;
  border-radius: 24px;
  padding: 10px 24px;
  font-size: 15px;
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(126, 200, 227, 0.4);
  transition: all 0.3s;
}

.btn-add:hover {
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

/* 文件夹卡片 */
.folder-card {
  background: #f0f4f8;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  min-height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.folder-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.folder-cover {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
}

.folder-icon {
  width: 80px;
  height: 60px;
  flex-shrink: 0;
}

.folder-name {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

/* 文件夹悬停操作 */
.folder-hover-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 6px 12px;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 2;
}

.folder-card:hover .folder-hover-actions {
  opacity: 1;
}

/* 课程卡片 */
.course-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  position: relative;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.course-card-pinned {
  border: 2px solid #667eea;
}

.pinned-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  z-index: 3;
}

.card-cover {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;
  background: #f0f2f5;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.course-card:hover .cover-img {
  transform: scale(1.05);
}

.cover-default {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
}

/* 课程卡片悬停操作栏 */
.card-hover-actions {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 0 0 8px 8px;
  opacity: 0;
  transform: translateY(-100%);
  transition: all 0.3s ease;
  z-index: 2;
}

.course-card:hover .card-hover-actions {
  opacity: 1;
  transform: translateY(0);
}

.hover-action-btn {
  font-size: 13px;
  color: #409eff;
  cursor: pointer;
  user-select: none;
  transition: color 0.2s;
}

.hover-action-btn:hover {
  color: #66b1ff;
}

.hover-action-btn.danger {
  color: #f56c6c;
}

.hover-action-btn.danger:hover {
  color: #f78989;
}

.hover-action-divider {
  color: #dcdfe6;
  font-size: 12px;
  user-select: none;
}

.drag-icon {
  font-size: 14px;
  color: #409eff;
  cursor: grab;
}

.progress-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 10px 14px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  font-size: 13px;
}

.progress-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.progress-bar {
  width: 80px;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #409eff;
  border-radius: 3px;
  transition: width 0.3s;
}

.progress-percent {
  font-weight: 600;
  min-width: 36px;
  text-align: right;
}

.card-body {
  padding: 16px 16px 20px;
}

.course-title {
  margin: 0 0 10px 0;
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-teacher {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  padding: 60px 0;
}

/* 分页 */
.pagination {
  margin-top: 32px;
  display: flex;
  justify-content: center;
}

/* 封面上传 */
.cover-upload {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cover-uploader :deep(.el-upload) {
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.cover-uploader :deep(.el-upload:hover) {
  border-color: var(--el-color-primary);
}

.cover-image {
  width: 140px;
  height: 90px;
  display: block;
  object-fit: cover;
  border-radius: 6px;
}

.cover-placeholder {
  width: 140px;
  height: 90px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
  color: #8c939d;
  border-radius: 6px;
}

.upload-icon {
  font-size: 28px;
  margin-bottom: 4px;
}

.upload-text {
  font-size: 12px;
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
