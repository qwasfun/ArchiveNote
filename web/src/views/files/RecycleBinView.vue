<script setup>
import { ref, onMounted } from 'vue'
import FileGrid from '../../components/FileGrid.vue'
import FileDetails from '../../components/FileDetails.vue'

import recycleService from '../../api/recycleService.js'

const files = ref([])
const folders = ref([])
const loading = ref(false)
const selectedFiles = ref([])
const selectedFolders = ref([])
const isSelectionMode = ref(true) // Default to selection mode for easier management
const detailsFile = ref(null)
const showDetails = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const res = await recycleService.getItems()
    files.value = res.files || []
    folders.value = res.folders || []
  } catch (error) {
    console.error('Failed to load recycle bin', error)
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedFiles.value = selection.files
  selectedFolders.value = selection.folders
}

const restoreItems = async () => {
  try {
    await recycleService.restoreItems({
      file_ids: selectedFiles.value,
      folder_ids: selectedFolders.value,
    })
    await loadData()
    selectedFiles.value = []
    selectedFolders.value = []
  } catch (e) {
    console.error(e)
  }
}

const permanentDeleteItems = async () => {
  if (!confirm('Are you sure? This cannot be undone.')) return
  try {
    await recycleService.permanentDeleteItems({
      file_ids: selectedFiles.value,
      folder_ids: selectedFolders.value,
    })
    await loadData()
    selectedFiles.value = []
    selectedFolders.value = []
  } catch (e) {
    console.error(e)
  }
}

const handleViewDetails = (file) => {
  detailsFile.value = file
  showDetails.value = true
}

const handleCloseDetails = () => {
  showDetails.value = false
  detailsFile.value = null
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-900">
    <div class="container mx-auto px-4 py-6">
      <div class="mb-8 flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">🗑️ 回收站</h1>
          <p class="text-gray-600 dark:text-gray-400 mt-1">管理已删除的文件和文件夹</p>
        </div>
        <div class="flex gap-2">
          <button
            @click="restoreItems"
            class="btn btn-success"
            :disabled="selectedFiles.length === 0 && selectedFolders.length === 0"
          >
            还原
          </button>
          <button
            @click="permanentDeleteItems"
            class="btn btn-error"
            :disabled="selectedFiles.length === 0 && selectedFolders.length === 0"
          >
            彻底删除
          </button>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center py-12">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

      <div v-else>
        <FileGrid
          :files="files"
          :folders="folders"
          :selection-mode="isSelectionMode"
          :selected-files="selectedFiles"
          :selected-folders="selectedFolders"
          :isShowOperationBtn="false"
          @view-details="handleViewDetails"
          @selection-change="handleSelectionChange"
        />
      </div>
    </div>
    <!-- 文件详情模态框 -->
    <FileDetails
      :file-id="detailsFile && detailsFile.id"
      :is-open="showDetails"
      show-manage-notes
      @close="handleCloseDetails"
    />
  </div>
</template>
