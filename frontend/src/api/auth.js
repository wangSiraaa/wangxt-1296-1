import request from './request'

export const login = (data) => {
  return request.post('/auth/login/', data)
}

export const register = (data) => {
  return request.post('/auth/register/', data)
}

export const refreshToken = (refresh) => {
  return request.post('/auth/refresh/', { refresh })
}

export const getUserProfile = () => {
  return request.get('/auth/profile/')
}

export const updateUserProfile = (data) => {
  return request.put('/auth/profile/', data)
}

export const getUserList = (params) => {
  return request.get('/auth/users/', { params })
}
