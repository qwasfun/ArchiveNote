<script setup>
import { ref, watch } from 'vue'
import { formatDate, formatSize } from '@/utils/format'
import {
  getFileIcon,
  getFileTypeColor,
  isImage,
  isVideo,
  isAudio,
  isPdf,
  isText,
} from '@/utils/file'

import PDFViewer from '@/components/PDFViewer.vue'
import TextViewer from '@/components/TextViewer.vue'
import fileService from '../api/fileService'

const props = defineProps({
  // 当模态框打开才有 fileId
  fileId: {
    type: String,
    // required: true,
  },
  isOpen: {
    type: Boolean,
    default: false,
  },
  showRename: {
    type: Boolean,
    default: false,
  },
  showManageNotes: {
    type: Boolean,
    default: false,
  },
  showDelete: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close', 'manage-notes', 'rename', 'delete', 'download'])

const file = ref(null)

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('已复制到剪贴板')
  } catch (err) {
    console.error('复制失败:', err)
  }
}

const getFileExtension = (filename) => {
  const parts = filename?.split('.')
  return parts && parts.length > 1 ? parts.pop().toUpperCase() : 'FILE'
}

const close = () => {
  emit('close')
}

watch(
  () => props.isOpen,
  async (newVal) => {
    try {
      const id = props.fileId
      if (newVal && id) {
        const response = await fileService.getFile(id)
        file.value = response
      }
    } catch (error) {
      console.error('Failed to load file', error)
    }
  },
)
</script>

<template>
  <div
    v-if="isOpen && file"
    class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
    @click.self="close"
  >
    <div
      class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col"
    >
      <!-- 头部 -->
      <div
        class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700"
      >
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div :class="`text-3xl ${getFileTypeColor(file.mime_type)}`">
            {{ getFileIcon(file.mime_type) }}
          </div>
          <div class="flex-1 min-w-0">
            <h2
              class="text-xl font-bold text-gray-900 dark:text-gray-100 truncate"
              :title="file.filename"
            >
              {{ file.filename }}
            </h2>
            <p class="flex gap-3 text-sm text-gray-500 dark:text-gray-400 mt-1">
              <span class="badge badge-outline">{{ getFileExtension(file.filename) }} 文件</span>
              <span class="badge badge-outline badge-warning">在回收站</span>
            </p>
          </div>
        </div>
        <button
          @click="close"
          class="btn btn-sm btn-circle btn-ghost text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
      <!-- 内容区域 -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <!-- 预览区域 -->

        <!-- 图片预览 -->
        <div
          v-if="isImage(file.mime_type)"
          class="flex items-center justify-center bg-gray-50 dark:bg-gray-800 h-full"
        >
          <img
            :src="`${file.preview_url}`"
            :alt="file.filename"
            class="max-w-full max-h-full object-contain rounded-lg shadow-lg"
          />
        </div>

        <!-- 视频预览 -->
        <div
          v-else-if="isVideo(file.mime_type)"
          class="flex items-center justify-center bg-black h-full"
        >
          <video
            :src="`${file.preview_url}`"
            controls
            class="max-w-full max-h-full rounded-lg shadow-lg"
          >
            您的浏览器不支持视频播放
          </video>
        </div>

        <!-- PDF预览 -->
        <PDFViewer v-else-if="isPdf(file.mime_type)" :url="file.preview_url" />

        <!-- 音频预览 -->
        <div v-else-if="isAudio(file.mime_type)" class="flex items-center justify-center p-8">
          <div class="w-full max-w-md">
            <div class="text-center mb-6">
              <div
                class="w-24 h-24 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-4xl mx-auto mb-4"
              >
                🎵
              </div>
              <h3 class="font-medium text-gray-900 dark:text-gray-100">
                {{ file.filename }}
              </h3>
            </div>
            <audio :src="`${file.preview_url}`" controls class="w-full">
              您的浏览器不支持音频播放
            </audio>
          </div>
        </div>

        <!-- 文本文件预览 -->
        <TextViewer v-else-if="isText(file.mime_type)" :url="file.preview_url" class="p-4 h-full" />

        <!-- 其他文件类型 -->
        <div v-else class="flex flex-col items-center justify-center p-12 text-center">
          <div
            :class="`w-24 h-24 rounded-full flex items-center justify-center text-4xl mb-6 ${getFileTypeColor(file.mime_type)}`"
          >
            {{ getFileIcon(file.mime_type) }}
          </div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            {{ file.filename }}
          </h3>
          <p class="text-gray-500 dark:text-gray-400 mb-6">
            此文件类型 ({{ file.mime_type }}) 暂不支持预览
          </p>
          <a :href="`${file.download_url}`" target="_blank" download class="btn btn-primary">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              ></path>
            </svg>
            下载文件
          </a>
        </div>
        <!-- 基本信息 -->
        <div class="bg-gray-50 dark:bg-gray-900 rounded-xl p-6">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">📋 基本信息</h3>
          <div class="space-y-3">
            <!-- 文件名 -->
            <div class="flex justify-between items-start">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">文件名</span>
              <div class="flex items-center gap-2">
                <span
                  class="text-sm text-gray-900 dark:text-gray-100 text-right max-w-md break-all"
                >
                  {{ file.filename }}
                </span>
                <button
                  @click="copyToClipboard(file.filename)"
                  class="btn btn-xs btn-ghost text-gray-400 hover:text-blue-500"
                  title="复制文件名"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <!-- 文件大小 -->
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">文件大小</span>
              <span class="text-sm text-gray-900 dark:text-gray-100 font-mono">
                {{ formatSize(file.size) }}
              </span>
            </div>

            <!-- MIME 类型 -->
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">文件类型</span>
              <span class="text-sm text-gray-900 dark:text-gray-100 font-mono">
                {{ file.mime_type }}
              </span>
            </div>

            <!-- 文件哈希 -->
            <div class="flex justify-between items-start">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">文件哈希</span>
              <div class="flex items-center gap-2">
                <span
                  class="text-sm text-gray-900 dark:text-gray-100 font-mono text-right break-all max-w-md"
                >
                  {{ file.hash }}
                </span>
                <button
                  v-if="file.hash"
                  @click="copyToClipboard(file.hash)"
                  class="btn btn-xs btn-ghost text-gray-400 hover:text-blue-500"
                  title="复制哈希值"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <!-- 存储路径 -->
            <div class="flex justify-between items-start">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">存储路径</span>
              <span
                class="text-sm text-gray-900 dark:text-gray-100 font-mono text-right break-all max-w-md"
              >
                {{ file.storage_path }}
              </span>
            </div>
          </div>
        </div>

        <!-- 时间信息 -->
        <div class="bg-gray-50 dark:bg-gray-900 rounded-xl p-6">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">⏰ 时间信息</h3>
          <div class="space-y-3">
            <!-- 上传时间 -->
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">上传时间</span>
              <span class="text-sm text-gray-900 dark:text-gray-100">
                {{ formatDate(file.created_at) }}
              </span>
            </div>

            <!-- 修改时间 -->
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">修改时间</span>
              <span class="text-sm text-gray-900 dark:text-gray-100">
                {{ formatDate(file.updated_at) }}
              </span>
            </div>

            <!-- 原始创建时间 -->
            <div v-if="file.original_created_at" class="flex justify-between items-center">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">原始创建时间</span>
              <span class="text-sm text-gray-900 dark:text-gray-100">
                {{ formatDate(file.original_created_at) }}
              </span>
            </div>

            <!-- 原始修改时间 -->
            <div v-if="file.original_modified_at" class="flex justify-between items-center">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">原始修改时间</span>
              <span class="text-sm text-gray-900 dark:text-gray-100">
                {{ formatDate(file.original_modified_at) }}
              </span>
            </div>
          </div>
        </div>

        <!-- 其他信息 -->
        <div class="bg-gray-50 dark:bg-gray-900 rounded-xl p-6">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">💡 其他信息</h3>
          <div class="space-y-3">
            <!-- 文件 ID -->
            <div class="flex justify-between items-start">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">文件 ID</span>
              <div class="flex items-center gap-2">
                <span
                  class="text-sm text-gray-900 dark:text-gray-100 font-mono text-right break-all max-w-md"
                >
                  {{ file.id }}
                </span>
                <button
                  @click="copyToClipboard(file.id)"
                  class="btn btn-xs btn-ghost text-gray-400 hover:text-blue-500"
                  title="复制 ID"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <!-- 笔记数量 -->
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">关联笔记</span>
              <span class="text-sm text-gray-900 dark:text-gray-100">
                {{ file.notes_count || 0 }} 条
              </span>
            </div>

            <!-- 文件夹 ID -->
            <div v-if="file.folder_id" class="flex justify-between items-start">
              <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">所属文件夹</span>
              <span
                class="text-sm text-gray-900 dark:text-gray-100 font-mono text-right break-all max-w-md"
              >
                {{ file.folder_id }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div
        class="flex flex-wrap sm:flex-row items-center justify-between gap-4 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900"
      >
        <div class="flex gap-2">
          <button
            v-if="showRename"
            @click="$emit('rename', file)"
            class="btn btn-sm btn-outline gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
            重命名
          </button>
          <button
            v-if="showDelete"
            @click="$emit('delete', file.id)"
            class="btn btn-sm btn-outline btn-error gap-2"
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
        </div>
        <div class="flex gap-2">
          <button
            v-if="showManageNotes"
            @click="$emit('manage-notes', file, 'file')"
            class="btn btn-sm btn-primary gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
            管理笔记
            <span v-if="file.notes_count > 0" class="badge badge-sm">{{ file.notes_count }}</span>
          </button>
          <router-link
            :to="{ name: 'file-detail', params: { id: file.id } }"
            class="btn btn-sm btn-info"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            详情
          </router-link>
          <a
            :href="file.download_url"
            target="_blank"
            download
            class="btn btn-sm btn-success gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            下载文件
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
