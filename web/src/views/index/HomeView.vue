<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { getFiles } from '../../api/fileService.js'
import { getNotes } from '../../api/noteService.js'
import { getStats } from '../../api/statsService.js'
import { formatSize } from '@/utils/format'
import { getFileIcon, getFileTypeColor } from '@/utils/file'
import { useAuthStore } from '@/stores/auth.js'

const router = useRouter()

const stats = ref({
  totalFiles: 0,
  totalNotes: 0,
  totalSize: 0,
  todayActivity: 0,
})

const recentFiles = ref([])
const recentNotes = ref([])

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString()
}

// 导航到页面
const goToFiles = () => router.push('/files')
const goToNotes = () => router.push('/notes')

// 加载数据
const loadData = async () => {
  try {
    // 加载统计数据
    const statsData = await getStats()
    stats.value.totalFiles = statsData.file_count
    stats.value.totalSize = statsData.storage_usage
    stats.value.totalNotes = statsData.note_count
    stats.value.todayActivity = statsData.today_activity

    // 加载文件列表用于展示最近文件
    const filesResponse = await getFiles()
    const files = filesResponse.data || []

    // 最近文件（最多5个）
    recentFiles.value = files
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5)

    // 加载笔记列表用于展示最近笔记
    const notesResponse = await getNotes()
    const notes = notesResponse.data || []

    // 最近笔记（最多5个）
    recentNotes.value = notes
      .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
      .slice(0, 5)
  } catch (error) {
    console.error('Failed to load dashboard data', error)
  }
}

const { isAuthenticated } = useAuthStore()

onMounted(() => {
  if (isAuthenticated) {
    loadData()
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- 头部欢迎区域 -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="container mx-auto px-4 py-12">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            欢迎使用 <span class="text-blue-600">ArchiveNote</span>
          </h1>
          <p class="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            您的个人文件和笔记管理中心，让信息整理变得简单而高效
          </p>

          <!-- 快捷操作按钮 -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <RouterLink to="/files" class="btn btn-primary btn-lg gap-3 w-full sm:w-auto">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                ></path>
              </svg>
              上传文件
            </RouterLink>
            <RouterLink to="/notes" class="btn btn-outline btn-lg gap-3 w-full sm:w-auto">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4v16m8-8H4"
                ></path>
              </svg>
              新建笔记
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="container mx-auto px-4 py-8">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">总文件数</p>
              <p class="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                {{ stats.totalFiles }}
              </p>
            </div>
            <div
              class="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-xl flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-blue-600 dark:text-blue-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                ></path>
              </svg>
            </div>
          </div>
        </div>

        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">笔记数量</p>
              <p class="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                {{ stats.totalNotes }}
              </p>
            </div>
            <div
              class="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-xl flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-green-600 dark:text-green-300"
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
            </div>
          </div>
        </div>

        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">存储使用</p>
              <p class="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                {{ formatSize(stats.totalSize) }}
              </p>
            </div>
            <div
              class="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-xl flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-purple-600 dark:text-purple-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"
                ></path>
              </svg>
            </div>
          </div>
        </div>

        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">今日活动</p>
              <p class="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                {{ stats.todayActivity }}
              </p>
            </div>
            <div
              class="w-12 h-12 bg-orange-100 dark:bg-orange-900 rounded-xl flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-orange-600 dark:text-orange-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                ></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近活动和功能介绍 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- 最近文件 -->
        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
        >
          <div class="p-6 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">最近文件</h2>
              <RouterLink to="/files" class="text-sm text-blue-600 hover:text-blue-500 font-medium">
                查看全部 →
              </RouterLink>
            </div>
          </div>
          <div class="p-6">
            <div v-if="recentFiles.length === 0" class="text-center py-8">
              <div class="text-4xl mb-4">📂</div>
              <p class="text-gray-500 dark:text-gray-400">还没有上传任何文件</p>
              <RouterLink to="/files" class="btn btn-sm btn-primary mt-4">
                上传第一个文件
              </RouterLink>
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="file in recentFiles"
                :key="file.id"
                class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
                @click="goToFiles"
              >
                <div
                  :class="`w-10 h-10 rounded-lg flex items-center justify-center text-sm ${getFileTypeColor(file.mime_type)}`"
                >
                  {{ getFileIcon(file.mime_type) }}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-gray-900 dark:text-gray-100 truncate">
                    {{ file.filename }}
                  </p>
                  <p class="text-xs text-gray-500">{{ formatDate(file.created_at) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 最近笔记 -->
        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
        >
          <div class="p-6 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">最近笔记</h2>
              <RouterLink to="/notes" class="text-sm text-blue-600 hover:text-blue-500 font-medium">
                查看全部 →
              </RouterLink>
            </div>
          </div>
          <div class="p-6">
            <div v-if="recentNotes.length === 0" class="text-center py-8">
              <div class="text-4xl mb-4">📝</div>
              <p class="text-gray-500 dark:text-gray-400">还没有创建任何笔记</p>
              <RouterLink to="/notes" class="btn btn-sm btn-primary mt-4">
                创建第一个笔记
              </RouterLink>
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="note in recentNotes"
                :key="note.id"
                class="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
                @click="goToNotes"
              >
                <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-1 truncate">
                  {{ note.title || '无标题' }}
                </h4>
                <p class="text-sm text-gray-600 dark:text-gray-300 mb-2 line-clamp-2">
                  {{ note.content }}
                </p>
                <p class="text-xs text-gray-500">{{ formatDate(note.updated_at) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 功能特点 -->
      <div class="mt-12">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">强大的功能特点</h2>
          <p class="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            ArchiveNote 提供完整的文件和笔记管理解决方案，让您的工作更有条理
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div class="text-center p-6">
            <div
              class="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-2xl flex items-center justify-center mx-auto mb-4"
            >
              <svg
                class="w-8 h-8 text-blue-600 dark:text-blue-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                ></path>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">多格式支持</h3>
            <p class="text-gray-600 dark:text-gray-400">
              支持图片、视频、PDF、音频等多种文件格式的预览和管理
            </p>
          </div>

          <div class="text-center p-6">
            <div
              class="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-2xl flex items-center justify-center mx-auto mb-4"
            >
              <svg
                class="w-8 h-8 text-green-600 dark:text-green-300"
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
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">智能笔记</h3>
            <p class="text-gray-600 dark:text-gray-400">
              为文件添加笔记，支持文件关联，让信息管理更有条理
            </p>
          </div>

          <div class="text-center p-6">
            <div
              class="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-2xl flex items-center justify-center mx-auto mb-4"
            >
              <svg
                class="w-8 h-8 text-purple-600 dark:text-purple-300"
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
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">快速搜索</h3>
            <p class="text-gray-600 dark:text-gray-400">
              强大的搜索功能，快速找到您需要的文件和笔记
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
