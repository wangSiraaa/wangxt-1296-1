import request from './request'

export const getLocationRecords = (params) => {
  return request.get('/location-records/', { params })
}

export const validateLocation = (data) => {
  return request.post('/location-records/validate/', data)
}
