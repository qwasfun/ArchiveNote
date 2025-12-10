<script setup>
import { RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'
</script>

<template>
  <div class="min-h-screen bg-base-200 flex flex-col">
    <NavBar />
    <main class="flex-1 container mx-auto">
      <RouterView />
    </main>
  </div>
</template>

<style scoped></style>
