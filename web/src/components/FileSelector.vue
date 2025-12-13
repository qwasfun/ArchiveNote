<script setup>
import { ref, onMounted } from 'vue'
import fileService from '../api/fileService'

const props = defineProps({
  excludeIds: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['select', 'cancel'])

const files = ref([])
const loading = ref(false)
const selectedFiles = ref([])

const loadFiles = async () => {
  loading.value = true
  try {
    const response = await fileService.getFiles({ limit: 100 })
    files.value = response.data
  } catch (error) {
    console.error('Failed to load files', error)
  } finally {
    loading.value = false
  }
}

const toggleSelection = (fileId) => {
  if (selectedFiles.value.includes(fileId)) {
    selectedFiles.value = selectedFiles.value.filter((id) => id !== fileId)
  } else {
    selectedFiles.value.push(fileId)
  }
}

const handleConfirm = () => {
  emit('select', selectedFiles.value)
}

const isImage = (mimeType) => mimeType.startsWith('image/')
const getFileIcon = (mimeType) => {
  if (mimeType.startsWith('image/')) return '🖼️'
  if (mimeType.startsWith('video/')) return '🎥'
  if (mimeType === 'application/pdf') return '📄'
  return '📁'
}

onMounted(() => {
  loadFiles()
})
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-base-100 p-6 rounded-box shadow-xl w-[90%] max-w-3xl h-[80vh] flex flex-col">
      <h3 class="font-bold text-lg mb-4">Attach Files</h3>

      <div v-if="loading" class="flex-1 flex justify-center items-center">
        <span class="loading loading-spinner"></span>
      </div>

      <div
        v-else
        class="flex-1 overflow-y-auto grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 p-2"
      >
        <div
          v-for="file in files"
          :key="file.id"
          class="card bg-base-200 border-2 cursor-pointer relative"
          :class="
            selectedFiles.includes(file.id)
              ? 'border-primary'
              : 'border-transparent hover:border-base-300'
          "
          @click="toggleSelection(file.id)"
        >
          <div
            v-if="props.excludeIds.includes(file.id)"
            class="absolute inset-0 bg-base-300/50 cursor-not-allowed z-10 flex items-center justify-center"
          >
            <span class="badge">Attached</span>
          </div>

          <figure class="h-24 flex items-center justify-center bg-base-300 overflow-hidden">
            <img
              v-if="isImage(file.mime_type)"
              :src="`${file.download_url}`"
              class="w-full h-full object-cover opacity-80"
            />
            <span v-else class="text-3xl">{{ getFileIcon(file.mime_type) }}</span>
          </figure>
          <div class="p-2 text-xs truncate font-medium">
            {{ file.filename }}
          </div>

          <div
            v-if="selectedFiles.includes(file.id)"
            class="absolute top-2 right-2 badge badge-primary"
          >
            ✓
          </div>
        </div>
      </div>

      <div class="modal-action mt-4">
        <button class="btn" @click="$emit('cancel')">Cancel</button>
        <button
          class="btn btn-primary"
          @click="handleConfirm"
          :disabled="selectedFiles.length === 0"
        >
          Attach ({{ selectedFiles.length }})
        </button>
      </div>
    </div>
  </div>
</template>
