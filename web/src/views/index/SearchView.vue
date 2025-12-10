<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import fileService from '../../api/fileService.js'
import noteService from '../../api/noteService.js'
import FileGrid from '../../components/FileGrid.vue'

const route = useRoute()
const query = ref('')
const files = ref([])
const notes = ref([])
const loading = ref(false)

const performSearch = async () => {
  if (!query.value) return
  loading.value = true
  try {
    const [filesRes, notesRes] = await Promise.all([
      fileService.getFiles({ q: query.value }),
      noteService.getNotes({ q: query.value }),
    ])
    files.value = filesRes.data
    notes.value = notesRes.data
  } catch (error) {
    console.error('Search failed', error)
  } finally {
    loading.value = false
  }
}

watch(
  () => route.query.q,
  (newQ) => {
    query.value = newQ
    performSearch()
  },
  { immediate: true },
)
</script>

<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold mb-6">Search Results for "{{ query }}"</h1>

    <div v-if="loading" class="flex justify-center p-8">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <div v-else class="space-y-8">
      <!-- Notes Results -->
      <section>
        <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
          <span>📝</span> Notes ({{ notes.length }})
        </h2>
        <div v-if="notes.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="note in notes"
            :key="note.id"
            class="card bg-base-100 shadow-sm hover:shadow-md cursor-pointer"
            @click="$router.push('/notes')"
          >
            <div class="card-body p-4">
              <h3 class="font-bold truncate">{{ note.title || 'Untitled Note' }}</h3>
              <p class="text-xs text-base-content/60 line-clamp-3">{{ note.content }}</p>
              <div class="card-actions justify-end mt-2">
                <span class="text-xs text-base-content/40">ID: {{ note.id }}</span>
              </div>
            </div>
          </div>
        </div>
        <p v-else class="text-base-content/50 italic">No notes found.</p>
      </section>

      <!-- Files Results -->
      <section>
        <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
          <span>📂</span> Files ({{ files.length }})
        </h2>
        <div v-if="files.length > 0">
          <FileGrid :files="files" />
        </div>
        <p v-else class="text-base-content/50 italic">No files found.</p>
      </section>
    </div>
  </div>
</template>
