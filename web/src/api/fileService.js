import apiV1 from './apiV1.js'

export default {
  uploadFiles(formData) {
    return apiV1.post('/files/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  getFiles(params) {
    return apiV1.get('/files/', { params })
  },
  deleteFile(id) {
    return apiV1.delete(`/files/${id}`)
  },
}
