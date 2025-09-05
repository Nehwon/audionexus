import React from 'react'
import { useMutation } from '@tanstack/react-query'
import { useSyncStatus, useInstances } from '@/hooks/useDashboard'
import * as syncApi from '@/services/syncApi'
import toast from 'react-hot-toast'

const Sync: React.FC = () => {
  const { data: syncStatus, isLoading: syncLoading } = useSyncStatus()
  const { data: instances, isLoading: instancesLoading } = useInstances()

  const startSyncMutation = useMutation({
    mutationFn: ({ instanceId, fullSync }: { instanceId: number; fullSync: boolean }) =>
      syncApi.startSync(instanceId, fullSync),
    onSuccess: () => {
      toast.success('Synchronisation lancée')
    },
    onError: (error: any) => {
      toast.error(`Erreur lors du lancement: ${error.message}`)
    }
  })

  const startAllSyncMutation = useMutation({
    mutationFn: ({ fullSync }: { fullSync: boolean }) =>
      syncApi.startAllSync(fullSync),
    onSuccess: () => {
      toast.success('Synchronisation de toutes les instances lancée')
    },
    onError: (error: any) => {
      toast.error(`Erreur lors du lancement: ${error.message}`)
    }
  })

  const startSchedulerMutation = useMutation({
    mutationFn: syncApi.startScheduler,
    onSuccess: () => {
      toast.success('Planificateur de synchronisation démarré')
    },
    onError: (error: any) => {
      toast.error(`Erreur: ${error.message}`)
    }
  })

  const stopSchedulerMutation = useMutation({
    mutationFn: syncApi.stopScheduler,
    onSuccess: () => {
      toast.success('Planificateur de synchronisation arrêté')
    },
    onError: (error: any) => {
      toast.error(`Erreur: ${error.message}`)
    }
  })

  const handleStartSync = (instanceId: number, fullSync = false) => {
    startSyncMutation.mutate({ instanceId, fullSync })
  }

  const handleStartAllSync = (fullSync = false) => {
    startAllSyncMutation.mutate({ fullSync })
  }

  const handleSchedulerToggle = () => {
    if (syncStatus?.is_running) {
      stopSchedulerMutation.mutate()
    } else {
      startSchedulerMutation.mutate()
    }
  }

  if (syncLoading || instancesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  const activeInstances = instances?.filter(i => i.status === 'online') || []

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Gestion de la synchronisation</h1>
        <p className="text-gray-600 mt-1">
          Contrôlez la synchronisation de vos instances Audiobookshelf
        </p>
      </div>

      {/* État du planificateur */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-medium text-gray-900">Planificateur automatique</h2>
            <p className="text-sm text-gray-500 mt-1">
              Synchronisation automatique en arrière-plan
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                syncStatus?.is_running ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {syncStatus?.is_running ? 'Actif' : 'Inactif'}
              </span>
            </div>
            <button
              onClick={handleSchedulerToggle}
              disabled={startSchedulerMutation.isPending || stopSchedulerMutation.isPending}
              className={`px-4 py-2 text-sm font-medium rounded-md ${
                syncStatus?.is_running
                  ? 'text-red-700 bg-red-100 hover:bg-red-200'
                  : 'text-green-700 bg-green-100 hover:bg-green-200'
              } disabled:opacity-50`}
            >
              {syncStatus?.is_running ? 'Arrêter' : 'Démarrer'}
            </button>
          </div>
        </div>

        {syncStatus?.last_sync && (
          <div className="mt-4 text-sm text-gray-600">
            Dernière synchronisation: {new Date(syncStatus.last_sync).toLocaleString('fr-FR')}
          </div>
        )}
      </div>

      {/* Synchronisation manuelle */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Synchronisation manuelle</h2>

        <div className="space-y-4">
          {/* Synchronisation de toutes les instances */}
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="text-sm font-medium text-gray-900">Toutes les instances actives</h3>
              <p className="text-sm text-gray-500">
                {activeInstances.length} instance(s) disponible(s)
              </p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => handleStartAllSync(false)}
                disabled={startAllSyncMutation.isPending || activeInstances.length === 0}
                className="px-3 py-1 text-sm font-medium text-blue-700 bg-blue-100 hover:bg-blue-200 rounded-md disabled:opacity-50"
              >
                Sync incrémentielle
              </button>
              <button
                onClick={() => handleStartAllSync(true)}
                disabled={startAllSyncMutation.isPending || activeInstances.length === 0}
                className="px-3 py-1 text-sm font-medium text-purple-700 bg-purple-100 hover:bg-purple-200 rounded-md disabled:opacity-50"
              >
                Sync complète
              </button>
            </div>
          </div>

          {/* Synchronisation individuelle */}
          {activeInstances.map((instance) => (
            <div key={instance.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div>
                <h3 className="text-sm font-medium text-gray-900">{instance.name}</h3>
                <p className="text-sm text-gray-500">{instance.base_url}</p>
                {instance.last_sync && (
                  <p className="text-xs text-gray-400">
                    Dernière sync: {new Date(instance.last_sync).toLocaleDateString('fr-FR')}
                  </p>
                )}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleStartSync(instance.id, false)}
                  disabled={startSyncMutation.isPending}
                  className="px-3 py-1 text-sm font-medium text-blue-700 bg-blue-100 hover:bg-blue-200 rounded-md disabled:opacity-50"
                >
                  Sync incrémentielle
                </button>
                <button
                  onClick={() => handleStartSync(instance.id, true)}
                  disabled={startSyncMutation.isPending}
                  className="px-3 py-1 text-sm font-medium text-purple-700 bg-purple-100 hover:bg-purple-200 rounded-md disabled:opacity-50"
                >
                  Sync complète
                </button>
              </div>
            </div>
          ))}

          {activeInstances.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>Aucune instance active trouvée</p>
              <p className="text-sm mt-1">
                Configurez et activez des instances dans l'onglet "Instances"
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Historique des synchronisations */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Historique récent</h2>

        <div className="space-y-3">
          {instances?.filter(i => i.last_sync).map((instance) => (
            <div key={instance.id} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-md">
              <div className="flex items-center space-x-3">
                <div className={`w-2 h-2 rounded-full ${
                  instance.status === 'online' ? 'bg-green-400' : 'bg-gray-400'
                }`}></div>
                <span className="text-sm font-medium text-gray-900">{instance.name}</span>
              </div>
              <span className="text-sm text-gray-500">
                {instance.last_sync ? new Date(instance.last_sync).toLocaleString('fr-FR') : 'Jamais'}
              </span>
            </div>
          ))}

          {(!instances || instances.filter(i => i.last_sync).length === 0) && (
            <p className="text-sm text-gray-500 text-center py-4">
              Aucune synchronisation effectuée pour le moment
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Sync