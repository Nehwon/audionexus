import api from './authApi'
import { AudiobookshelfInstance, AudiobookshelfInstanceCreate, AudiobookshelfInstanceUpdate } from '@/types/api'

export const getInstances = async (onlyActive = true): Promise<AudiobookshelfInstance[]> => {
  const response = await api.get(`/audiobookshelf/instances?only_active=${onlyActive}`)
  return response.data.instances || []
}

export const getInstance = async (id: number): Promise<AudiobookshelfInstance> => {
  const response = await api.get(`/audiobookshelf/instances/${id}`)
  return response.data
}

export const createInstance = async (data: AudiobookshelfInstanceCreate): Promise<AudiobookshelfInstance> => {
  const response = await api.post('/audiobookshelf/instances', data)
  return response.data
}

export const updateInstance = async (id: number, data: AudiobookshelfInstanceUpdate): Promise<AudiobookshelfInstance> => {
  const response = await api.put(`/audiobookshelf/instances/${id}`, data)
  return response.data
}

export const deleteInstance = async (id: number): Promise<void> => {
  await api.delete(`/audiobookshelf/instances/${id}`)
}

export const testInstance = async (id: number): Promise<any> => {
  const response = await api.post(`/audiobookshelf/instances/${id}/test`)
  return response.data
}

export const rotateInstanceToken = async (id: number, password: string): Promise<AudiobookshelfInstance> => {
  const response = await api.post(`/audiobookshelf/instances/${id}/rotate-token`, { password })
  return response.data
}