<script setup>
import { ref, watch } from 'vue'
import { formatDate, formatSize } from '@/utils/format'
import { getFileIcon, getFileTypeColor, isImage } from '@/utils/file'

const props = defineProps({
  files: {
    type: Array,
    required: false,
    default: () => [],
  },
  folders: {
    type: Array,
    default: () => [],
  },
  selectionMode: {
    type: Boolean,
    default: false,
  },
  selectedFiles: {
    type: Array,
    default: () => [],
  },
  selectedFolders: {
    type: Array,
    default: () => [],
  },
  isShowOperationBtn: {
    type: Boolean,
    default: true,
  },
  viewMode: {
    type: String,
    default: 'grid', // 'grid' or 'list'
  },
})

const emit = defineEmits([
  'delete-file',
  'manage-notes',
  'open-folder',
  'delete-folder',
  'edit-folder',
  'rename-file',
  'selection-change',
  'view-details',
])

const localSelectedFiles = ref([...props.selectedFiles])
const localSelectedFolders = ref([...props.selectedFolders])

watch(
  () => props.selectedFiles,
  (newVal) => {
    localSelectedFiles.value = [...newVal]
  },
)

watch(
  () => props.selectedFolders,
  (newVal) => {
    localSelectedFolders.value = [...newVal]
  },
)

const toggleFileSelection = (fileId) => {
  if (localSelectedFiles.value.includes(fileId)) {
    localSelectedFiles.value = localSelectedFiles.value.filter((id) => id !== fileId)
  } else {
    localSelectedFiles.value.push(fileId)
  }
  emitSelection()
}

const toggleFolderSelection = (folderId) => {
  if (localSelectedFolders.value.includes(folderId)) {
    localSelectedFolders.value = localSelectedFolders.value.filter((id) => id !== folderId)
  } else {
    localSelectedFolders.value.push(folderId)
  }
  emitSelection()
}

const emitSelection = () => {
  emit('selection-change', {
    files: localSelectedFiles.value,
    folders: localSelectedFolders.value,
  })
}

const hoveredFile = ref(null)
const hoveredFolder = ref(null)
</script>

<template>
  <div>
    <!-- 网格视图 -->
    <div v-if="viewMode === 'grid'">
      <!-- Folders Section -->
      <div v-if="folders.length > 0" class="mb-4">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-3 flex items-center">
          <span class="mr-1.5">📁</span> Folders ({{ folders.length }})
        </h3>

        <div
          class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-3"
        >
          <div
            v-for="folder in folders"
            :key="folder.id"
            class="relative group bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-all duration-200 overflow-hidden border border-gray-100 dark:border-gray-700"
            @click="$emit('open-folder', folder)"
            @mouseenter="hoveredFolder = folder.id"
            @mouseleave="hoveredFolder = null"
          >
            <div v-if="selectionMode" class="absolute top-1.5 left-1.5 z-10">
              <input
                type="checkbox"
                :checked="localSelectedFolders.includes(folder.id)"
                class="checkbox checkbox-sm checkbox-primary"
                @click.stop="toggleFolderSelection(folder.id)"
              />
            </div>
            <div
              class="relative h-32 bg-linear-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 flex items-center justify-center overflow-hidden cursor-pointer group-hover:scale-105 transition-transform duration-200"
              @click.stop="$emit('open-folder', folder)"
            >
              <!-- 文件夹图标 -->
              <div class="flex flex-col items-center justify-center p-2">
                <div
                  class="w-12 h-12 rounded-full flex items-center justify-center text-yellow-400 text-4xl"
                >
                  📁
                </div>
              </div>
            </div>

            <!-- 文件信息 -->
            <div class="p-2.5 space-y-2">
              <div class="flex items-center justify-between">
                <h3
                  class="font-medium text-gray-900 dark:text-gray-100 text-xs leading-tight line-clamp-2 flex-1 mr-1"
                  :title="folder.name"
                >
                  {{ folder.name }}
                </h3>
                <button
                  class="btn btn-xs btn-outline text-gray-400 hover:text-blue-500 min-h-0 h-6 px-1"
                  :class="{ 'text-blue-500': folder.notes_count > 0 }"
                  :title="`管理笔记 (${folder.notes_count || 0})`"
                  @click.stop="$emit('manage-notes', folder, 'folder')"
                >
                  📝
                  <span v-if="folder.notes_count > 0" class="text-xs">{{
                    folder.notes_count
                  }}</span>
                </button>
              </div>
              <!-- 操作按钮 -->
              <div
                class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 gap-1 pt-1.5 border-t border-gray-100 dark:border-gray-700"
              >
                <div class="flex-1">
                  <button
                    class="btn btn-xs btn-ghost text-gray-500 hover:text-blue-600 min-h-0 h-6 px-1"
                    @click.stop="$emit('edit-folder', folder)"
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
                    class="btn btn-xs btn-ghost text-red-500 hover:text-red-600 min-h-0 h-6 px-1"
                    @click.stop="$emit('delete-folder', folder)"
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
                <span>{{ formatDate(folder.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Files Section -->
      <div v-if="files.length > 0">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-3 flex items-center">
          <span class="mr-1.5">📄</span> Files ({{ files.length }})
        </h3>
        <div
          class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-3"
        >
          <div
            v-for="file in files"
            :key="file.id"
            class="relative group bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-all duration-200 overflow-hidden border border-gray-100 dark:border-gray-700"
            @mouseenter="hoveredFile = file.id"
            @mouseleave="hoveredFile = null"
          >
            <div v-if="selectionMode" class="absolute top-1.5 left-1.5 z-10">
              <input
                type="checkbox"
                :checked="localSelectedFiles.includes(file.id)"
                class="checkbox checkbox-sm checkbox-primary"
                @click.stop="toggleFileSelection(file.id)"
              />
            </div>
            <!-- 文件预览区域 -->
            <div
              class="relative h-32 bg-linear-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 flex items-center justify-center overflow-hidden cursor-pointer group-hover:scale-105 transition-transform duration-200"
              @click="$emit('view-details', file)"
            >
              <!-- 图片预览 -->
              <img
                v-if="isImage(file.mime_type)"
                :src="`${file.preview_url}`"
                :alt="file.filename"
                class="w-full h-full object-cover"
              />
              <!-- 文件类型图标 -->
              <div v-else class="flex flex-col items-center justify-center p-2">
                <div
                  :class="`w-16 h-16 rounded-full flex items-center justify-center text-4xl ${getFileTypeColor(file.mime_type)}`"
                >
                  {{ getFileIcon(file.mime_type) }}
                </div>
                <span
                  class="mt-1 text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide"
                  >{{ file.mime_type.split('/')[1] }}</span
                >
              </div>

              <!-- 悬浮操作按钮 -->
              <div
                v-if="hoveredFile === file.id"
                class="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200"
              >
                <div class="flex gap-2">
                  <button
                    class="btn btn-sm btn-circle bg-white/90 hover:bg-white text-gray-700 border-0 shadow-lg"
                    title="查看文件"
                    @click.stop="$emit('view-details', file)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      ></path>
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      ></path>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- 文件信息 -->
            <div class="p-2.5 space-y-1.5">
              <div class="flex items-center justify-between">
                <h3
                  class="font-medium text-gray-900 dark:text-gray-100 text-xs leading-tight line-clamp-2 flex-1 mr-1"
                  :title="file.filename"
                >
                  {{ file.filename }}
                </h3>
                <button
                  class="btn btn-xs btn-outline text-gray-400 hover:text-blue-500 min-h-0 h-6 px-1"
                  :class="{ 'text-blue-500': file.notes_count > 0 }"
                  :title="`管理笔记 (${file.notes_count || 0})`"
                  @click="$emit('manage-notes', file, 'file')"
                >
                  📝
                  <span v-if="file.notes_count > 0" class="text-xs">{{ file.notes_count }}</span>
                </button>
              </div>

              <div
                class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400"
              >
                <span>{{ formatSize(file.size) }}</span>
                <span>{{ formatDate(file.created_at) }}</span>
              </div>

              <!-- 操作按钮 -->
              <div
                v-if="isShowOperationBtn"
                class="flex gap-1 pt-1.5 border-t border-gray-100 dark:border-gray-700"
              >
                <button
                  class="btn btn-xs btn-ghost text-gray-500 hover:text-blue-600 min-h-0 h-6 px-1"
                  @click="$emit('view-details', file)"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </button>
                <button
                  class="btn btn-xs btn-ghost text-gray-500 hover:text-blue-600 min-h-0 h-6 px-1"
                  @click="$emit('rename-file', file)"
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
                  class="btn btn-xs btn-ghost text-red-500 hover:text-red-600 min-h-0 h-6 px-1"
                  @click="$emit('delete-file', file.id)"
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
                <a
                  :href="`${file.download_url}`"
                  target="_blank"
                  download
                  class="btn btn-xs btn-ghost flex-1 text-gray-600 hover:text-blue-600 min-h-0 h-6 px-1"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    ></path>
                  </svg>
                  下载
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div
        v-if="files.length === 0 && folders.length === 0"
        class="text-center py-12 text-gray-500"
      >
        No files or folders found
      </div>
    </div>

    <!-- 列表视图 -->
    <div v-else-if="viewMode === 'list'">
      <!-- Folders Section - List View -->
      <div v-if="folders.length > 0" class="mb-4">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-2 flex items-center">
          <span class="mr-1.5">📁</span> Folders ({{ folders.length }})
        </h3>
        <div class="space-y-1">
          <div
            v-for="folder in folders"
            :key="folder.id"
            class="flex items-center gap-3 p-2.5 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow transition-all duration-200 border border-gray-100 dark:border-gray-700 cursor-pointer"
            @click="$emit('open-folder', folder)"
          >
            <div v-if="selectionMode" class="flex-shrink-0">
              <input
                type="checkbox"
                :checked="localSelectedFolders.includes(folder.id)"
                class="checkbox checkbox-sm checkbox-primary"
                @click.stop="toggleFolderSelection(folder.id)"
              />
            </div>
            <div class="flex-shrink-0 w-10 h-10 flex items-center justify-center text-2xl">📁</div>
            <div class="flex-1 min-w-0">
              <h4 class="font-medium text-gray-900 dark:text-gray-100 text-sm truncate">
                {{ folder.name }}
              </h4>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatDate(folder.created_at) }}
              </p>
            </div>
            <div class="flex items-center gap-1">
              <button
                class="btn btn-xs btn-outline text-gray-400 hover:text-blue-500 min-h-0 h-7 px-1.5"
                :class="{ 'text-blue-500': folder.notes_count > 0 }"
                :title="`管理笔记 (${folder.notes_count || 0})`"
                @click.stop="$emit('manage-notes', folder, 'folder')"
              >
                📝
                <span v-if="folder.notes_count > 0" class="text-xs">{{ folder.notes_count }}</span>
              </button>
              <button
                class="btn btn-xs btn-ghost text-gray-500 hover:text-blue-600 min-h-0 h-7 px-1.5"
                @click.stop="$emit('edit-folder', folder)"
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
                class="btn btn-xs btn-ghost text-red-500 hover:text-red-600 min-h-0 h-7 px-1.5"
                @click.stop="$emit('delete-folder', folder)"
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

      <!-- Files Section - List View -->
      <div v-if="files.length > 0">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-2 flex items-center">
          <span class="mr-1.5">📄</span> Files ({{ files.length }})
        </h3>
        <div class="space-y-1">
          <div
            v-for="file in files"
            :key="file.id"
            class="flex items-center gap-3 p-2.5 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow transition-all duration-200 border border-gray-100 dark:border-gray-700 cursor-pointer"
            @click="$emit('view-details', file)"
          >
            <div v-if="selectionMode" class="flex-shrink-0">
              <input
                type="checkbox"
                :checked="localSelectedFiles.includes(file.id)"
                class="checkbox checkbox-sm checkbox-primary"
                @click.stop="toggleFileSelection(file.id)"
              />
            </div>
            <!-- 文件预览缩略图 -->
            <div
              class="flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700 flex items-center justify-center"
            >
              <img
                v-if="isImage(file.mime_type)"
                :src="`${file.preview_url}`"
                :alt="file.filename"
                class="w-full h-full object-cover"
              />
              <div v-else :class="`text-2xl ${getFileTypeColor(file.mime_type)}`">
                {{ getFileIcon(file.mime_type) }}
              </div>
            </div>
            <!-- 文件信息 -->
            <div class="flex-1 min-w-0">
              <h4 class="font-medium text-gray-900 dark:text-gray-100 text-sm truncate">
                {{ file.filename }}
              </h4>
              <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                <span>{{ formatSize(file.size) }}</span>
                <span>•</span>
                <span>{{ formatDate(file.created_at) }}</span>
                <span>•</span>
                <span class="uppercase">{{ file.mime_type.split('/')[1] }}</span>
              </div>
            </div>
            <!-- 操作按钮 -->
            <div v-if="isShowOperationBtn" class="flex items-center gap-1">
              <button
                class="btn btn-xs btn-outline text-gray-400 hover:text-blue-500 min-h-0 h-7 px-1.5"
                :class="{ 'text-blue-500': file.notes_count > 0 }"
                :title="`管理笔记 (${file.notes_count || 0})`"
                @click.stop="$emit('manage-notes', file, 'file')"
              >
                📝
                <span v-if="file.notes_count > 0" class="text-xs">{{ file.notes_count }}</span>
              </button>
              <button
                class="btn btn-xs btn-ghost text-gray-500 hover:text-blue-600 min-h-0 h-7 px-1.5"
                @click.stop="$emit('view-details', file)"
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </button>
              <button
                class="btn btn-xs btn-ghost text-gray-500 hover:text-blue-600 min-h-0 h-7 px-1.5"
                @click.stop="$emit('rename-file', file)"
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
                class="btn btn-xs btn-ghost text-red-500 hover:text-red-600 min-h-0 h-7 px-1.5"
                @click.stop="$emit('delete-file', file.id)"
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
              <a
                :href="`${file.download_url}`"
                target="_blank"
                download
                class="btn btn-xs btn-ghost text-gray-600 hover:text-blue-600 min-h-0 h-7 px-1.5"
                @click.stop
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  ></path>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="files.length === 0 && folders.length === 0"
        class="text-center py-12 text-gray-500"
      >
        No files or folders found
      </div>
    </div>
  </div>
</template>
