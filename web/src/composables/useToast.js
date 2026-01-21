import { reactive } from 'vue'

export function useToast() {
  const toast = reactive({
    show: false,
    message: '',
    type: 'success',
  })

  const showToast = (message, type = 'success') => {
    toast.message = message
    toast.type = type
    toast.show = true
  }

  return {
    toast,
    showToast,
  }
}
