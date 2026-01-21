<script setup>
import { ref } from 'vue'
import fileService from '../api/fileService'

const props = defineProps({
  folderId: {
    type: String,
    default: null,
  },
  uploadMode: {
    type: String,
    default: 'traditional',
    validator: (value) => ['traditional', 'direct'].includes(value),
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['upload-start', 'upload-progress', 'upload-complete', 'upload-error'])

const isDragging = ref(false)
const uploading = ref(false)
const uploadProgress = ref({ current: 0, total: 0 })
const fileInput = ref(null)
const folderInput = ref(null)

// 拖拽事件处理
const handleDragOver = (e) => {
  if (props.disabled || uploading.value) return
  e.preventDefault()
  e.stopPropagation()
  isDragging.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  e.stopPropagation()
  // 只有离开整个拖拽区域时才取消拖拽状态
  if (e.currentTarget === e.target || !e.currentTarget.contains(e.relatedTarget)) {
    isDragging.value = false
  }
}

const handleDrop = async (e) => {
  e.preventDefault()
  e.stopPropagation()
  isDragging.value = false

  if (props.disabled || uploading.value) {
    console.log('正在上传中或已禁用，请稍候...')
    return
  }

  let files = []

  // 处理拖拽的文件和文件夹
  if (e.dataTransfer.items && e.dataTransfer.items.length) {
    files = await getAllFiles(e.dataTransfer.items)
  } else if (e.dataTransfer.files.length) {
    files = Array.from(e.dataTransfer.files).map((f) => ({ file: f, path: f.name }))
  }

  if (files.length > 0) {
    await uploadFiles(files)
  }
}

// 递归处理文件和文件夹
const getAllFiles = async (dataTransferItems) => {
  const files = []
  const queue = []

  for (let i = 0; i < dataTransferItems.length; i++) {
    const item = dataTransferItems[i].webkitGetAsEntry()
    if (item) {
      queue.push({ entry: item, path: '' })
    }
  }

  while (queue.length > 0) {
    const { entry, path } = queue.shift()

    if (entry.isFile) {
      const file = await new Promise((resolve) => {
        entry.file(resolve)
      })
      const fullPath = path ? `${path}/${entry.name}` : entry.name
      files.push({ file, path: fullPath })
    } else if (entry.isDirectory) {
      const reader = entry.createReader()
      const entries = await new Promise((resolve) => {
        reader.readEntries(resolve)
      })

      for (const childEntry of entries) {
        const newPath = path ? `${path}/${entry.name}` : entry.name
        queue.push({ entry: childEntry, path: newPath })
      }
    }
  }

  return files
}

// 处理文件选择
const handleFileSelect = (e) => {
  if (e.target.files.length) {
    const files = Array.from(e.target.files).map((f) => ({
      file: f,
      path: f.name,
    }))
    uploadFiles(files)
  }
  // 重置input以允许选择相同文件
  e.target.value = ''
}

// 处理文件夹选择
const handleFolderSelect = (e) => {
  if (e.target.files.length) {
    const files = Array.from(e.target.files).map((f) => ({
      file: f,
      path: f.webkitRelativePath || f.name,
    }))
    uploadFiles(files)
  }
  // 重置input以允许选择相同文件夹
  e.target.value = ''
}

// 触发文件选择
const triggerFileInput = () => {
  if (props.disabled || uploading.value) return
  fileInput.value?.click()
}

// 触发文件夹选择
const triggerFolderInput = () => {
  if (props.disabled || uploading.value) return
  folderInput.value?.click()
}

// 上传文件
const uploadFiles = async (filesWithPaths) => {
  uploading.value = true
  emit('upload-start')

  try {
    if (props.uploadMode === 'direct') {
      await uploadFilesDirect(filesWithPaths)
    } else {
      await uploadFilesTraditional(filesWithPaths)
    }
    emit('upload-complete')
  } catch (error) {
    console.error('文件上传失败', error)
    emit('upload-error', error)
  } finally {
    uploading.value = false
    uploadProgress.value = { current: 0, total: 0 }
  }
}

// 普通上传方式（通过后端）
const uploadFilesTraditional = async (filesWithPaths) => {
  // 分批上传，每批最多 20 个文件
  const BATCH_SIZE = 20
  const totalFiles = filesWithPaths.length
  let uploadedCount = 0

  uploadProgress.value = { current: 0, total: totalFiles }

  for (let i = 0; i < totalFiles; i += BATCH_SIZE) {
    const batch = filesWithPaths.slice(i, i + BATCH_SIZE)
    const formData = new FormData()

    // 添加文件和对应的相对路径
    for (const { file, path } of batch) {
      const fileToUpload = new File([file], path, { type: file.type })
      formData.append('files', fileToUpload)
    }

    const params = {}
    if (props.folderId) {
      params.folder_id = props.folderId
    }

    await fileService.uploadFiles(formData, params)
    uploadedCount += batch.length
    uploadProgress.value.current = uploadedCount
    emit('upload-progress', { current: uploadedCount, total: totalFiles })
  }
}

// S3直传方式
const uploadFilesDirect = async (filesWithPaths) => {
  const totalFiles = filesWithPaths.length
  let uploadedCount = 0

  uploadProgress.value = { current: 0, total: totalFiles }

  for (const { file, path } of filesWithPaths) {
    try {
      // 1. 获取预签名URL
      const presignedData = await fileService.getPresignedUploadUrl({
        filename: path,
        content_type: file.type,
        folder_id: props.folderId,
      })

      // 2. 直接上传到S3
      await fileService.uploadToS3(presignedData.upload_url, file, file.type)

      // 3. 确认上传完成
      await fileService.confirmUpload(presignedData.file_id)

      uploadedCount++
      uploadProgress.value.current = uploadedCount
      emit('upload-progress', { current: uploadedCount, total: totalFiles })
    } catch (error) {
      console.error(`上传文件 ${path} 失败:`, error)
    }
  }
}

defineExpose({
  isDragging,
  uploading,
  uploadProgress,
})
</script>

<template>
  <div
    class="drag-upload-zone"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <!-- 隐藏的文件输入框 -->
    <input
      ref="fileInput"
      type="file"
      multiple
      class="hidden"
      @change="handleFileSelect"
    />

    <!-- 隐藏的文件夹输入框 -->
    <input
      ref="folderInput"
      type="file"
      webkitdirectory
      directory
      class="hidden"
      @change="handleFolderSelect"
    />

    <!-- 默认插槽：包裹需要拖拽上传功能的内容 -->
    <slot :triggerFileInput="triggerFileInput" :triggerFolderInput="triggerFolderInput"></slot>

    <!-- 拖拽覆盖层 -->
    <div
      v-if="isDragging && !disabled"
      class="absolute inset-0 bg-blue-500 bg-opacity-10 border-4 border-dashed border-blue-500 rounded-2xl flex items-center justify-center z-50 pointer-events-none"
    >
      <div class="text-center">
        <svg
          class="w-16 h-16 mx-auto mb-4 text-blue-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          ></path>
        </svg>
        <p class="text-xl font-semibold text-blue-600 dark:text-blue-400">
          释放以上传文件到当前文件夹
        </p>
      </div>
    </div>

    <!-- 上传按钮浮动层（仅在非拖拽和非上传状态显示） -->
    <div
      v-if="!isDragging && !uploading && !disabled"
      class="absolute top-4 right-4 z-40 flex gap-2"
    >
      <button
        @click.stop="triggerFileInput"
        class="btn btn-sm btn-primary gap-2 shadow-lg"
        title="选择文件上传"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          ></path>
        </svg>
        选择文件
      </button>
      <button
        @click.stop="triggerFolderInput"
        class="btn btn-sm btn-primary gap-2 shadow-lg"
        title="选择文件夹上传"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
          ></path>
        </svg>
        选择文件夹
      </button>
    </div>

    <!-- 上传进度覆盖层 -->
    <div
      v-if="uploading"
      class="absolute inset-0 bg-white dark:bg-gray-800 bg-opacity-95 rounded-2xl flex items-center justify-center z-50"
    >
      <div class="text-center">
        <span class="loading loading-spinner loading-lg text-blue-500 mb-4"></span>
        <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          上传中... {{ uploadProgress.current }} / {{ uploadProgress.total }}
        </p>
        <div
          class="w-64 h-2 bg-gray-200 dark:bg-gray-700 rounded-full mt-4 mx-auto overflow-hidden"
        >
          <div
            class="h-full bg-blue-500 transition-all duration-300"
            :style="{ width: `${(uploadProgress.current / uploadProgress.total) * 100}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.drag-upload-zone {
  position: relative;
}
</style>
