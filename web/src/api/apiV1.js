import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'

const apiV1 = axios.create({
  baseURL: `${baseURL}/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

const noAuthPaths = ['/auth/register', '/auth/login']

const access_token = localStorage.getItem('access_token')

apiV1.interceptors.request.use(
  (config) => {
    if (!noAuthPaths.includes(config.url)) {
      // 请求头里添加 access_token
      config.headers.Authorization = `Bearer ${access_token}`
    }
    return config
  },
  (error) => {
    console.error('请求出错:', error)
    return Promise.reject(error)
  },
)

apiV1.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('响应出错:', error)
    return Promise.reject(error)
  },
)

export default apiV1
