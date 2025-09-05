export interface User {
  id: number
  username: string
  email: string
  full_name: string
  is_active: boolean
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  refresh_token: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface AudiobookshelfInstance {
  id: number
  name: string
  base_url: string
  username: string
  is_active: boolean
  status: 'online' | 'offline' | 'error'
  version?: string
  last_sync?: string
  last_error?: string
  created_at: string
}

export interface AudiobookshelfInstanceCreate {
  name: string
  base_url: string
  username: string
  password: string
}

export interface AudiobookshelfInstanceUpdate {
  name?: string
  base_url?: string
  is_active?: boolean
}

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

export interface DashboardMetrics {
  total_instances: number
  active_instances: number
  total_audiobooks: number
  recent_syncs: number
  system_health: 'healthy' | 'warning' | 'error'
}