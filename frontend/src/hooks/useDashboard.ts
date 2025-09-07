import { useQuery } from '@tanstack/react-query'
import * as instancesApi from '@/services/instancesApi'
import * as syncApi from '@/services/syncApi'

export interface DashboardMetrics {
  total_instances: number
  active_instances: number
  total_audiobooks: number
  recent_syncs: number
  system_health: 'healthy' | 'warning' | 'error'
  // Nouvelles métriques pour les uploads
  uploaded_audiobooks: UploadStats
  upload_success_rate: number
  recent_uploads: number
}

export interface UploadStats {
  total: number
  successful: number
  failed: number
  processing: number
  total_size_gb: number
  last_24h: number
  this_week: number
  this_month: number
}

export interface AdminMetrics {
  users: {
    total: number
    active: number
    superusers: number
    recent: number
  }
  books: {
    total: number
    audiobookshelf: number
    local: number
    finished: number
  }
  usage: {
    total_progress: number
    recent_activity: number
  }
  storage: {
    total: number
    audiobookshelf: number
    local: number
  }
  collections: {
    total_libraries: number
  }
  timestamp: string
}

// Hook for regular dashboard metrics
export const useDashboardMetrics = () => {
  return useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async (): Promise<DashboardMetrics> => {
      // Récupérer les instances
      const instances = await instancesApi.getInstances()

      // Calculer les métriques
      const total_instances = instances.length
      const active_instances = instances.filter(i => i.status === 'online').length

      // Essayer de récupérer les vraies métriques admin (fallback si pas disponible)
  try {
    const response = await fetch('/api/admin/metrics', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
    if (response.ok) {
      const adminMetrics: AdminMetrics = await response.json()
      return {
        total_instances,
        active_instances,
        total_audiobooks: adminMetrics.books.total,
        recent_syncs: instances.filter(i => i.last_sync).length,
        system_health: active_instances === total_instances ? 'healthy' : (active_instances > total_instances / 2 ? 'warning' : 'error'),
        // Métriques d'upload (à développer avec une vraie API)
        uploaded_audiobooks: {
          total: 0,
          successful: 0,
          failed: 0,
          processing: 0,
          total_size_gb: 0,
          last_24h: 0,
          this_week: 0,
          this_month: 0
        },
        upload_success_rate: 100,
        recent_uploads: 0
      }
    }
  } catch {
    // Fallback to basic calculation
  }

      const total_audiobooks = instances.reduce((acc, instance) => acc + (instance.id || 0), 0) // Placeholder
      const recent_syncs = instances.filter(i => i.last_sync).length

      // Déterminer la santé système
      let system_health: 'healthy' | 'warning' | 'error' = 'healthy'
      const errorInstances = instances.filter(i => i.status === 'error').length
      const offlineInstances = instances.filter(i => i.status === 'offline').length

      if (errorInstances > 0) {
        system_health = 'error'
      } else if (offlineInstances > 0) {
        system_health = 'warning'
      }

      return {
        total_instances,
        active_instances,
        total_audiobooks,
        recent_syncs,
        system_health,
        // Métriques d'upload (vides pour l'instant)
        uploaded_audiobooks: {
          total: 0,
          successful: 0,
          failed: 0,
          processing: 0,
          total_size_gb: 0,
          last_24h: 0,
          this_week: 0,
          this_month: 0
        },
        upload_success_rate: 100,
        recent_uploads: 0
      }
    },
    refetchInterval: 30000, // Rafraîchir toutes les 30 secondes
  })
}

// Hook for admin metrics
export const useAdminMetrics = () => {
  return useQuery({
    queryKey: ['admin-metrics'],
    queryFn: async (): Promise<AdminMetrics> => {
      const response = await fetch('/api/admin/metrics', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })
      if (!response.ok) {
        throw new Error('Failed to fetch admin metrics')
      }
      return response.json()
    },
    refetchInterval: 30000
  })
}

export const useInstances = () => {
  return useQuery({
    queryKey: ['instances'],
    queryFn: () => instancesApi.getInstances(),
    refetchInterval: 30000,
  })
}

export const useSyncStatus = () => {
  return useQuery({
    queryKey: ['sync-status'],
    queryFn: () => syncApi.getSyncStatus(),
    refetchInterval: 5000, // Rafraîchir toutes les 5 secondes
  })
}