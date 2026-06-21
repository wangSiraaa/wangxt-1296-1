import request from './request'

export const getVisitRecords = (params) => {
  return request.get('/visit-records/', { params })
}

export const getVisitRecord = (id) => {
  return request.get(`/visit-records/${id}/`)
}

export const createVisitRecord = (data) => {
  return request.post('/visit-records/', data)
}

export const updateVisitRecord = (id, data) => {
  return request.put(`/visit-records/${id}/`, data)
}

export const deleteVisitRecord = (id) => {
  return request.delete(`/visit-records/${id}/`)
}
