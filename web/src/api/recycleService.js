import service from '@/utils/service'

export default {
  getItems() {
    return service.get('/v1/recycle/items')
  },
  restoreItems(data) {
    return service.post('/v1/recycle/restore', data)
  },
  permanentDeleteItems(data) {
    return service.delete('/v1/recycle/permanent', { data })
  },
}
