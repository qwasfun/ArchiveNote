import service from '@/utils/service'

export function createNote(noteData) {
  return service.post('/v1/notes/', noteData)
}

export function getNotes(params) {
  return service.get('/v1/notes/', { params })
}

export function getNote(id) {
  return service.get(`/v1/notes/${id}`)
}

export function getNotesByFileId(fileId) {
  return service.get('/v1/notes/', { params: { file_id: fileId } })
}

export function getNotesByFolderId(folderId) {
  return service.get('/v1/notes/', { params: { folder_id: folderId } })
}

export function updateNote(id, noteData) {
  return service.put(`/v1/notes/${id}`, noteData)
}

export function deleteNote(id) {
  return service.delete(`/v1/notes/${id}`)
}

export function attachFiles(id, fileIds) {
  return service.post(`/v1/notes/${id}/attach`, { file_ids: fileIds })
}

export function detachFiles(id, fileIds) {
  return service.post(`/v1/notes/${id}/detach`, { file_ids: fileIds })
}

export function attachFolders(id, folderIds) {
  return service.post(`/v1/notes/${id}/attach-folders`, { folder_ids: folderIds })
}

export function detachFolders(id, folderIds) {
  return service.post(`/v1/notes/${id}/detach-folders`, { folder_ids: folderIds })
}
