<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
    @click.self="$emit('close')"
  >
    <div
      class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden"
    >
      <!-- 头部 -->
      <div
        class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700"
      >
        <div class="flex items-center gap-3">
          <div
            :class="`w-10 h-10 rounded-full flex items-center justify-center text-lg ${getFileTypeColor(file?.mime_type)}`"
          >
            {{ getFileIcon(file?.mime_type) }}
          </div>
          <div>
            <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
              {{ isEditing ? (editingNote?.id ? '编辑笔记' : '添加笔记') : '文件笔记' }}
            </h2>
            <p class="text-sm text-gray-500">{{ file?.filename }}</p>
          </div>
        </div>
        <button @click="$emit('close')" class="btn btn-sm btn-circle btn-ghost">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>

      <!-- 内容区域 -->
      <div class="flex-1 overflow-hidden flex">
        <!-- 左侧：笔记列表 -->
        <div class="w-1/3 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          <div class="p-4 border-b border-gray-200 dark:border-gray-700">
            <button @click="startNewNote" class="w-full btn btn-primary btn-sm">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4v16m8-8H4"
                ></path>
              </svg>
              新建笔记
            </button>
          </div>

          <div class="flex-1 overflow-y-auto">
            <div v-if="loading" class="flex justify-center p-6">
              <span class="loading loading-spinner loading-md"></span>
            </div>

            <div v-else-if="notes.length === 0" class="p-6 text-center text-gray-500">
              <svg
                class="w-12 h-12 mx-auto mb-3 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
              <p class="text-sm">暂无笔记</p>
            </div>

            <div v-else class="space-y-2 p-4">
              <div
                v-for="note in notes"
                :key="note.id"
                :class="[
                  'p-3 rounded-lg border cursor-pointer transition-colors',
                  selectedNote?.id === note.id
                    ? 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-700'
                    : 'bg-gray-50 border-gray-200 hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700',
                ]"
                @click="selectNote(note)"
              >
                <h4 class="font-medium text-sm text-gray-900 dark:text-gray-100 mb-1 line-clamp-1">
                  {{ note.title || '无标题' }}
                </h4>
                <p class="text-xs text-gray-500 line-clamp-2">
                  {{ note.content }}
                </p>
                <div class="flex items-center justify-between mt-2">
                  <span class="text-xs text-gray-400">
                    {{ formatDate(note.updated_at) }}
                  </span>
                  <div class="flex gap-1">
                    <button
                      @click.stop="editNote(note)"
                      class="btn btn-xs btn-ghost text-gray-400 hover:text-blue-500"
                      title="编辑"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                        ></path>
                      </svg>
                    </button>
                    <button
                      @click.stop="deleteNote(note.id)"
                      class="btn btn-xs btn-ghost text-gray-400 hover:text-red-500"
                      title="删除"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        ></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：笔记内容/编辑器 -->
        <div class="flex-1 flex flex-col">
          <!-- 编辑模式 -->
          <div v-if="isEditing" class="flex-1 flex flex-col">
            <div class="p-4 border-b border-gray-200 dark:border-gray-700">
              <input
                v-model="editingNote.title"
                placeholder="笔记标题..."
                class="w-full px-2 py-2 border border-gray-300 dark:border-gray-600 rounded-xl text-lg font-medium bg-transparent focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 dark:text-gray-100 placeholder-gray-400"
              />
            </div>
            <div class="flex-1 p-4">
              <textarea
                v-model="editingNote.content"
                placeholder="在这里记录您的想法..."
                class="w-full h-64 px-2 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 resize-none"
              ></textarea>
            </div>
            <div class="p-4 border-t border-gray-200 dark:border-gray-700 flex gap-2 justify-end">
              <button @click="cancelEdit" class="btn btn-sm btn-ghost">取消</button>
              <button
                @click="saveNote"
                class="btn btn-sm btn-primary"
                :disabled="!editingNote.title?.trim() || !editingNote.content?.trim()"
              >
                保存
              </button>
            </div>
          </div>

          <!-- 查看模式 -->
          <div v-else-if="selectedNote" class="flex-1 flex flex-col">
            <div class="p-6">
              <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
                {{ selectedNote.title }}
              </h3>
              <div class="text-sm text-gray-500 mb-4">
                创建于 {{ formatDate(selectedNote.created_at) }}
                <span v-if="selectedNote.updated_at !== selectedNote.created_at">
                  · 更新于 {{ formatDate(selectedNote.updated_at) }}
                </span>
              </div>
              <div class="prose prose-sm max-w-none dark:prose-invert">
                <pre class="whitespace-pre-wrap font-sans text-gray-700 dark:text-gray-300">{{
                  selectedNote.content
                }}</pre>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else class="flex-1 flex items-center justify-center">
            <div class="text-center text-gray-500">
              <svg
                class="w-16 h-16 mx-auto mb-4 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
              <p>选择一个笔记查看内容</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import noteService from '../api/noteService.js'

const props = defineProps({
  isOpen: Boolean,
  file: Object,
})

const emit = defineEmits(['close', 'noteCreated'])

const notes = ref([])
const selectedNote = ref(null)
const isEditing = ref(false)
const editingNote = ref({ title: '', content: '', file_id: null })
const loading = ref(false)

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString()
}

const getFileIcon = (mimeType) => {
  if (!mimeType) return '📁'
  if (mimeType.startsWith('image/')) return '🖼️'
  if (mimeType.startsWith('video/')) return '🎥'
  if (mimeType === 'application/pdf') return '📄'
  if (mimeType.startsWith('audio/')) return '🎵'
  if (mimeType.includes('document') || mimeType.includes('word')) return '📝'
  if (mimeType.includes('sheet') || mimeType.includes('excel')) return '📊'
  if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return '📋'
  if (mimeType.includes('zip') || mimeType.includes('archive')) return '🗜️'
  return '📁'
}

const getFileTypeColor = (mimeType) => {
  if (!mimeType) return 'bg-gray-100 text-gray-600'
  if (mimeType.startsWith('image/')) return 'bg-green-100 text-green-600'
  if (mimeType.startsWith('video/')) return 'bg-blue-100 text-blue-600'
  if (mimeType === 'application/pdf') return 'bg-red-100 text-red-600'
  if (mimeType.startsWith('audio/')) return 'bg-purple-100 text-purple-600'
  return 'bg-gray-100 text-gray-600'
}

const loadNotes = async () => {
  if (!props.file?.id) return

  loading.value = true
  try {
    // 这里假设API支持按文件ID过滤笔记
    const response = await noteService.getNotesByFileId(props.file.id)
    notes.value = response.data || []
  } catch (error) {
    console.error('Failed to load notes', error)
    notes.value = []
  } finally {
    loading.value = false
  }
}

const selectNote = (note) => {
  if (!isEditing.value) {
    selectedNote.value = note
  }
}

const startNewNote = () => {
  editingNote.value = {
    title: `关于文件 "${props.file?.filename}" 的笔记`,
    content: '',
    file_id: props.file?.id,
  }
  isEditing.value = true
  selectedNote.value = null
}

const editNote = (note) => {
  editingNote.value = { ...note }
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
  editingNote.value = { title: '', content: '', file_id: null }
}

const saveNote = async () => {
  try {
    if (editingNote.value.id) {
      await noteService.updateNote(editingNote.value.id, {
        title: editingNote.value.title,
        content: editingNote.value.content,
      })
    } else {
      const newNote = await noteService.createNote({
        title: editingNote.value.title,
        content: editingNote.value.content,
      })

      if (editingNote.value.file_id) {
        await noteService.attachFiles(newNote.id, [editingNote.value.file_id])
      }
    }

    isEditing.value = false
    await loadNotes()
    emit('noteCreated')
  } catch (error) {
    console.error('Failed to save note', error)
  }
}

const deleteNote = async (noteId) => {
  if (!confirm('确定要删除这个笔记吗？')) return

  try {
    await noteService.deleteNote(noteId)
    if (selectedNote.value?.id === noteId) {
      selectedNote.value = null
    }
    await loadNotes()
  } catch (error) {
    console.error('Failed to delete note', error)
  }
}

// 监听文件变化，重新加载笔记
watch(
  () => props.file?.id,
  (newFileId) => {
    if (newFileId) {
      loadNotes()
      selectedNote.value = null
      isEditing.value = false
    }
  },
)

// 监听打开状态
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen && props.file?.id) {
      loadNotes()
    } else if (!isOpen) {
      selectedNote.value = null
      isEditing.value = false
    }
  },
)
</script>
