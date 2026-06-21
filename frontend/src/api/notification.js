import request from './request'

export const getNotifications = (params) => {
  return request.get('/notifications/', { params })
}

export const getNotification = (id) => {
  return request.get(`/notifications/${id}/`)
}

export const getUnreadCount = () => {
  return request.get('/notifications/unread_count/')
}

export const markNotificationRead = (id) => {
  return request.post(`/notifications/${id}/mark_read/`)
}

export const markAllRead = () => {
  return request.post('/notifications/mark_all_read/')
}

export const markNotificationHandled = (id) => {
  return request.post(`/notifications/${id}/mark_handled/`)
}
