import service from '@/utils/service'

export function register(formData) {
  return service.post('/v1/auth/register', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

export function login(formData) {
  return service.post('/v1/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

export function refreshToken() {
  return service.post('/v1/auth/refresh')
}

export function logout() {
  return service.post('/v1/auth/logout')
}
