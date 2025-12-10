import apiV1 from './apiV1'

export default {
  createNote(noteData) {
    return apiV1.post('/notes/', noteData)
  },
  getNotes(params) {
    return apiV1.get('/notes/', { params })
  },
  getNote(id) {
    return apiV1.get(`/notes/${id}`)
  },
  updateNote(id, noteData) {
    return apiV1.put(`/notes/${id}`, noteData)
  },
  deleteNote(id) {
    return apiV1.delete(`/notes/${id}`)
  },
  attachFiles(id, fileIds) {
    return apiV1.post(`/notes/${id}/attach`, fileIds)
  },
  detachFiles(id, fileIds) {
    return apiV1.post(`/notes/${id}/detach`, fileIds)
  },
}
