<script setup>
import { ref } from 'vue'

defineProps({
  files: {
    type: Array,
    required: true,
    default: () => [],
  },
})

defineEmits(['delete-file', 'preview-file', 'add-note', 'view-notes'])

const hoveredFile = ref(null)

const formatSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString()
}

const isImage = (mimeType) => mimeType.startsWith('image/')

const getFileIcon = (mimeType) => {
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
  if (mimeType.startsWith('image/')) return 'bg-green-100 text-green-600'
  if (mimeType.startsWith('video/')) return 'bg-blue-100 text-blue-600'
  if (mimeType === 'application/pdf') return 'bg-red-100 text-red-600'
  if (mimeType.startsWith('audio/')) return 'bg-purple-100 text-purple-600'
  return 'bg-gray-100 text-gray-600'
}
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    <div
      v-for="file in files"
      :key="file.id"
      class="group bg-white dark:bg-gray-800 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 dark:border-gray-700"
      @mouseenter="hoveredFile = file.id"
      @mouseleave="hoveredFile = null"
    >
      <!-- 文件预览区域 -->
      <div
        class="relative h-48 bg-linear-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 flex items-center justify-center overflow-hidden cursor-pointer group-hover:scale-105 transition-transform duration-300"
        @click="$emit('preview-file', file)"
      >
        <!-- 图片预览 -->
        <img
          v-if="isImage(file.mime_type)"
          :src="`${file.download_url}`"
          :alt="file.filename"
          class="w-full h-full object-cover"
        />
        <!-- 文件类型图标 -->
        <div v-else class="flex flex-col items-center justify-center p-4">
          <div
            :class="`w-16 h-16 rounded-full flex items-center justify-center text-2xl ${getFileTypeColor(file.mime_type)}`"
          >
            {{ getFileIcon(file.mime_type) }}
          </div>
          <span class="mt-2 text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">{{
            file.mime_type.split('/')[1]
          }}</span>
        </div>

        <!-- 悬浮操作按钮 -->
        <div
          v-if="hoveredFile === file.id"
          class="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200"
        >
          <div class="flex gap-2">
            <button
              @click.stop="$emit('preview-file', file)"
              class="btn btn-sm btn-circle bg-white/90 hover:bg-white text-gray-700 border-0 shadow-lg"
              title="预览文件"
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
            <button
              @click.stop="$emit('add-note', file)"
              class="btn btn-sm btn-circle bg-blue-500 hover:bg-blue-600 text-white border-0 shadow-lg"
              title="添加笔记"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4v16m8-8H4"
                ></path>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 文件信息 -->
      <div class="p-4 space-y-3">
        <div class="flex items-start justify-between">
          <h3
            class="font-medium text-gray-900 dark:text-gray-100 text-sm leading-tight line-clamp-2 flex-1 mr-2"
            :title="file.filename"
          >
            {{ file.filename }}
          </h3>
          <div class="shrink-0">
            <button
              @click="$emit('view-notes', file)"
              class="btn btn-xs btn-ghost btn-circle text-gray-400 hover:text-blue-500"
              :class="{ 'text-blue-500': file.notes_count > 0 }"
              :title="`查看笔记 (${file.notes_count || 0})`"
            >
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"></path>
                <path
                  fill-rule="evenodd"
                  d="M4 5a2 2 0 012-2v1a1 1 0 001 1h6a1 1 0 001-1V3a2 2 0 012 2v6.5a1.5 1.5 0 01-1.5 1.5h-9A1.5 1.5 0 014 11.5V5z"
                  clip-rule="evenodd"
                ></path>
              </svg>
              <span v-if="file.notes_count > 0" class="text-xs">{{ file.notes_count }}</span>
            </button>
          </div>
        </div>

        <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>{{ formatSize(file.size) }}</span>
          <span>{{ formatDate(file.created_at) }}</span>
        </div>

        <!-- 操作按钮 -->
        <div class="flex gap-2 pt-2 border-t border-gray-100 dark:border-gray-700">
          <a
            :href="`${file.download_url}`"
            target="_blank"
            download
            class="btn btn-xs btn-ghost flex-1 text-gray-600 hover:text-blue-600"
          >
            <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              ></path>
            </svg>
            下载
          </a>
          <button
            class="btn btn-xs btn-ghost text-red-500 hover:text-red-600"
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
        </div>
      </div>
    </div>
  </div>
</template>
