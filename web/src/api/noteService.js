import service from '@/utils/service'

export default {
  createNote(noteData) {
    return service.post('/v1/v1/notes/', noteData)
  },
  getNotes(params) {
    return service.get('/v1/notes/', { params })
  },
  getNote(id) {
    return service.get(`/v1/notes/${id}`)
  },
  getNotesByFileId(fileId) {
    return service.get('/v1/notes/', { params: { file_id: fileId } })
  },
  updateNote(id, noteData) {
    return service.put(`/v1/notes/${id}`, noteData)
  },
  deleteNote(id) {
    return service.delete(`/v1/notes/${id}`)
  },
  attachFiles(id, fileIds) {
    return service.post(`/v1/notes/${id}/attach`, fileIds)
  },
  detachFiles(id, fileIds) {
    return service.post(`/v1/notes/${id}/detach`, fileIds)
  },
}
