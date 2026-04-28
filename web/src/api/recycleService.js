import service from '@/utils/service'

export function getItems() {
  return service.get('/v1/recycle/items')
}

export function restoreItems(data) {
  return service.post('/v1/recycle/restore', data)
}

export function permanentDeleteItems(data) {
  return service.delete('/v1/recycle/permanent', { data })
}
