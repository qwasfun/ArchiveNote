<script setup>
import { ref, watch, computed, onBeforeUnmount } from 'vue'
import noteService from '../api/noteService'
import FileFolderSelector from './FileFolderSelector.vue'
import { useToast } from '@/composables/useToast'
import { getFileIcon, getFileTypeColor } from '@/utils/file'
import { formatSize } from '@/utils/format'

const props = defineProps({
  note: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['save', 'cancel', 'auto-save', 'update:isDirty'])

const title = ref('')
const content = ref('')
const attachedFiles = ref([])
const attachedFolders = ref([])
const showSelector = ref(false)

const lastSavedState = ref({ title: '', content: '' })
const saveStatus = ref('')
let autoSaveTimer = null
const currentNoteId = ref(null)

const { showToast } = useToast()

const isDirty = computed(() => {
  return (
    title.value !== lastSavedState.value.title || content.value !== lastSavedState.value.content
  )
})

watch(isDirty, (newVal) => {
  emit('update:isDirty', newVal)
})

// 监听属性变化
watch(
  () => props.note,
  (newNote, oldNote) => {
    // 如果ID改变了，或者之前没有ID（新建），则视为切换了笔记，需要重置状态
    // 如果是同一个ID，可能是自动保存后的更新，尽量不打断用户输入
    const isNewNote = !oldNote || newNote?.id !== oldNote.id

    if (newNote) {
      if (isNewNote) {
        title.value = newNote.title || ''
        content.value = newNote.content || ''
        attachedFiles.value = newNote.files || []
        attachedFolders.value = newNote.folders || []
        currentNoteId.value = newNote.id

        // 更新最后保存状态
        lastSavedState.value = {
          title: newNote.title || '',
          content: newNote.content || '',
        }
      } else {
        // 同一个笔记更新，只更新非编辑字段
        attachedFiles.value = newNote.files || []
        attachedFolders.value = newNote.folders || []
      }
    } else {
      saveStatus.value = ''
      title.value = ''
      content.value = ''
      attachedFiles.value = []
      attachedFolders.value = []
      currentNoteId.value = null
      lastSavedState.value = { title: '', content: '' }
    }
  },
  { immediate: true, deep: true },
)

// 自动保存逻辑
const triggerAutoSave = () => {
  if (!title.value.trim() && !content.value.trim()) return

  saveStatus.value = '正在保存...'
  emit(
    'auto-save',
    {
      title: title.value,
      content: content.value,
    },
    (success) => {
      if (success) {
        saveStatus.value = '已自动保存'
        lastSavedState.value = {
          title: title.value,
          content: content.value,
        }
      } else {
        saveStatus.value = '自动保存失败'
      }
    },
  )
}

// 监听内容变化触发自动保存
watch([title, content], () => {
  if (isDirty.value) {
    saveStatus.value = '有未保存内容'
    clearTimeout(autoSaveTimer)
    autoSaveTimer = setTimeout(triggerAutoSave, 2000)
  }
})

onBeforeUnmount(() => {
  clearTimeout(autoSaveTimer)
})

// 事件处理
const handleManualSave = () => {
  if (!title.value.trim() && !content.value.trim()) {
    return
  }

  // 手动保存时，清除自动保存定时器，避免重复提交
  clearTimeout(autoSaveTimer)

  // 更新最后保存状态，防止isDirty误判
  lastSavedState.value = {
    title: title.value,
    content: content.value,
  }

  emit('save', {
    title: title.value,
    content: content.value,
  })
}

const handleShowSelector = () => {
  if (!props.note || !props.note.id) {
    showToast('请先保存笔记，再关联文件和文件夹', 'warning')
    return
  }
  showSelector.value = true
}

const handleAttachItems = async ({ files: fileIds, folders: folderIds }) => {
  showSelector.value = false

  if (!props.note || !props.note.id) {
    showToast('请先保存笔记，再关联文件和文件夹', 'warning')
    return
  }

  try {
    // 同时关联文件和文件夹
    const promises = []
    if (fileIds.length > 0) {
      promises.push(noteService.attachFiles(props.note.id, fileIds))
    }
    if (folderIds.length > 0) {
      promises.push(noteService.attachFolders(props.note.id, folderIds))
    }

    await Promise.all(promises)

    // 重新获取笔记信息以更新关联列表
    const response = await noteService.getNote(props.note.id)
    attachedFiles.value = response.files || []
    attachedFolders.value = response.folders || []
  } catch (error) {
    console.error('Failed to attach items', error)
    showToast('关联失败', 'error')
  }
}

const handleDetachFile = async (fileId) => {
  if (!props.note || !props.note.id) return

  if (!confirm('确定要移除这个文件的关联吗？')) return

  try {
    await noteService.detachFiles(props.note.id, [fileId])
    attachedFiles.value = attachedFiles.value.filter((file) => file.id !== fileId)
  } catch (error) {
    console.error('Failed to detach file', error)
    showToast('移除文件关联失败', 'error')
  }
}

const handleDetachFolder = async (folderId) => {
  if (!props.note || !props.note.id) return

  if (!confirm('确定要移除这个文件夹的关联吗？')) return

  try {
    await noteService.detachFolders(props.note.id, [folderId])
    attachedFolders.value = attachedFolders.value.filter((folder) => folder.id !== folderId)
  } catch (error) {
    console.error('Failed to detach folder', error)
    showToast('移除文件夹关联失败', 'error')
  }
}
</script>

<template>
  <div
    class="bg-white dark:bg-gray-900 rounded-2xl overflow-hidden shadow-xl border border-gray-200 dark:border-gray-700 h-full flex flex-col"
  >
    <!-- 头部工具栏 -->
    <div
      class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-11 h-11 bg-blue-500 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              ></path>
            </svg>
          </div>
          <div class="flex flex-col md:flex-row items-start md:items-center justify-center">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {{ note ? '编辑笔记' : '新建笔记' }}
            </h2>

            <div v-if="saveStatus" class="badge badge-info badge-xs md:mx-2">
              {{ saveStatus }}
            </div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button class="btn btn-sm btn-soft" @click="$emit('cancel')">
            ✖️ <span class="hidden sm:inline-block">取消</span>
          </button>
          <button
            class="btn btn-sm btn-primary"
            :disabled="!title.trim() && !content.trim()"
            @click="handleManualSave"
          >
            💾
            <span class="hidden sm:inline-block">保存并预览</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑区域 -->
    <div class="p-6 flex-1 flex flex-col gap-6 overflow-auto">
      <!-- 标题输入 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          笔记标题
        </label>
        <div class="flex items-center justify-between">
          <input
            v-model="title"
            type="text"
            placeholder="输入笔记标题..."
            class="w-full px-4 py-3 text-lg border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400"
          />
          <button class="btn btn-lg btn-primary ml-2 rounded-lg" @click="handleShowSelector">
            ＋ 关联
          </button>
        </div>
      </div>

      <!-- 关联文件夹 -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            关联的文件夹 ({{ attachedFolders.length }})
          </label>
        </div>
        <div
          v-if="attachedFolders.length > 0"
          class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3"
        >
          <div
            v-for="folder in attachedFolders"
            :key="folder.id"
            class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
            @click="handleFolderClick(folder)"
          >
            <div class="text-2xl">📁</div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {{ folder.name }}
              </p>
              <p class="text-xs text-gray-500">
                {{ new Date(folder.updated_at).toLocaleDateString() }}
              </p>
            </div>
            <button
              class="btn btn-xs btn-ghost text-gray-400 hover:text-red-500"
              title="移除关联"
              @click="handleDetachFolder(folder.id)"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                ></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
      <!-- 关联文件 -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            关联的文件 ({{ attachedFiles.length }})
          </label>
        </div>
        <div
          v-if="attachedFiles.length > 0"
          class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3"
        >
          <div
            v-for="file in attachedFiles"
            :key="file.id"
            class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
          >
            <div
              :class="`w-10 h-10 rounded-lg flex items-center justify-center text-sm ${getFileTypeColor(file.mime_type)}`"
            >
              {{ getFileIcon(file.mime_type) }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {{ file.filename }}
              </p>
              <p class="text-xs text-gray-500">
                {{ formatSize(file.size) }}
              </p>
            </div>
            <button
              class="btn btn-xs btn-ghost text-gray-400 hover:text-red-500"
              title="移除关联"
              @click="handleDetachFile(file.id)"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                ></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
      <!-- 内容编辑 -->
      <div class="flex-1 flex flex-col min-h-80">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          笔记内容
        </label>
        <div class="relative flex-1 flex flex-col">
          <textarea
            v-model="content"
            placeholder="在这里记录您的想法、心得或重要信息..."
            class="w-full h-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 resize-none"
          ></textarea>
          <div class="absolute bottom-3 right-3 text-xs text-gray-400">
            {{ content.length }} 字符
          </div>
        </div>
      </div>

      <!-- 工具栏 -->
      <div class="flex items-center justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
        <div class="text-xs text-gray-400">支持 Markdown 格式</div>
      </div>
    </div>

    <!-- 统一选择器模态框 -->
    <div
      v-if="showSelector"
      class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      @click.self="showSelector = false"
    >
      <div
        class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-5xl w-full h-[90vh] overflow-hidden flex flex-col"
      >
        <div
          class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700"
        >
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">选择文件和文件夹</h3>
          <button class="btn btn-sm btn-circle btn-ghost" @click="showSelector = false">
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
        <FileFolderSelector
          :exclude-file-ids="attachedFiles.map((f) => f.id)"
          :exclude-folder-ids="attachedFolders.map((f) => f.id)"
          mode="both"
          class="p-4 flex-1 overflow-hidden"
          @select="handleAttachItems"
          @cancel="showSelector = false"
        />
      </div>
    </div>
  </div>
</template>
