import axios from 'axios'
import { LoginRequest, LoginResponse, RegisterRequest, User } from '@/types/api'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await api.post('/auth/login', credentials)
  return response.data
}

export const register = async (userData: RegisterRequest): Promise<User> => {
  const response = await api.post('/auth/register', userData)
  return response.data
}

export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get('/auth/me')
  return response.data
}

export const refreshToken = async (): Promise<LoginResponse> => {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) {
    throw new Error('No refresh token available')
  }

  const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
  return response.data
}

export default api