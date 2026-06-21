import { defineStore } from 'pinia'
import { login, getUserProfile, register } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    refreshToken: localStorage.getItem('refreshToken') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    userRole: (state) => state.user?.role || '',
    userName: (state) => state.user?.real_name || state.user?.username || '',
  },

  actions: {
    async login(credentials) {
      const response = await login(credentials)
      this.token = response.access
      this.refreshToken = response.refresh
      this.user = response.user
      localStorage.setItem('token', response.access)
      localStorage.setItem('refreshToken', response.refresh)
      localStorage.setItem('user', JSON.stringify(response.user))
      return response
    },

    async register(data) {
      const response = await register(data)
      return response
    },

    async fetchProfile() {
      const response = await getUserProfile()
      this.user = response
      localStorage.setItem('user', JSON.stringify(response))
      return response
    },

    logout() {
      this.token = ''
      this.refreshToken = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
    },

    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
    },
  },
})
