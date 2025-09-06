import api from './authApi'

export interface SyncStatus {
  is_running: boolean
  last_sync?: string
  next_sync?: string
  total_instances: number
  active_instances: number
}

export interface SyncProgress {
  instance_id: number
  name: string
  last_sync?: string
  status: string
  synced_audiobooks: number
  last_error?: string
}

export const getSyncStatus = async (): Promise<SyncStatus> => {
  const response = await api.get('/audiobookshelf/sync/status')
  return response.data
}

export const startSync = async (instanceId: number, fullSync = false): Promise<any> => {
  const response = await api.post(`/audiobookshelf/sync/instances/${instanceId}/sync`, { full_sync: fullSync })
  return response.data
}

export const startAllSync = async (fullSync = false): Promise<any> => {
  const response = await api.post('/audiobookshelf/sync/sync-all', { full_sync: fullSync })
  return response.data
}

export const getSyncProgress = async (instanceId: number): Promise<SyncProgress> => {
  const response = await api.get(`/audiobookshelf/sync/instances/${instanceId}/progress`)
  return response.data
}

export const startScheduler = async (): Promise<any> => {
  const response = await api.post('/audiobookshelf/sync/scheduler/start')
  return response.data
}

export const stopScheduler = async (): Promise<any> => {
  const response = await api.post('/audiobookshelf/sync/scheduler/stop')
  return response.data
}