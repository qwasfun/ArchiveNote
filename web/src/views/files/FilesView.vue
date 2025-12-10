<script setup>
import { ref, onMounted } from 'vue'
import FileUpload from '../../components/FileUpload.vue'
import FileGrid from '../../components/FileGrid.vue'
import fileService from '../../api/fileService.js'

const files = ref([])
const loading = ref(false)
const showUploadModal = ref(false)

const loadFiles = async () => {
  loading.value = true
  try {
    const response = await fileService.getFiles()
    files.value = response.data
  } catch (error) {
    console.error('Failed to load files', error)
  } finally {
    loading.value = false
  }
}

const handleUploadSuccess = async () => {
  await loadFiles()
  showUploadModal.value = false
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this file?')) return
  try {
    await fileService.deleteFile(id)
    await loadFiles()
  } catch (error) {
    console.error('Failed to delete file', error)
  }
}

const handlePreview = (file) => {
  // Open in new tab for now, simplistic preview
  const serverUrl = import.meta.env.VITE_API_FILE_SERVER_URL || ''
  window.open(`${serverUrl}/${file.download_url}`, '_blank')
}

onMounted(() => {
  loadFiles()
})
</script>

<template>
  <div class="p-4 h-full flex flex-col">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Files</h1>
      <button class="btn btn-primary" @click="showUploadModal = !showUploadModal">
        {{ showUploadModal ? 'Close Upload' : 'Upload Files' }}
      </button>
    </div>

    <div v-if="showUploadModal" class="mb-6 animate-fade-in">
      <FileUpload @upload-success="handleUploadSuccess" />
    </div>

    <div v-if="loading" class="flex justify-center p-8">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <div
      v-else-if="files.length === 0"
      class="flex-1 bg-base-200 rounded-box p-12 flex flex-col items-center justify-center text-base-content/50"
    >
      <span class="text-6xl mb-4">📂</span>
      <p class="text-xl">No files found.</p>
      <p class="text-sm mt-2">Upload some files to get started.</p>
    </div>

    <div v-else class="flex-1 overflow-y-auto">
      <FileGrid :files="files" @delete-file="handleDelete" @preview-file="handlePreview" />
    </div>
  </div>
</template>
