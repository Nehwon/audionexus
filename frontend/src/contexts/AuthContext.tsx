import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User, LoginRequest, LoginResponse, RegisterRequest } from '@/types/api'
import * as authApi from '@/services/authApi'

interface AuthContextType {
  user: User | null
  login: (credentials: LoginRequest) => Promise<void>
  register: (userData: RegisterRequest) => Promise<void>
  logout: () => void
  isLoading: boolean
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const userData = await authApi.getCurrentUser()
        setUser(userData)
      } catch (error) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    }
    setIsLoading(false)
  }

  const login = async (credentials: LoginRequest) => {
    setIsLoading(true)
    try {
      const response: LoginResponse = await authApi.login(credentials)
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      const userData = await authApi.getCurrentUser()
      setUser(userData)
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (userData: RegisterRequest) => {
    setIsLoading(true)
    try {
      await authApi.register(userData)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  const value: AuthContextType = {
    user,
    login,
    register,
    logout,
    isLoading,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}