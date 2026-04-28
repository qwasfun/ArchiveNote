<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { getNotes, createNote, updateNote, getNote, deleteNote } from '../../api/noteService.js'
import { deleteFile } from '../../api/fileService.js'
import NoteEditor from '../../components/NoteEditor.vue'
import FileDetails from '../../components/FileDetails.vue'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { formatDate, formatSize } from '@/utils/format'
import { getFileIcon, getFileTypeColor } from '@/utils/file'

const router = useRouter()

const notes = ref([])
const loading = ref(false)
const selectedNote = ref(null)
const isEditing = ref(false)
const isViewing = ref(false)

const detailsFile = ref(null)
const showDetails = ref(false)

const currentPage = ref(1)
const pageSize = ref(10)
const totalNotes = ref(0)
const totalPages = ref(0)

const isNoteDirty = ref(false)

const { showToast } = useToast()
const { confirm: showConfirm } = useConfirm()

const loadNotes = async () => {
  loading.value = true
  try {
    const response = await getNotes({
      page: currentPage.value,
      page_size: pageSize.value,
    })

    if ((response.data || []).length === 0 && currentPage.value > 1) {
      currentPage.value = 1
      return loadNotes()
    }

    notes.value = response.data
    totalNotes.value = response.total
    totalPages.value = response.total_pages
  } catch (error) {
    console.error('Failed to load notes', error)
  } finally {
    loading.value = false
  }
}

const confirmDiscardChanges = async () => {
  if (isNoteDirty.value) {
    try {
      await showConfirm('您有未保存的修改，确定要离开吗？未保存的内容将会丢失。', {
        title: '确认放弃修改',
        type: 'warning',
      })
      return true
    } catch {
      return false
    }
  }
  return true
}

const handlePageChange = async (page) => {
  if (isEditing.value && !(await confirmDiscardChanges())) return
  currentPage.value = page
  loadNotes()
}

const handleCreate = async () => {
  if (isEditing.value && !(await confirmDiscardChanges())) return

  selectedNote.value = null
  isViewing.value = false
  isEditing.value = true
  isNoteDirty.value = false
}

const handleRefresh = async () => {
  if (isEditing.value && !(await confirmDiscardChanges())) return
  loadNotes()
}

const handleView = async (note) => {
  if (isEditing.value && !(await confirmDiscardChanges())) return

  selectedNote.value = { ...note } // Clone to avoid direct mutation
  isViewing.value = true
  isEditing.value = false
  isNoteDirty.value = false
}

const handleDetail = async (note) => {
  if (isEditing.value && !(await confirmDiscardChanges())) return
  // 跳转到独立的笔记详情页面
  router.push({ name: 'note-detail', params: { id: note.id } })
}

const handleEdit = async (note) => {
  if (note) {
    if (isEditing.value && !(await confirmDiscardChanges())) return
    selectedNote.value = { ...note }
  }
  isViewing.value = false
  isEditing.value = true
  isNoteDirty.value = false
}

const handleAutoSave = async (noteData, callback) => {
  try {
    let savedNoteId
    let response
    if (selectedNote.value && selectedNote.value.id) {
      await updateNote(selectedNote.value.id, noteData)
      savedNoteId = selectedNote.value.id
    } else {
      response = await createNote(noteData)
      savedNoteId = response.id
    }

    // 成功回调
    if (callback) callback(true)

    // 如果是新建笔记，自动保存后需要更新selectedNote的ID，以便后续是更新操作而不是新建
    if ((!selectedNote.value || !selectedNote.value.id) && savedNoteId) {
      selectedNote.value = {
        ...noteData,
        id: savedNoteId,
      }
      // 重新通过API获取完整信息（包括时间戳等）
      const freshNote = await getNote(savedNoteId)
      selectedNote.value = freshNote

      // 刷新列表以显示新笔记
      loadNotes()
    } else {
      // 如果是更新，也刷新当前笔记以拿到最新关联信息
      if (savedNoteId) {
        const freshNote = await getNote(savedNoteId)
        selectedNote.value = freshNote
      }
    }
  } catch (error) {
    console.error('Auto save failed', error)
    if (callback) callback(false)
  }
}

const handleSave = async (noteData) => {
  try {
    let savedNoteId
    if (selectedNote.value && selectedNote.value.id) {
      await updateNote(selectedNote.value.id, noteData)
      savedNoteId = selectedNote.value.id
    } else {
      const response = await createNote(noteData)
      savedNoteId = response.id
    }

    showToast('笔记已保存')
    isNoteDirty.value = false

    // 重新加载笔记列表
    await loadNotes()

    // 找到刚保存的笔记并显示预览
    const savedNote = notes.value.find((note) => note.id === savedNoteId)
    if (savedNote) {
      selectedNote.value = { ...savedNote }
    }

    // 切换到预览模式
    isEditing.value = false
    isViewing.value = true
  } catch (error) {
    console.error('Failed to save note', error)
  }
}

const handleDelete = async (id) => {
  try {
    await showConfirm('Are you sure you want to delete this note?', {
      title: '确认删除',
      type: 'error',
    })
    await deleteNote(id)
    await loadNotes()
    if (selectedNote.value && selectedNote.value.id === id) {
      isViewing.value = false
      selectedNote.value = null
    }
  } catch (error) {
    if (error !== false) {
      console.error('Failed to delete note', error)
    }
  }
}

const handleCancel = async () => {
  // NoteEditor已经处理了脏检查提示（或者我们在这里处理）
  // 如果NoteEditor的取消按钮触发了这个，说明用户已经点击了取消
  // 但是我们需要确认是否真的要取消（如果NoteEditor内部没做确认）
  // 通常取消按钮已经在NoteEditor里，但目前的NoteEditor使用了emit 'cancel'

  if (await confirmDiscardChanges()) {
    isEditing.value = false
    isNoteDirty.value = false
    if (!selectedNote.value?.id) {
      isViewing.value = false
      selectedNote.value = null
    } else {
      isViewing.value = true
    }
  }
  // 有可能更新了关联文件或文件夹，刷新一次列表，保持列表最新
  loadNotes()
}

const handleDeleteFile = async (id) => {
  try {
    await showConfirm('Are you sure you want to delete this file?', {
      title: '确认删除',
      type: 'error',
    })
    await deleteFile(id)
    showDetails.value = false
    await loadNotes()
  } catch (error) {
    if (error !== false) {
      console.error('Failed to delete file', error)
    }
  }
}

const handleFileClick = (file) => {
  detailsFile.value = file
  showDetails.value = true
}

const handleFolderClick = async (folder) => {
  // 应该也检查是否有未保存修改
  if (isEditing.value && !(await confirmDiscardChanges())) return
  // 跳转到文件列表页面，显示该文件夹内容
  router.push({ name: 'files', query: { folder_id: folder.id } })
}

const handleCloseDetails = () => {
  showDetails.value = false
  detailsFile.value = null
}

const renderedContent = computed(() => {
  if (!selectedNote.value?.content) return ''
  const rawHtml = marked.parse(selectedNote.value.content)
  return DOMPurify.sanitize(rawHtml)
})

const handleDirtyUpdate = (val) => {
  isNoteDirty.value = val
}

// 路由守卫
onBeforeRouteLeave(async (to, from, next) => {
  if (isEditing.value && !(await confirmDiscardChanges())) {
    next(false)
  } else {
    next()
  }
})

onMounted(async () => {
  await loadNotes()
})
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-900 h-[calc(100vh-64px)]">
    <div class="container mx-auto px-4 py-6 h-full flex flex-col md:flex-row">
      <!-- Notes List Sidebar -->
      <div
        class="w-full md:w-1/3 flex-col h-full"
        :class="[isEditing || isViewing ? 'hidden md:flex' : 'flex']"
      >
        <div class="flex justify-between items-center mb-4 px-2">
          <div>
            <h1 class="text-3xl font-bold">📝 笔记管理</h1>
            <p class="text-gray-600 dark:text-gray-400 mt-1">管理您的笔记</p>
          </div>
          <div class="flex items-center gap-2">
            <button
              class="btn btn-ghost btn-sm"
              :disabled="loading"
              :aria-busy="loading ? 'true' : 'false'"
              aria-label="Refresh"
              @click="handleRefresh"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-4 h-4"
                :class="{ 'animate-spin': loading }"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M21 3V8M21 8H16M21 8L18 5.29168C16.4077 3.86656 14.3051 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21C16.2832 21 19.8675 18.008 20.777 14"
                />
              </svg>
            </button>
            <button class="btn btn-primary btn-sm" @click="handleCreate">新建笔记</button>
          </div>
        </div>

        <div v-if="loading && notes.length === 0" class="flex justify-center p-4">
          <span class="loading loading-spinner"></span>
        </div>

        <div v-else class="flex-1 overflow-y-auto space-y-2 p-2">
          <div
            v-for="note in notes"
            :key="note.id"
            class="card bg-base-100 shadow-md hover:bg-base-200 cursor-pointer transition-colors"
            :class="{ 'ring-2 ring-primary': selectedNote?.id === note.id }"
            @click="handleView(note)"
          >
            <div class="card-body p-4">
              <h3 class="font-bold truncate">{{ note.title || 'Untitled Note' }}</h3>
              <p class="text-xs text-base-content/60 line-clamp-2">{{ note.content }}</p>
              <div class="flex justify-between items-center mt-2">
                <span class="flex-1 text-xs text-base-content/40">{{
                  formatDate(note.updated_at)
                }}</span>
                <div class="flex gap-1">
                  <span v-if="note.folders && note.folders.length > 0" class="badge"
                    >📁 {{ note.folders.length }}</span
                  >
                  <span v-if="note.files && note.files.length > 0" class="badge"
                    >📎 {{ note.files.length }}</span
                  >
                </div>
              </div>
            </div>
          </div>

          <div v-if="notes.length === 0 && !loading" class="text-center text-base-content/50 py-8">
            No notes found.
          </div>
        </div>

        <div v-if="totalPages > 1" class="p-2 border-t border-base-200">
          <div class="join flex justify-center">
            <button
              class="join-item btn btn-sm"
              :disabled="currentPage === 1"
              @click="handlePageChange(currentPage - 1)"
            >
              «
            </button>
            <button class="join-item btn btn-sm">Page {{ currentPage }}</button>
            <button
              class="join-item btn btn-sm"
              :disabled="currentPage === totalPages"
              @click="handlePageChange(currentPage + 1)"
            >
              »
            </button>
          </div>
        </div>
      </div>

      <!-- main Content / Editor / Preview -->
      <div
        class="flex-1 h-full md:ml-4 pb-2 overflow-auto"
        :class="{ 'hidden md:block': !isEditing && !isViewing }"
      >
        <!-- Editor -->
        <NoteEditor
          v-if="isEditing"
          :note="selectedNote"
          @save="handleSave"
          @auto-save="handleAutoSave"
          @cancel="handleCancel"
          @update:is-dirty="handleDirtyUpdate"
        />

        <!-- Preview -->
        <div
          v-else-if="isViewing && selectedNote"
          class="h-full flex flex-col bg-base-100 rounded-box shadow-md"
        >
          <!-- Preview Header -->
          <div class="p-4 border-b border-base-200">
            <div class="flex justify-between items-center">
              <button class="btn btn-ghost btn-sm md:hidden" @click="isViewing = false">
                ← 返回
              </button>
              <div class="flex-1"></div>
              <div class="flex gap-2">
                <button class="btn btn-outline btn-sm" @click="handleDetail(selectedNote)">
                  🔗 打开
                </button>
                <button
                  class="btn btn-error btn-sm btn-outline"
                  @click="handleDelete(selectedNote.id)"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                  删除
                </button>
                <button class="btn btn-primary btn-sm" @click="handleEdit(selectedNote)">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                  编辑
                </button>
              </div>
            </div>

            <!-- Preview Content -->
            <h1 class="text-3xl font-bold py-4">{{ selectedNote.title || 'Untitled Note' }}</h1>

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
                <span>创建于 {{ formatDate(selectedNote.created_at) }}</span>
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
                <span>更新于 {{ formatDate(selectedNote.updated_at) }}</span>
              </div>
            </div>
          </div>

          <div class="flex-1 overflow-y-auto px-6">
            <!-- 关联文件夹列表 -->
            <div
              v-if="selectedNote.folders && selectedNote.folders.length > 0"
              class="border-b border-gray-200 dark:border-gray-700 mt-3 pb-4"
            >
              <h3 class="text-sm font-medium mb-3 flex items-center gap-2">
                <span>📁</span>
                <span>关联的文件夹 ({{ selectedNote.folders.length }})</span>
              </h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                <div
                  v-for="folder in selectedNote.folders"
                  :key="folder.id"
                  class="flex items-center gap-3 p-3 bg-base-200 hover:bg-base-300 rounded-lg cursor-pointer transition-colors"
                  @click="handleFolderClick(folder)"
                >
                  <div class="text-2xl shrink-0">📁</div>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium truncate text-sm">{{ folder.name }}</p>
                    <p class="text-xs text-base-content/60">
                      {{ formatDate(folder.updated_at) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 关联文件列表 -->
            <div
              v-if="selectedNote.files && selectedNote.files.length > 0"
              class="border-b border-gray-200 dark:border-gray-700 mt-3 pb-4"
            >
              <h3 class="text-sm font-medium mb-3 flex items-center gap-2">
                <span>📎</span>
                <span>关联的文件 ({{ selectedNote.files.length }})</span>
              </h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                <div
                  v-for="file in selectedNote.files"
                  :key="file.id"
                  class="flex items-center gap-3 p-3 bg-base-200 hover:bg-base-300 rounded-lg cursor-pointer transition-colors"
                  @click="handleFileClick(file)"
                >
                  <div
                    :class="`w-10 h-10 rounded-lg flex items-center justify-center text-lg shrink-0 ${getFileTypeColor(file.mime_type)}`"
                  >
                    {{ getFileIcon(file.mime_type) }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium truncate text-sm">{{ file.filename }}</p>
                    <p class="text-xs text-base-content/60">{{ formatSize(file.size) }}</p>
                  </div>
                  <svg
                    class="w-5 h-5 text-base-content/40 shrink-0"
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
            <!-- 笔记内容 -->
            <div class="prose dark:prose-invert max-w-none overflow-auto">
              <div v-html="renderedContent"></div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-else
          class="h-full flex flex-col items-center justify-center text-base-content/30 bg-base-200 rounded-box"
        >
          <span class="text-6xl mb-4">📝</span>
          <p class="text-xl">Select a note to view or edit</p>
        </div>
      </div>
    </div>

    <!-- 文件详情弹窗 -->
    <FileDetails
      :file-id="detailsFile && detailsFile.id"
      :is-open="showDetails"
      @close="handleCloseDetails"
      @delete="handleDeleteFile"
    />
  </div>
</template>
