<script setup>
import { RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'
import ConfirmModal from './components/ConfirmModal.vue'
import { useToast } from './composables/useToast'
import { useConfirm } from './composables/useConfirm'

const { toast } = useToast()
const { state: confirmState, handleConfirm, handleCancel } = useConfirm()
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
    <NavBar />
    <main class="relative">
      <RouterView class="animate-fade-in" />
    </main>
    <ToastMessage v-model="toast.show" :message="toast.message" :type="toast.type" />
    <ConfirmModal
      v-model:show="confirmState.show"
      :title="confirmState.title"
      :message="confirmState.message"
      :confirm-text="confirmState.confirmText"
      :cancel-text="confirmState.cancelText"
      :type="confirmState.type"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    />
  </div>
</template>

<style>
/* 全局样式 */
html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
}

/* 确保深色模式正确应用 */
.dark {
  color-scheme: dark;
}

/* 路由过渡动画 */
.router-view {
  transition: all 0.3s ease;
}

/* 自定义选择样式 */
::selection {
  background: rgba(59, 130, 246, 0.2);
}

/* Focus 样式 */
.focus\:ring-2:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  box-shadow: 0 0 0 2px #3b82f6;
}

/* 打印样式 */
@media print {
  .no-print {
    display: none !important;
  }

  .print-break {
    page-break-before: always;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .btn {
    border: 2px solid;
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
