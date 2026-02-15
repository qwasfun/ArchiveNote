<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '确认',
  },
  message: {
    type: String,
    required: true,
  },
  confirmText: {
    type: String,
    default: '确认',
  },
  cancelText: {
    type: String,
    default: '取消',
  },
  type: {
    type: String,
    default: 'info', // info, warning, error, success
    validator: (value) => ['info', 'warning', 'error', 'success'].includes(value),
  },
})

const emit = defineEmits(['confirm', 'cancel', 'update:show'])

const modalRef = ref(null)

const confirmButtonClass = computed(() => {
  const typeMap = {
    info: 'btn-primary',
    warning: 'btn-warning',
    error: 'btn-error',
    success: 'btn-success',
  }
  return typeMap[props.type] || 'btn-primary'
})

watch(
  () => props.show,
  (newVal) => {
    if (newVal && modalRef.value) {
      modalRef.value.showModal()
    } else if (!newVal && modalRef.value) {
      modalRef.value.close()
    }
  },
)

const handleConfirm = () => {
  emit('confirm')
  emit('update:show', false)
  if (modalRef.value) {
    modalRef.value.close()
  }
}

const handleCancel = () => {
  emit('cancel')
  emit('update:show', false)
  if (modalRef.value) {
    modalRef.value.close()
  }
}
</script>

<template>
  <dialog ref="modalRef" class="modal modal-bottom sm:modal-middle">
    <div class="modal-box">
      <h3 class="text-lg font-bold">{{ title }}</h3>
      <p class="py-4">{{ message }}</p>
      <div class="modal-action">
        <button type="button" class="btn" @click="handleCancel">
          {{ cancelText }}
        </button>
        <button type="button" :class="['btn', confirmButtonClass]" @click="handleConfirm">
          {{ confirmText }}
        </button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop" @click="handleCancel">
      <button type="button">close</button>
    </form>
  </dialog>
</template>
