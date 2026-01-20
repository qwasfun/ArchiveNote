<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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
import fileService from '@/api/fileService.js'
import UnifiedNotes from '@/components/UnifiedNotes.vue'
import PDFViewer from '@/components/PDFViewer.vue'
import TextViewer from '@/components/TextViewer.vue'

const route = useRoute()
const router = useRouter()

const file = ref(null)
const loading = ref(false)
const showNotes = ref(false)
const showRenameModal = ref(false)
const newFileName = ref('')

const getFileExtension = (filename) => {
  const parts = filename?.split('.')
  return parts && parts.length > 1 ? parts.pop().toUpperCase() : 'FILE'
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('已复制到剪贴板')
  } catch (err) {
    console.error('复制失败:', err)
  }
}

const loadFile = async () => {
  loading.value = true
  try {
    const fileId = route.params.id
    // 通过获取文件列表来获取单个文件信息
    const response = await fileService.getFile(fileId)
    const foundFile = response
    if (foundFile) {
      file.value = foundFile
      newFileName.value = foundFile.filename
    } else {
      alert('文件不存在')
      router.push({ name: 'files' })
    }
  } catch (error) {
    console.error('加载文件失败:', error)
    alert('加载文件失败')
    router.push({ name: 'files' })
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const handleRename = async () => {
  if (!newFileName.value.trim()) return
  try {
    await fileService.renameFile(file.value.id, { filename: newFileName.value })
    showRenameModal.value = false
    await loadFile()
  } catch (error) {
    console.error('重命名失败:', error)
    alert('重命名失败')
  }
}

const handleDelete = async () => {
  if (!confirm(`确定要删除文件 "${file.value.filename}" 吗？`)) return
  try {
    await fileService.deleteFile(file.value.id)
    router.push({ name: 'files' })
  } catch (error) {
    console.error('删除失败:', error)
    alert('删除失败')
  }
}

const handleManageNotes = () => {
  showNotes.value = true
}

const closeNotes = () => {
  showNotes.value = false
  loadFile() // 刷新文件信息以更新笔记数量
}

onMounted(() => {
  loadFile()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center min-h-screen">
      <div class="text-center">
        <span class="loading loading-spinner loading-lg text-blue-500"></span>
        <p class="text-gray-500 mt-2">加载中...</p>
      </div>
    </div>

    <!-- 文件详情 -->
    <div v-else-if="file" class="container mx-auto px-4 py-6">
      <!-- 头部导航 -->
      <div class="mb-6">
        <button @click="goBack" class="btn btn-ghost gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10 19l-7-7m0 0l7-7m-7 7h18"
            />
          </svg>
          返回
        </button>
      </div>

      <!-- 主要内容区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧：文件预览 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 文件标题卡片 -->
          <div
            class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <div class="flex items-start gap-4">
              <div :class="`text-5xl ${getFileTypeColor(file.mime_type)}`">
                {{ getFileIcon(file.mime_type) }}
              </div>
              <div class="flex-1 min-w-0">
                <h1
                  class="text-3xl font-bold text-gray-900 dark:text-gray-100 break-words mb-2"
                  :title="file.filename"
                >
                  {{ file.filename }}
                </h1>
                <div
                  class="flex flex-wrap gap-3 text-sm text-gray-600 dark:text-gray-400 items-center"
                >
                  <span class="badge badge-outline"
                    >{{ getFileExtension(file.filename) }} 文件</span
                  >
                  <span class="badge badge-outline badge-warning" v-if="file.is_deleted === 1"
                    >在回收站</span
                  >
                </div>
              </div>
            </div>
          </div>

          <!-- 文件预览卡片 -->
          <div
            class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <h2
              class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2"
            >
              <span>📷</span> 文件预览
            </h2>
            <div class="flex items-center justify-center min-h-[400px] rounded-xl overflow-hidden">
              <!-- 图片预览 -->
              <img
                v-if="isImage(file.mime_type)"
                :src="file.preview_url"
                :alt="file.filename"
                class="max-w-full max-h-[600px] object-contain"
              />
              <!-- 视频预览 -->
              <video
                v-else-if="isVideo(file.mime_type)"
                :src="file.preview_url"
                controls
                class="max-w-full max-h-[600px] rounded-lg"
              ></video>
              <!-- 音频预览 -->
              <div v-else-if="isAudio(file.mime_type)" class="w-full p-8">
                <div class="text-center mb-4">
                  <div class="text-6xl mb-2">🎵</div>
                  <p class="text-gray-600 dark:text-gray-400">音频文件</p>
                </div>
                <audio :src="file.preview_url" controls class="w-full"></audio>
              </div>
              <!-- PDF 预览 -->
              <PDFViewer
                v-else-if="isPdf(file.mime_type)"
                :url="file.preview_url"
                class="h-screen w-full"
              />
              <!-- 文本文件预览 -->
              <TextViewer
                v-else-if="isText(file.mime_type)"
                :url="file.preview_url"
                class="w-full h-full"
              />
              <!-- 其他文件类型 -->
              <div v-else class="text-center p-8">
                <div :class="`text-8xl ${getFileTypeColor(file.mime_type)}`">
                  {{ getFileIcon(file.mime_type) }}
                </div>
                <p class="text-xl text-gray-600 dark:text-gray-400 mt-4">{{ file.mime_type }}</p>
                <p class="text-sm text-gray-500 mt-2">无法预览此文件类型</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：文件信息 -->
        <div class="space-y-6">
          <!-- 操作按钮 -->
          <div
            class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">⚡ 快速操作</h2>
            <div class="space-y-2">
              <a
                :href="file.download_url"
                target="_blank"
                download
                class="btn btn-primary w-full gap-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                下载文件
              </a>
              <button @click="handleManageNotes" class="btn btn-outline w-full gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
                管理笔记
                <span v-if="file.notes_count > 0" class="badge badge-primary">{{
                  file.notes_count
                }}</span>
              </button>
              <button
                @click="showRenameModal = true"
                class="btn btn-outline w-full gap-2"
                v-if="!file.is_deleted === 1"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                @click="handleDelete"
                class="btn btn-outline btn-error w-full gap-2"
                v-if="!file.is_deleted === 1"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
                删除文件
              </button>
            </div>
          </div>

          <!-- 基本信息 -->
          <div
            class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">📋 基本信息</h2>
            <div class="space-y-4">
              <!-- 文件名 -->
              <div>
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >文件名</label
                >
                <div class="flex items-center gap-2 mt-1">
                  <p class="text-sm text-gray-900 dark:text-gray-100 break-all flex-1">
                    {{ file.filename }}
                  </p>
                  <button
                    @click="copyToClipboard(file.filename)"
                    class="btn btn-xs btn-ghost text-gray-400 hover:text-blue-500"
                    title="复制"
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
              <div>
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >文件大小</label
                >
                <p class="text-sm text-gray-900 dark:text-gray-100 font-mono mt-1">
                  {{ formatSize(file.size) }}
                </p>
              </div>

              <!-- 文件类型 -->
              <div>
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >MIME 类型</label
                >
                <p class="text-sm text-gray-900 dark:text-gray-100 font-mono mt-1">
                  {{ file.mime_type }}
                </p>
              </div>

              <!-- 文件哈希 -->
              <div v-if="file.hash">
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >文件哈希</label
                >
                <div class="flex items-center gap-2 mt-1">
                  <p class="text-xs text-gray-900 dark:text-gray-100 font-mono break-all flex-1">
                    {{ file.hash }}
                  </p>
                  <button
                    @click="copyToClipboard(file.hash)"
                    class="btn btn-xs btn-ghost text-gray-400 hover:text-blue-500"
                    title="复制"
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
              <div>
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >存储路径</label
                >
                <p class="text-xs text-gray-900 dark:text-gray-100 font-mono break-all mt-1">
                  {{ file.storage_path }}
                </p>
              </div>
            </div>
          </div>

          <!-- 时间信息 -->
          <div
            class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">⏰ 时间信息</h2>
            <div class="space-y-4">
              <div>
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >上传时间</label
                >
                <p class="text-sm text-gray-900 dark:text-gray-100 mt-1">
                  {{ formatDate(file.created_at) }}
                </p>
              </div>
              <div>
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >修改时间</label
                >
                <p class="text-sm text-gray-900 dark:text-gray-100 mt-1">
                  {{ formatDate(file.updated_at) }}
                </p>
              </div>

              <div v-if="file.original_created_at">
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >原始创建时间</label
                >
                <p class="text-sm text-gray-900 dark:text-gray-100 mt-1">
                  {{ formatDate(file.original_created_at) }}
                </p>
              </div>
              <div v-if="file.original_modified_at">
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >原始修改时间</label
                >
                <p class="text-sm text-gray-900 dark:text-gray-100 mt-1">
                  {{ formatDate(file.original_modified_at) }}
                </p>
              </div>
              <div v-if="file.deleted_at">
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >删除时间</label
                >
                <p class="text-sm text-gray-900 dark:text-gray-100 mt-1">
                  {{ formatDate(file.deleted_at) }}
                </p>
              </div>
            </div>
          </div>

          <!-- 其他信息 -->
          <div
            class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">💡 其他信息</h2>
            <div class="space-y-4">
              <div>
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >文件 ID</label
                >
                <div class="flex items-center gap-2 mt-1">
                  <p class="text-xs text-gray-900 dark:text-gray-100 font-mono break-all flex-1">
                    {{ file.id }}
                  </p>
                  <button
                    @click="copyToClipboard(file.id)"
                    class="btn btn-xs btn-ghost text-gray-400 hover:text-blue-500"
                    title="复制"
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
              <div>
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >关联笔记</label
                >
                <p class="text-sm text-gray-900 dark:text-gray-100 mt-1">
                  {{ file.notes_count || 0 }} 条
                </p>
              </div>
              <div v-if="file.folder_id">
                <label
                  class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide"
                  >所属文件夹 ID</label
                >
                <p class="text-xs text-gray-900 dark:text-gray-100 font-mono break-all mt-1">
                  {{ file.folder_id }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 重命名模态框 -->
    <div
      v-if="showRenameModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showRenameModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-96 shadow-xl">
        <h3 class="text-lg font-bold mb-4 text-gray-900 dark:text-gray-100">重命名文件</h3>
        <input
          v-model="newFileName"
          type="text"
          placeholder="文件名"
          class="input input-bordered w-full mb-4"
          @keyup.enter="handleRename"
          autoFocus
        />
        <div class="flex justify-end gap-2">
          <button @click="showRenameModal = false" class="btn btn-ghost">取消</button>
          <button @click="handleRename" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>

    <!-- 笔记管理模态框 -->
    <UnifiedNotes :is-open="showNotes" :item="file" :item-type="'file'" @close="closeNotes" />
  </div>
</template>
