import { useQuery } from '@tanstack/react-query'
import * as instancesApi from '@/services/instancesApi'
import * as syncApi from '@/services/syncApi'

export interface DashboardMetrics {
  total_instances: number
  active_instances: number
  total_audiobooks: number
  recent_syncs: number
  system_health: 'healthy' | 'warning' | 'error'
}

export const useDashboardMetrics = () => {
  return useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async (): Promise<DashboardMetrics> => {
      // Récupérer les instances
      const instances = await instancesApi.getInstances()

      // Calculer les métriques
      const total_instances = instances.length
      const active_instances = instances.filter(i => i.status === 'online').length
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
        system_health
      }
    },
    refetchInterval: 30000, // Rafraîchir toutes les 30 secondes
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