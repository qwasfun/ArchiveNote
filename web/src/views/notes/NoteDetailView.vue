<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import noteService from '../../api/noteService.js'
import NoteEditor from '../../components/NoteEditor.vue'
import FileDetails from '../../components/FileDetails.vue'
import { formatDate, formatSize } from '@/utils/format'
import { getFileIcon, getFileTypeColor } from '@/utils/file'

const route = useRoute()
const router = useRouter()

const note = ref(null)
const loading = ref(false)
const isEditing = ref(false)
const detailsFile = ref(null)
const showDetails = ref(false)

const noteId = computed(() => route.params.id)

// 检查是否可以返回（是否从其他页面导航过来）
const canGoBack = ref(false)

const loadNote = async () => {
  if (!noteId.value) return

  loading.value = true
  try {
    const response = await noteService.getNote(noteId.value)
    note.value = response
  } catch (error) {
    console.error('Failed to load note', error)
    // 如果笔记不存在，返回笔记列表
    if (error.response?.status === 404) {
      alert('笔记不存在')
      router.push({ name: 'notes' })
    }
  } finally {
    loading.value = false
  }
}

const handleEdit = () => {
  isEditing.value = true
}

const handleSave = async (noteData) => {
  try {
    await noteService.updateNote(noteId.value, noteData)
    await loadNote()
    isEditing.value = false
  } catch (error) {
    console.error('Failed to save note', error)
  }
}

const handleDelete = async () => {
  if (!confirm('Are you sure you want to delete this note?')) return
  try {
    await noteService.deleteNote(noteId.value)
    router.push({ name: 'notes' })
  } catch (error) {
    console.error('Failed to delete note', error)
  }
}

const handleCancel = () => {
  isEditing.value = false
}

const handleBack = () => {
  router.back()
}

const handleFileClick = (file) => {
  detailsFile.value = file
  showDetails.value = true
}

const handleFolderClick = (folder) => {
  // 跳转到文件列表页面，显示该文件夹内容
  router.push({ name: 'files', query: { folder_id: folder.id } })
}

const handleCloseDetails = () => {
  showDetails.value = false
  detailsFile.value = null
}

const renderedContent = computed(() => {
  if (!note.value?.content) return '暂无内容'
  const rawHtml = marked.parse(note.value.content)
  return DOMPurify.sanitize(rawHtml)
})

onMounted(async () => {
  // 检查是否从笔记列表页进入
  // router.options.history.state.back 包含上一个路由的路径
  const previousRoute = router.options.history.state.back

  console.log(previousRoute)

  // 如果上一个路由是 /notes 或 /#/notes（hash 模式），则显示返回按钮
  if (previousRoute) {
    // 检查是否来自笔记列表页（不是笔记详情页）
    canGoBack.value =
      previousRoute === '/notes' ||
      previousRoute.startsWith('/notes') ||
      previousRoute.startsWith('#/notes')
  } else {
    canGoBack.value = false
  }

  await loadNote()
})
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-900 min-h-[calc(100vh-64px)]">
    <div class="container mx-auto px-4 py-6 flex flex-row">
      <!-- Loading State -->
      <div v-if="loading" class="flex-1 justify-center items-center py-12">
        <div class="text-center">
          <span class="loading loading-spinner loading-lg text-blue-500"></span>
          <p class="text-gray-500 mt-2">加载中...</p>
        </div>
      </div>

      <!-- Editor Mode -->
      <div v-else-if="isEditing && note" class="mx-auto flex-1 pb-2 overflow-auto">
        <NoteEditor :note="note" @save="handleSave" @cancel="handleCancel" />
      </div>

      <!-- View Mode -->
      <div v-else-if="note" class="flex-1 mx-auto">
        <!-- Header -->
        <div class="mb-6">
          <div class="flex items-center gap-4 mb-4">
            <button v-if="canGoBack" class="btn btn-ghost btn-sm gap-2" @click="handleBack">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              返回
            </button>
            <div class="flex-1"></div>
            <button class="btn btn-error btn-sm btn-outline gap-2" @click="handleDelete">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              删除笔记
            </button>
            <button class="btn btn-primary btn-sm gap-2" @click="handleEdit">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              编辑笔记
            </button>
          </div>

          <div
            class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-200 dark:border-gray-700"
          >
            <h1 class="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              {{ note.title || 'Untitled Note' }}
            </h1>
            <div class="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <span>创建于 {{ formatDate(note.created_at) }}</span>
              </div>
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                <span>更新于 {{ formatDate(note.updated_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Associated Folders -->
        <div
          v-if="note.folders && note.folders.length > 0"
          class="mb-6 bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
            <span>📁</span>
            <span>关联的文件夹 ({{ note.folders.length }})</span>
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div
              v-for="folder in note.folders"
              :key="folder.id"
              class="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-xl cursor-pointer transition-colors group"
              @click="handleFolderClick(folder)"
            >
              <div class="text-3xl flex-shrink-0">📁</div>
              <div class="flex-1 min-w-0">
                <p class="font-medium truncate group-hover:text-primary">{{ folder.name }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  {{ formatDate(folder.updated_at) }}
                </p>
              </div>
              <svg
                class="w-5 h-5 text-gray-400 group-hover:text-primary flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </div>
          </div>
        </div>

        <!-- Associated Files -->
        <div
          v-if="note.files && note.files.length > 0"
          class="mb-6 bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
            <span>📎</span>
            <span>关联的文件 ({{ note.files.length }})</span>
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div
              v-for="file in note.files"
              :key="file.id"
              class="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-xl cursor-pointer transition-colors group"
              @click="handleFileClick(file)"
            >
              <div
                :class="`w-12 h-12 rounded-lg flex items-center justify-center text-2xl flex-shrink-0 ${getFileTypeColor(file.mime_type)}`"
              >
                {{ getFileIcon(file.mime_type) }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium truncate group-hover:text-primary">{{ file.filename }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatSize(file.size) }}</p>
              </div>
              <svg
                class="w-5 h-5 text-gray-400 group-hover:text-primary flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </div>
          </div>
        </div>

        <!-- Note Content -->
        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-200 dark:border-gray-700"
        >
          <div class="prose dark:prose-invert max-w-none prose-lg">
            <div v-html="renderedContent"></div>
          </div>
        </div>
      </div>

      <!-- Note Not Found -->
      <div
        v-else
        class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-12 text-center border border-gray-200 dark:border-gray-700"
      >
        <div class="text-6xl mb-4">📝</div>
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">笔记未找到</h3>
        <p class="text-gray-500 mb-6">该笔记可能已被删除或不存在</p>
        <button @click="handleBack" class="btn btn-primary">返回笔记列表</button>
      </div>
    </div>

    <!-- File Details Modal -->
    <FileDetails
      :file-id="detailsFile && detailsFile.id"
      :is-open="showDetails"
      @close="handleCloseDetails"
      @delete="handleDelete"
    />
  </div>
</template>
