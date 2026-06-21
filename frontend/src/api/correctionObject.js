import request from './request'

export const getCorrectionObjects = (params) => {
  return request.get('/correction-objects/', { params })
}

export const getCorrectionObject = (id) => {
  return request.get(`/correction-objects/${id}/`)
}

export const createCorrectionObject = (data) => {
  return request.post('/correction-objects/', data)
}

export const updateCorrectionObject = (id, data) => {
  return request.put(`/correction-objects/${id}/`, data)
}

export const deleteCorrectionObject = (id) => {
  return request.delete(`/correction-objects/${id}/`)
}

export const changeRiskLevel = (id, data) => {
  return request.post(`/correction-objects/${id}/change_risk_level/`, data)
}

export const generateMonthlyPlans = (id) => {
  return request.post(`/correction-objects/${id}/generate_monthly_plans/`)
}
