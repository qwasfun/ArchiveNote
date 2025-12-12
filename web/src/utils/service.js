import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'

// 创建 axios 实例
const service = axios.create({
  baseURL,
})

const noAuthPaths = ['/auth/register', '/auth/login']

service.interceptors.request.use(
  (config) => {
    // 从 Pinia store 获取 token
    const authStore = useAuthStore()
    const access_token = authStore.accessToken
    
    // 检查当前请求路径是否需要认证
    const isNoAuthPath = noAuthPaths.some(path => config.url.includes(path))
    
    if (!isNoAuthPath && access_token) {
      // 请求头里添加 access_token
      config.headers.Authorization = `Bearer ${access_token}`
    }
    return config
  },
  (error) => {
    console.error('请求异常:', error)
    return Promise.reject(error)
  },
)

service.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('响应出错:', error)
    return Promise.reject(error)
  },
)

export default service
