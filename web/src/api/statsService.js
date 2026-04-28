import service from '@/utils/service'

export function getStats() {
  return service.get('/v1/stats/')
}
