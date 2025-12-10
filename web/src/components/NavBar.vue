<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ name: 'search', query: { q: searchQuery.value } })
  }
}
</script>

<template>
  <div class="navbar bg-base-100 shadow-sm">
    <div class="flex-1">
      <RouterLink to="/" class="btn btn-ghost text-xl">FileTrace</RouterLink>
    </div>
    <div class="flex-none gap-2">
      <div class="form-control">
        <input
          type="text"
          placeholder="Search..."
          class="input input-bordered w-24 md:w-auto h-8"
          v-model="searchQuery"
          @keyup.enter="handleSearch"
        />
      </div>
      <ul class="menu menu-horizontal px-1">
        <li><RouterLink to="/files">Files</RouterLink></li>
        <li><RouterLink to="/notes">Notes</RouterLink></li>
      </ul>
    </div>
  </div>
</template>
