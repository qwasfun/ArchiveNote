<script setup>
import { ref, watch } from 'vue'
import noteService from '../api/noteService'
import FileSelector from './FileSelector.vue'

const props = defineProps({
  note: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['save', 'cancel'])

const title = ref('')
const content = ref('')
const attachedFiles = ref([]) // Currently attached files
const showFileSelector = ref(false)

// Watch for prop changes to populate form
watch(
  () => props.note,
  (newNote) => {
    if (newNote) {
      title.value = newNote.title || ''
      content.value = newNote.content || ''
      attachedFiles.value = newNote.files || []
    } else {
      title.value = ''
      content.value = ''
      attachedFiles.value = []
    }
  },
  { immediate: true },
)

const handleSubmit = () => {
  emit('save', {
    title: title.value,
    content: content.value,
  })
}

const handleAttachFiles = async (fileIds) => {
  showFileSelector.value = false
  if (!props.note || !props.note.id) {
    alert('Please save the note before attaching files (MVP limitation).') // Or handle temp attachment
    return
  }

  try {
    await noteService.attachFiles(props.note.id, {
      file_ids: fileIds,
    })
    // Refresh note logic or manually append
    // For simplicity, we assume parent might refresh, but we can also fetch fresh note
    // Let's manually append for UI responsiveness if we had file objects,
    // but we only have IDs here. Actually better to re-fetch or emit update needed.
    // Simplest: emit save to refresh parent or fetch details here.
    // Let's fetch details here.
    const res = await noteService.getNote(props.note.id)

    attachedFiles.value = res.files
  } catch (e) {
    console.error(e)
  }
}

const handleDetach = async (fileId) => {
  if (!props.note || !props.note.id) return
  try {
    await noteService.detachFiles(props.note.id, {
      file_ids: [fileId],
    })
    attachedFiles.value = attachedFiles.value.filter((f) => f.id !== fileId)
  } catch (e) {
    console.error(e)
  }
}

const getFileIcon = (mimeType) => {
  if (mimeType.startsWith('image/')) return '🖼️'
  if (mimeType.startsWith('video/')) return '🎥'
  if (mimeType === 'application/pdf') return '📄'
  return '📁'
}
</script>

<template>
  <div class="card bg-base-100 shadow-xl h-full flex flex-col relative">
    <div class="card-body flex flex-col h-full overflow-hidden">
      <div class="flex justify-between items-start">
        <h2 class="card-title">{{ note ? 'Edit Note' : 'New Note' }}</h2>
        <div v-if="note" class="badge badge-outline text-xs">ID: {{ note.id }}</div>
      </div>

      <div class="form-control w-full">
        <label class="label">
          <span class="label-text">Title</span>
        </label>
        <input
          type="text"
          v-model="title"
          placeholder="Note Title (Optional)"
          class="input input-bordered w-full"
        />
      </div>

      <div class="form-control flex-1 mt-4 min-h-0">
        <label class="label">
          <span class="label-text">Content</span>
        </label>
        <textarea
          v-model="content"
          class="textarea textarea-bordered h-full resize-none font-mono"
          placeholder="Write your note here..."
        ></textarea>
      </div>

      <!-- Attachments Section -->
      <div class="mt-4 border-t pt-4">
        <div class="flex justify-between items-center mb-2">
          <span class="label-text font-bold">Attachments ({{ attachedFiles.length }})</span>
          <button class="btn btn-xs btn-outline" @click="showFileSelector = true" :disabled="!note">
            {{ !note ? 'Save to Attach' : '+ Attach File' }}
          </button>
        </div>

        <div class="flex flex-wrap gap-2 overflow-x-auto pb-2">
          <div
            v-for="file in attachedFiles"
            :key="file.id"
            class="badge badge-lg gap-2 cursor-pointer hover:bg-base-300 p-4 h-auto"
          >
            {{ getFileIcon(file.mime_type) }}
            <span class="truncate max-w-[150px] text-xs">{{ file.filename }}</span>
            <button
              class="btn btn-ghost btn-xs btn-circle h-4 w-4 min-h-0"
              @click.stop="handleDetach(file.id)"
            >
              ✕
            </button>
          </div>
          <span v-if="attachedFiles.length === 0" class="text-xs text-base-content/50 italic"
            >No files attached</span
          >
        </div>
      </div>

      <div class="card-actions justify-end mt-4 pt-2 border-t">
        <button class="btn btn-ghost" @click="$emit('cancel')">Cancel</button>
        <button class="btn btn-primary" @click="handleSubmit" :disabled="!content.trim()">
          Save
        </button>
      </div>
    </div>

    <FileSelector
      v-if="showFileSelector"
      :exclude-ids="attachedFiles.map((f) => f.id)"
      @select="handleAttachFiles"
      @cancel="showFileSelector = false"
    />
  </div>
</template>
