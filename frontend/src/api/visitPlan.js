import request from './request'

export const getVisitPlans = (params) => {
  return request.get('/visit-plans/', { params })
}

export const getVisitPlan = (id) => {
  return request.get(`/visit-plans/${id}/`)
}

export const createVisitPlan = (data) => {
  return request.post('/visit-plans/', data)
}

export const updateVisitPlan = (id, data) => {
  return request.put(`/visit-plans/${id}/`, data)
}

export const deleteVisitPlan = (id) => {
  return request.delete(`/visit-plans/${id}/`)
}

export const cancelVisitPlan = (id) => {
  return request.post(`/visit-plans/${id}/cancel/`)
}

export const batchGeneratePlans = (data) => {
  return request.post('/visit-plans/batch_generate/', data)
}
