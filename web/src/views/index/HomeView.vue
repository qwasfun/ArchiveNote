<script setup></script>

<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold mb-6">Dashboard</h1>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Recent Files</h2>
          <p>You have 0 files.</p>
          <div class="card-actions justify-end">
            <RouterLink to="/files" class="btn btn-primary">Manage Files</RouterLink>
          </div>
        </div>
      </div>
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Recent Notes</h2>
          <p>You have 0 notes.</p>
          <div class="card-actions justify-end">
            <RouterLink to="/notes" class="btn btn-secondary">Manage Notes</RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
