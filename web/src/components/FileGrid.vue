<script setup>
defineProps({
  files: {
    type: Array,
    required: true,
    default: () => [],
  },
})

defineEmits(['delete-file', 'preview-file'])

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
  return '📁'
}
const serverUrl = import.meta.env.VITE_API_FILE_SERVER_URL || ''
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
    <div
      v-for="file in files"
      :key="file.id"
      class="card bg-base-100 shadow-sm hover:shadow-md transition-shadow"
    >
      <figure
        class="h-32 bg-base-300 flex items-center justify-center overflow-hidden cursor-pointer"
        @click="$emit('preview-file', file)"
      >
        <img
          v-if="isImage(file.mime_type)"
          :src="`${serverUrl}/${file.download_url}`"
          :alt="file.filename"
          class="w-full h-full object-cover"
        />
        <span v-else class="text-4xl">{{ getFileIcon(file.mime_type) }}</span>
      </figure>
      <div class="card-body p-4">
        <h3 class="card-title text-sm truncate" :title="file.filename">{{ file.filename }}</h3>
        <div class="text-xs text-base-content/70">
          <p>{{ formatSize(file.size) }}</p>
          <p>{{ formatDate(file.created_at) }}</p>
        </div>
        <div class="card-actions justify-end mt-2">
          <button class="btn btn-xs btn-error btn-outline" @click="$emit('delete-file', file.id)">
            Delete
          </button>
          <a
            :href="`${serverUrl}/${file.download_url}`"
            target="_blank"
            download
            class="btn btn-xs btn-ghost"
            >Download</a
          >
        </div>
      </div>
    </div>
  </div>
</template>
