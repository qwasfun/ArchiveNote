import { reactive } from 'vue'

const state = reactive({
  show: false,
  title: '确认',
  message: '',
  confirmText: '确认',
  cancelText: '取消',
  type: 'info',
  resolvePromise: null,
  rejectPromise: null,
})

export function useConfirm() {
  const confirm = (message, options = {}) => {
    return new Promise((resolve, reject) => {
      state.show = true
      state.message = message
      state.title = options.title || '确认'
      state.confirmText = options.confirmText || '确认'
      state.cancelText = options.cancelText || '取消'
      state.type = options.type || 'info'
      state.resolvePromise = resolve
      state.rejectPromise = reject
    })
  }

  const handleConfirm = () => {
    if (state.resolvePromise) {
      state.resolvePromise(true)
    }
    resetState()
  }

  const handleCancel = () => {
    if (state.rejectPromise) {
      state.rejectPromise(false)
    }
    resetState()
  }

  const resetState = () => {
    state.show = false
    state.resolvePromise = null
    state.rejectPromise = null
  }

  return {
    state,
    confirm,
    handleConfirm,
    handleCancel,
  }
}

// 导出一个全局单例
export const confirmState = state
