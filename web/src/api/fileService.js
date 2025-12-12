import service from '@/utils/service'

export default {
  uploadFiles(formData) {
    return service.post('/v1/files/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  getFiles(params) {
    return service.get('/v1/files/', { params })
  },
  deleteFile(id) {
    return service.delete(`/v1/files/${id}`)
  },
}
