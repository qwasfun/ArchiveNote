<script setup>
import { ref, onMounted } from 'vue'
import noteService from '../../api/noteService.js'
import NoteEditor from '../../components/NoteEditor.vue'

const notes = ref([])
const loading = ref(false)
const selectedNote = ref(null)
const isEditing = ref(false)

const loadNotes = async () => {
  loading.value = true
  try {
    const response = await noteService.getNotes()

    notes.value = response.data
  } catch (error) {
    console.error('Failed to load notes', error)
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  selectedNote.value = null
  isEditing.value = true
}

const handleEdit = (note) => {
  selectedNote.value = { ...note } // Clone to avoid direct mutation
  isEditing.value = true
}

const handleSave = async (noteData) => {
  try {
    if (selectedNote.value && selectedNote.value.id) {
      await noteService.updateNote(selectedNote.value.id, noteData)
    } else {
      await noteService.createNote(noteData)
    }
    isEditing.value = false
    selectedNote.value = null
    await loadNotes()
  } catch (error) {
    console.error('Failed to save note', error)
  }
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this note?')) return
  try {
    await noteService.deleteNote(id)
    await loadNotes()
    if (selectedNote.value && selectedNote.value.id === id) {
      isEditing.value = false
      selectedNote.value = null
    }
  } catch (error) {
    console.error('Failed to delete note', error)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString()
}

onMounted(async () => {
  await loadNotes()
})
</script>

<template>
  <div class="h-full flex gap-6 p-4">
    <!-- Notes List Sidebar -->
    <div class="w-1/3 flex flex-col h-full">
      <div class="flex justify-between items-center mb-4">
        <h1 class="text-2xl font-bold">Notes</h1>
        <button class="btn btn-primary btn-sm" @click="handleCreate">New Note</button>
      </div>

      <div v-if="loading && notes.length === 0" class="flex justify-center p-4">
        <span class="loading loading-spinner"></span>
      </div>

      <div v-else class="flex-1 overflow-y-auto space-y-2 pr-2">
        <div
          v-for="note in notes"
          :key="note.id"
          class="card bg-base-100 shadow-sm hover:bg-base-200 cursor-pointer transition-colors"
          :class="{ 'ring-2 ring-primary': selectedNote?.id === note.id }"
          @click="handleEdit(note)"
        >
          <div class="card-body p-4">
            <h3 class="font-bold truncate">{{ note.title || 'Untitled Note' }}</h3>
            <p class="text-xs text-base-content/60 line-clamp-2">{{ note.content }}</p>
            <div class="flex justify-between items-center mt-2">
              <span class="text-xs text-base-content/40">{{ formatDate(note.updated_at) }}</span>
              <button class="btn btn-ghost btn-xs text-error" @click.stop="handleDelete(note.id)">
                Del
              </button>
            </div>
          </div>
        </div>

        <div v-if="notes.length === 0 && !loading" class="text-center text-base-content/50 py-8">
          No notes found.
        </div>
      </div>
    </div>

    <!-- main Content / Editor -->
    <div class="flex-1 h-full">
      <NoteEditor
        v-if="isEditing"
        :note="selectedNote"
        @save="handleSave"
        @cancel="isEditing = false"
      />
      <div
        v-else
        class="h-full flex flex-col items-center justify-center text-base-content/30 bg-base-200 rounded-box"
      >
        <span class="text-6xl mb-4">📝</span>
        <p class="text-xl">Select a note to view or edit</p>
      </div>
    </div>
  </div>
</template>
