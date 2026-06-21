import request from './request'

export const getFamilyFeedbacks = (params) => {
  return request.get('/family-feedbacks/', { params })
}

export const getFamilyFeedback = (id) => {
  return request.get(`/family-feedbacks/${id}/`)
}

export const createFamilyFeedback = (data) => {
  return request.post('/family-feedbacks/', data)
}

export const updateFamilyFeedback = (id, data) => {
  return request.put(`/family-feedbacks/${id}/`, data)
}

export const deleteFamilyFeedback = (id) => {
  return request.delete(`/family-feedbacks/${id}/`)
}

export const reviewFamilyFeedback = (id, data) => {
  return request.post(`/family-feedbacks/${id}/review/`, data)
}
