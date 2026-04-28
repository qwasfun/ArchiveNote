import service from '@/utils/service'

export function createFolder(data) {
  return service.post('/v1/folders/', data)
}

export function getFolders(params) {
  return service.get('/v1/folders/', { params })
}

export function getFolder(id) {
  return service.get(`/v1/folders/${id}`)
}

export function updateFolder(id, data) {
  return service.put(`/v1/folders/${id}`, data)
}

export function deleteFolder(id) {
  return service.delete(`/v1/folders/${id}`)
}

export function batchMoveFolders(data) {
  return service.post('/v1/folders/batch/move', data)
}

export function batchDeleteFolders(data) {
  return service.post('/v1/folders/batch/delete', data)
}

export function getFolderNotes(id) {
  return service.get(`/v1/folders/${id}/notes`)
}

export function attachNotes(id, noteIds) {
  return service.post(`/v1/folders/${id}/attach-notes`, { note_ids: noteIds })
}

export function detachNotes(id, noteIds) {
  return service.post(`/v1/folders/${id}/detach-notes`, { note_ids: noteIds })
}
