import service from '@/utils/service'

// 获取默认存储后端配置（普通用户也可访问）
export function getDefaultBackend() {
  return service.get('/v1/storage-backends/default')
}

// 获取所有存储后端
export function getBackends() {
  return service.get('/v1/storage-backends')
}

// 获取指定存储后端
export function getBackend(id) {
  return service.get(`/v1/storage-backends/${id}`)
}

// 创建存储后端
export function createBackend(data) {
  return service.post('/v1/storage-backends', data)
}

// 更新存储后端
export function updateBackend(id, data) {
  return service.put(`/v1/storage-backends/${id}`, data)
}

// 删除存储后端
export function deleteBackend(id) {
  return service.delete(`/v1/storage-backends/${id}`)
}

// 设置默认存储后端
export function setDefaultBackend(id) {
  return service.post(`/v1/storage-backends/${id}/set-default`)
}

// 测试存储后端连接
export function testBackend(id) {
  return service.post(`/v1/storage-backends/${id}/test`)
}

// 导出存储配置
export function exportConfig() {
  return service.get('/v1/storage-backends/export/config')
}

// 导入存储配置
export function importConfig(formData, replaceExisting = false) {
  return service.post(
    `/v1/storage-backends/import/config?replace_existing=${replaceExisting}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    },
  )
}
