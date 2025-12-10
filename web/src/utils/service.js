import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'

// 创建 axios 实例
const service = axios.create({
  baseURL,
})

const noAuthPaths = ['/auth/register', '/auth/login']

const access_token = localStorage.getItem('access_token')

service.interceptors.request.use(
  (config) => {
    if (!noAuthPaths.includes(baseURL)) {
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
