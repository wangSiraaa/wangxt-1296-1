import request from './request'

export const getStatistics = () => {
  return request.get('/system/statistics/')
}

export const checkMissedVisits = () => {
  return request.post('/system/check_missed_visits/')
}
