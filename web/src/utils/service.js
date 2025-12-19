import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'

// 创建 axios 实例
const service = axios.create({
  baseURL,
  withCredentials: true,
})

const noAuthPaths = ['/auth/register', '/auth/login', '/auth/refresh']

let isRefreshing = false
let requestsQueue = []

service.interceptors.request.use(
  (config) => {
    // 从 Pinia store 获取 token
    const authStore = useAuthStore()
    const access_token = authStore.accessToken

    // 检查当前请求路径是否需要认证
    const isNoAuthPath = noAuthPaths.some((path) => config.url.includes(path))

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
  async (error) => {
    const originalRequest = error.config

    // Handle 401 Unauthorized
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes('/auth/refresh') &&
      !originalRequest.url.includes('/auth/login')
    ) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          requestsQueue.push((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(service(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const data = await service.post('/v1/auth/refresh')
        const { access_token } = data

        const authStore = useAuthStore()
        authStore.updateAccessToken(access_token)

        // Process queue
        requestsQueue.forEach((cb) => cb(access_token))
        requestsQueue = []

        // Retry original request
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return service(originalRequest)
      } catch (refreshError) {
        // Refresh failed
        const authStore = useAuthStore()
        authStore.clearAuth()
        router.push('/auth/login')
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    console.error('响应出错:', error)
    return Promise.reject(error)
  },
)

export default service
