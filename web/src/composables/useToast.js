import { reactive } from 'vue'

// 全局单例状态
const toast = reactive({
  show: false,
  message: '',
  type: 'success',
})

export function useToast() {
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
