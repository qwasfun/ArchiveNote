<script setup>
import { ref, onMounted, watch } from 'vue'
import FileUpload from '../../components/FileUpload.vue'
import FileGrid from '../../components/FileGrid.vue'
import FilePreview from '../../components/FilePreview.vue'
import FileNotes from '../../components/FileNotes.vue'
import fileService from '../../api/fileService.js'
import folderService from '../../api/folderService.js'

const files = ref([])
const folders = ref([])
const currentFolderId = ref(null)
const breadcrumbs = ref([{ id: null, name: '首页' }])
const loading = ref(false)
const showUploadModal = ref(false)
const showCreateFolderModal = ref(false)
const showRenameFolderModal = ref(false)
const editingFolder = ref(null)
const newFolderName = ref('')
const renameFolderName = ref('')
const previewFile = ref(null)
const notesFile = ref(null)
const showNotes = ref(false)
const searchQuery = ref('')
const filterType = ref('all')

const currentPage = ref(1)
const pageSize = ref(20)
const totalFiles = ref(0)
const totalPages = ref(0)

const selectedFiles = ref([])
const selectedFolders = ref([])
const isSelectionMode = ref(false)
const showBatchMoveModal = ref(false)
const moveTargetFolderId = ref(null)
const allFolders = ref([])

const toggleSelectionMode = () => {
  isSelectionMode.value = !isSelectionMode.value
  selectedFiles.value = []
  selectedFolders.value = []
}

const handleSelectionChange = (selection) => {
  selectedFiles.value = selection.files
  selectedFolders.value = selection.folders
}

const batchDelete = async () => {
  if (
    !confirm(
      `Are you sure you want to delete ${selectedFiles.value.length} files and ${selectedFolders.value.length} folders?`,
    )
  )
    return

  try {
    if (selectedFiles.value.length > 0) {
      await fileService.batchDeleteFiles({ file_ids: selectedFiles.value })
    }
    if (selectedFolders.value.length > 0) {
      await folderService.batchDeleteFolders({ folder_ids: selectedFolders.value })
    }
    await loadData()
    selectedFiles.value = []
    selectedFolders.value = []
    isSelectionMode.value = false
  } catch (error) {
    console.error('Batch delete failed', error)
  }
}

const openBatchMoveModal = async () => {
  try {
    // Ideally we should fetch a tree or all folders.
    // For now, let's just fetch root folders or current level?
    // A proper folder selector is complex.
    // Let's just fetch all folders for now (might be heavy if many folders)
    // Or just fetch root and allow navigation?
    // Let's stick to a simple flat list of all folders for MVP if possible, or just root.
    // Actually, getFolders takes parent_id. If we want all, we might need a new endpoint or recursive fetch.
    // Let's just show root folders for now and maybe allow drilling down later?
    // Or just use a text input for folder ID for now? No that's bad UX.
    // Let's fetch root folders.
    const res = await folderService.getFolders({})
    allFolders.value = res
    showBatchMoveModal.value = true
  } catch (e) {
    console.error(e)
  }
}

const confirmBatchMove = async () => {
  try {
    if (selectedFiles.value.length > 0) {
      await fileService.batchMoveFiles({
        file_ids: selectedFiles.value,
        folder_id: moveTargetFolderId.value,
      })
    }
    if (selectedFolders.value.length > 0) {
      await folderService.batchMoveFolders({
        folder_ids: selectedFolders.value,
        parent_id: moveTargetFolderId.value,
      })
    }
    showBatchMoveModal.value = false
    await loadData()
    selectedFiles.value = []
    selectedFolders.value = []
    isSelectionMode.value = false
  } catch (error) {
    console.error('Batch move failed', error)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      q: searchQuery.value,
      file_type: filterType.value === 'all' ? undefined : filterType.value,
    }
    if (currentFolderId.value) {
      params.folder_id = currentFolderId.value
    }

    // Load folders
    const folderParams = {}
    if (currentFolderId.value) {
      folderParams.parent_id = currentFolderId.value
    }

    const [filesRes, foldersRes] = await Promise.all([
      fileService.getFiles(params),
      folderService.getFolders(folderParams),
    ])

    if ((filesRes.data || []).length === 0 && currentPage.value > 1) {
      currentPage.value = 1
      return loadData()
    }

    files.value = filesRes.data || []
    totalFiles.value = filesRes.total || 0
    totalPages.value = filesRes.total_pages || 0
    folders.value = foldersRes || []
  } catch (error) {
    console.error('Failed to load data', error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadData()
}

watch([searchQuery, filterType], () => {
  currentPage.value = 1
  loadData()
})

const createFolder = async () => {
  if (!newFolderName.value.trim()) return

  try {
    await folderService.createFolder({
      name: newFolderName.value,
      parent_id: currentFolderId.value,
    })
    newFolderName.value = ''
    showCreateFolderModal.value = false
    await loadData()
  } catch (error) {
    console.error('Failed to create folder', error)
  }
}

const openRenameFolderModal = (folder) => {
  editingFolder.value = folder
  renameFolderName.value = folder.name
  showRenameFolderModal.value = true
}

const renameFolder = async () => {
  if (!renameFolderName.value.trim()) return

  try {
    await folderService.updateFolder(editingFolder.value.id, {
      name: renameFolderName.value,
    })
    showRenameFolderModal.value = false
    editingFolder.value = null
    await loadData()
  } catch (error) {
    console.error('Failed to rename folder', error)
  }
}

const deleteFolder = async (folder) => {
  if (!confirm(`Are you sure you want to delete folder "${folder.name}" and all its contents?`))
    return

  try {
    await folderService.deleteFolder(folder.id)
    await loadData()
  } catch (error) {
    console.error('Failed to delete folder', error)
  }
}

const openFolder = async (folder) => {
  currentFolderId.value = folder.id
  breadcrumbs.value.push({ id: folder.id, name: folder.name })
  await loadData()
}

const navigateBreadcrumb = async (index) => {
  const target = breadcrumbs.value[index]
  currentFolderId.value = target.id
  breadcrumbs.value = breadcrumbs.value.slice(0, index + 1)
  await loadData()
}

const handleUploadSuccess = async () => {
  await loadData()
  showUploadModal.value = false
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this file?')) return
  try {
    await fileService.deleteFile(id)
    await loadData()
  } catch (error) {
    console.error('Failed to delete file', error)
  }
}

const handlePreview = (file) => {
  previewFile.value = file
}

const handleAddNote = (file) => {
  notesFile.value = file
  showNotes.value = true
  previewFile.value = null // 关闭预览
}

const handleViewNotes = (file) => {
  notesFile.value = file
  showNotes.value = true
}

const closePreview = () => {
  previewFile.value = null
}

const closeNotes = () => {
  showNotes.value = false
  notesFile.value = null
}

const handleNoteCreated = () => {
  // 可以在这里刷新文件列表，更新笔记计数
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-900">
    <div class="container mx-auto px-4 py-6">
      <!-- 头部区域 -->
      <div class="mb-8">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">📁 文件管理</h1>
            <p class="text-gray-600 dark:text-gray-400 mt-1">
              保存、查看和管理您的文件，支持多种格式
            </p>
          </div>
          <div class="flex gap-2">
            <button
              @click="toggleSelectionMode"
              class="btn"
              :class="isSelectionMode ? 'btn-secondary' : 'btn-ghost'"
            >
              {{ isSelectionMode ? '取消选择' : '批量选择' }}
            </button>
            <div v-if="isSelectionMode" class="flex gap-2">
              <button
                @click="batchDelete"
                class="btn btn-error"
                :disabled="selectedFiles.length === 0 && selectedFolders.length === 0"
              >
                删除
              </button>
              <button
                @click="openBatchMoveModal"
                class="btn btn-info"
                :disabled="selectedFiles.length === 0 && selectedFolders.length === 0"
              >
                移动
              </button>
            </div>
            <button @click="showCreateFolderModal = true" class="btn btn-primary gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"
                />
              </svg>
              新建文件夹
            </button>
            <button @click="showUploadModal = !showUploadModal" class="btn btn-primary gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                ></path>
              </svg>
              {{ showUploadModal ? '关闭上传' : '上传文件' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Breadcrumbs -->
      <div class="text-sm breadcrumbs mb-4">
        <ul>
          <li v-for="(crumb, index) in breadcrumbs" :key="crumb.id">
            <a
              @click="navigateBreadcrumb(index)"
              :class="{ 'font-bold': index === breadcrumbs.length - 1 }"
            >
              {{ crumb.name }}
            </a>
          </li>
        </ul>
      </div>
      <!-- Rename Folder Modal -->
      <div
        v-if="showRenameFolderModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-96 shadow-xl">
          <h3 class="text-lg font-bold mb-4 text-gray-900 dark:text-gray-100">重命名文件夹</h3>
          <input
            v-model="renameFolderName"
            type="text"
            placeholder="Folder Name"
            class="input input-bordered w-full mb-4"
            @keyup.enter="renameFolder"
            autoFocus
          />
          <div class="flex justify-end gap-2">
            <button @click="showRenameFolderModal = false" class="btn btn-ghost">取消</button>
            <button @click="renameFolder" class="btn btn-primary">保存</button>
          </div>
        </div>
      </div>

      <!-- Create Folder Modal -->
      <div
        v-if="showCreateFolderModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-96 shadow-xl">
          <h3 class="text-lg font-bold mb-4 text-gray-900 dark:text-gray-100">新建文件夹</h3>
          <input
            v-model="newFolderName"
            type="text"
            placeholder="Folder Name"
            class="input input-bordered w-full mb-4"
            @keyup.enter="createFolder"
            autoFocus
          />
          <div class="flex justify-end gap-2">
            <button @click="showCreateFolderModal = false" class="btn btn-ghost">取消</button>
            <button @click="createFolder" class="btn btn-primary">新建</button>
          </div>
        </div>
      </div>

      <!-- 上传区域 -->
      <div v-if="showUploadModal" class="mb-8">
        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">📤 上传文件</h2>
          <FileUpload :folder-id="currentFolderId" @upload-success="handleUploadSuccess" />
        </div>
      </div>

      <!-- 搜索和过滤 -->
      <div class="mb-6">
        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <div class="flex flex-col lg:flex-row gap-4">
            <!-- 搜索框 -->
            <div class="flex-1">
              <div class="relative">
                <svg
                  class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  ></path>
                </svg>
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="搜索文件名称..."
                  class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
            </div>

            <!-- 类型过滤 -->
            <div class="flex gap-2 flex-wrap">
              <select
                v-model="filterType"
                class="select select-bordered bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
              >
                <option value="all">📁 所有文件</option>
                <option value="image">🖼️ 图片</option>
                <option value="video">🎥 视频</option>
                <option value="pdf">📄 PDF</option>
                <option value="audio">🎵 音频</option>
                <option value="document">📝 文档</option>
              </select>
            </div>
          </div>

          <!-- 统计信息 -->
          <div
            class="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700"
          >
            <span class="text-sm text-gray-500">
              显示 {{ files.length }} / {{ totalFiles }} 个文件
            </span>
            <div class="flex gap-2 text-xs text-gray-500">
              <!-- Note: These counts are now only for the current page unless we fetch stats separately -->
              <span>🖼️ {{ files.filter((f) => f.mime_type.startsWith('image/')).length }}</span>
              <span>🎥 {{ files.filter((f) => f.mime_type.startsWith('video/')).length }}</span>
              <span>📄 {{ files.filter((f) => f.mime_type === 'application/pdf').length }}</span>
              <span>🎵 {{ files.filter((f) => f.mime_type.startsWith('audio/')).length }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 文件列表 -->
      <div class="min-h-96">
        <div v-if="loading" class="flex justify-center items-center py-12">
          <div class="text-center">
            <span class="loading loading-spinner loading-lg text-blue-500"></span>
            <p class="text-gray-500 mt-2">加载中...</p>
          </div>
        </div>

        <div
          v-else-if="
            totalFiles === 0 && folders.length === 0 && !searchQuery && filterType === 'all'
          "
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-12 text-center border border-gray-200 dark:border-gray-700"
        >
          <div class="text-6xl mb-4">📂</div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">暂无文件</h3>
          <p class="text-gray-500 mb-6">开始上传一些文件，让您的内容库丰富起来吧！</p>
          <button @click="showUploadModal = true" class="btn btn-primary">📤 上传第一个文件</button>
        </div>

        <div
          v-else-if="files.length === 0 && folders.length === 0"
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-12 text-center border border-gray-200 dark:border-gray-700"
        >
          <div class="text-6xl mb-4">🔍</div>

          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
            未找到匹配文件
          </h3>
          <p class="text-gray-500">请尝试修改搜索关键词或过滤条件</p>
        </div>

        <div
          v-else
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <FileGrid
            :files="files"
            :folders="folders"
            :selection-mode="isSelectionMode"
            :selected-files="selectedFiles"
            :selected-folders="selectedFolders"
            @selection-change="handleSelectionChange"
            @delete-file="handleDelete"
            @preview-file="handlePreview"
            @add-note="handleAddNote"
            @view-notes="handleViewNotes"
            @open-folder="openFolder"
            @delete-folder="deleteFolder"
            @edit-folder="openRenameFolderModal"
          />

          <!-- Pagination -->
          <div class="flex justify-center mt-6" v-if="totalPages > 1">
            <div class="join">
              <button
                class="join-item btn"
                :disabled="currentPage === 1"
                @click="handlePageChange(currentPage - 1)"
              >
                «
              </button>
              <button class="join-item btn">Page {{ currentPage }} of {{ totalPages }}</button>
              <button
                class="join-item btn"
                :disabled="currentPage === totalPages"
                @click="handlePageChange(currentPage + 1)"
              >
                »
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文件预览模态框 -->
    <FilePreview :file="previewFile" @close="closePreview" @add-note="handleAddNote" />

    <!-- 文件笔记模态框 -->
    <FileNotes
      :is-open="showNotes"
      :file="notesFile"
      @close="closeNotes"
      @note-created="handleNoteCreated"
    />

    <!-- Batch Move Modal -->
    <div
      v-if="showBatchMoveModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-96 shadow-xl">
        <h3 class="text-lg font-bold mb-4 text-gray-900 dark:text-gray-100">移动到...</h3>
        <select v-model="moveTargetFolderId" class="select select-bordered w-full mb-4">
          <option :value="null">根目录</option>
          <option v-for="folder in allFolders" :key="folder.id" :value="folder.id">
            {{ folder.name }}
          </option>
        </select>
        <div class="flex justify-end gap-2">
          <button @click="showBatchMoveModal = false" class="btn btn-ghost">取消</button>
          <button @click="confirmBatchMove" class="btn btn-primary">移动</button>
        </div>
      </div>
    </div>
  </div>
</template>
