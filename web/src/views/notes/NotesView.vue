<script setup>
import { ref, onMounted } from 'vue'
import noteService from '../../api/noteService.js'
import NoteEditor from '../../components/NoteEditor.vue'
import { formatDate } from '@/utils/format'

const notes = ref([])
const loading = ref(false)
const selectedNote = ref(null)
const isEditing = ref(false)
const isViewing = ref(false)

const currentPage = ref(1)
const pageSize = ref(10)
const totalNotes = ref(0)
const totalPages = ref(0)

const loadNotes = async () => {
  loading.value = true
  try {
    const response = await noteService.getNotes({
      page: currentPage.value,
      page_size: pageSize.value,
    })

    if ((response.data || []).length === 0 && currentPage.value > 1) {
      currentPage.value = 1
      return loadNotes()
    }

    notes.value = response.data
    totalNotes.value = response.total
    totalPages.value = response.total_pages
  } catch (error) {
    console.error('Failed to load notes', error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadNotes()
}

const handleCreate = () => {
  selectedNote.value = null
  isViewing.value = false
  isEditing.value = true
}

const handleView = (note) => {
  selectedNote.value = { ...note } // Clone to avoid direct mutation
  isViewing.value = true
  isEditing.value = false
}

const handleEdit = (note) => {
  if (note) {
    selectedNote.value = { ...note }
  }
  isViewing.value = false
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
    isViewing.value = false
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
      isViewing.value = false
      selectedNote.value = null
    }
  } catch (error) {
    console.error('Failed to delete note', error)
  }
}

const handleCancel = () => {
  isEditing.value = false
  if (!selectedNote.value?.id) {
    isViewing.value = false
    selectedNote.value = null
  } else {
    isViewing.value = true
    console.error('Failed to delete note', error)
  }
}

onMounted(async () => {
  await loadNotes()
})
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-900 h-[calc(100vh-64px)]">
    <div class="container mx-auto px-4 py-6 h-full flex flex-col md:flex-row">
      <!-- Notes List Sidebar -->
      <div
        class="w-full md:w-1/3 flex-col h-full"
        :class="[isEditing || isViewing ? 'hidden md:flex' : 'flex']"
      >
        <div class="flex justify-between items-center mb-4 px-2">
          <div>
            <h1 class="text-3xl font-bold">📝 笔记管理</h1>
            <p class="text-gray-600 dark:text-gray-400 mt-1">管理您的笔记</p>
          </div>
          <button class="btn btn-primary btn-sm" @click="handleCreate">新建笔记</button>
        </div>

        <div v-if="loading && notes.length === 0" class="flex justify-center p-4">
          <span class="loading loading-spinner"></span>
        </div>

        <div v-else class="flex-1 overflow-y-auto space-y-2 p-2">
          <div
            v-for="note in notes"
            :key="note.id"
            class="card bg-base-100 shadow-md hover:bg-base-200 cursor-pointer transition-colors"
            :class="{ 'ring-2 ring-primary': selectedNote?.id === note.id }"
            @click="handleView(note)"
          >
            <div class="card-body p-4">
              <h3 class="font-bold truncate">{{ note.title || 'Untitled Note' }}</h3>
              <p class="text-xs text-base-content/60 line-clamp-2">{{ note.content }}</p>
              <div class="flex justify-between items-center mt-2">
                <span class="text-xs text-base-content/40">{{ formatDate(note.updated_at) }}</span>
                <button class="btn btn-ghost btn-xs text-error" @click.stop="handleDelete(note.id)">
                  删除
                </button>
              </div>
            </div>
          </div>

          <div v-if="notes.length === 0 && !loading" class="text-center text-base-content/50 py-8">
            No notes found.
          </div>
        </div>

        <div class="p-2 border-t border-base-200" v-if="totalPages > 1">
          <div class="join flex justify-center">
            <button
              class="join-item btn btn-sm"
              :disabled="currentPage === 1"
              @click="handlePageChange(currentPage - 1)"
            >
              «
            </button>
            <button class="join-item btn btn-sm">Page {{ currentPage }}</button>
            <button
              class="join-item btn btn-sm"
              :disabled="currentPage === totalPages"
              @click="handlePageChange(currentPage + 1)"
            >
              »
            </button>
          </div>
        </div>
      </div>

      <!-- main Content / Editor / Preview -->
      <div
        class="flex-1 h-full md:ml-4 pb-2"
        :class="{ 'hidden md:block': !isEditing && !isViewing }"
      >
        <!-- Editor -->
        <NoteEditor
          v-if="isEditing"
          :note="selectedNote"
          @save="handleSave"
          @cancel="handleCancel"
        />

        <!-- Preview -->
        <div
          v-else-if="isViewing && selectedNote"
          class="h-full flex flex-col bg-base-100 rounded-box shadow-md"
        >
          <!-- Preview Header -->
          <div class="p-4 border-b border-base-200 flex justify-between items-center">
            <button class="btn btn-ghost btn-sm md:hidden" @click="isViewing = false">
              ← 返回
            </button>
            <div class="flex-1"></div>
            <div class="flex gap-2">
              <button class="btn btn-primary btn-sm" @click="handleEdit(selectedNote)">
                ✏️ 编辑
              </button>
              <button class="btn btn-error btn-sm" @click="handleDelete(selectedNote.id)">
                🗑️ 删除
              </button>
            </div>
          </div>

          <!-- Preview Content -->
          <div class="flex-1 overflow-y-auto p-6">
            <h1 class="text-3xl font-bold mb-4">{{ selectedNote.title || 'Untitled Note' }}</h1>
            <div class="text-sm text-base-content/60 mb-6 flex gap-4">
              <span>📅 创建: {{ formatDate(selectedNote.created_at) }}</span>
              <span>🔄 更新: {{ formatDate(selectedNote.updated_at) }}</span>
            </div>
            <div class="prose dark:prose-invert max-w-none">
              <pre class="whitespace-pre-wrap break-words bg-base-200 p-4 rounded-lg">{{
                selectedNote.content || '暂无内容'
              }}</pre>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-else
          class="h-full flex flex-col items-center justify-center text-base-content/30 bg-base-200 rounded-box"
        >
          <span class="text-6xl mb-4">📝</span>
          <p class="text-xl">Select a note to view or edit</p>
        </div>
      </div>
    </div>
  </div>
</template>
