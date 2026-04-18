import React from 'react'
import { useDashboardMetrics, useInstances, useSyncStatus } from '@/hooks/useDashboard'

const Dashboard: React.FC = () => {
  const { data: metrics, isLoading: metricsLoading } = useDashboardMetrics()
  const { data: instances, isLoading: instancesLoading } = useInstances()
  const { data: syncStatus, isLoading: syncLoading } = useSyncStatus()

  if (metricsLoading || instancesLoading || syncLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'text-green-600 bg-green-100'
      case 'warning': return 'text-yellow-600 bg-yellow-100'
      case 'error': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getHealthText = (health: string) => {
    switch (health) {
      case 'healthy': return 'Sain'
      case 'warning': return 'Attention'
      case 'error': return 'Erreur'
      default: return 'Inconnu'
    }
  }

  return (
    <div className="px-2 sm:px-0">
      <div className="mb-6 sm:mb-8">
        <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">Dashboard AudioNexus</h1>
        <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-2">
          Vue d'ensemble de vos instances Audiobookshelf
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
        {/* Instances actives */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">I</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Instances actives
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {metrics?.active_instances || 0} / {metrics?.total_instances || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Livres audio */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">L</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Livres audio synchronisés
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {metrics?.total_audiobooks || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Synchronisations récentes */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">S</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Sync. récentes
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {metrics?.recent_syncs || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Santé système */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${getHealthColor(metrics?.system_health || 'healthy')}`}>
                  <span className="text-white text-sm font-medium">H</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Santé système
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {getHealthText(metrics?.system_health || 'healthy')}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* État de synchronisation */}
      {syncStatus && (
        <div className="bg-white shadow overflow-hidden sm:rounded-md mb-8">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Statut de synchronisation
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              État actuel du système de synchronisation automatique.
            </p>
          </div>
          <div className="border-t border-gray-200">
            <div className="px-4 py-5 sm:p-6">
               <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">État:</span>
                  <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${
                    syncStatus.is_running ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {syncStatus.is_running ? 'En cours' : 'Arrêté'}
                  </span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Dernière sync:</span>
                  <span className="ml-2 text-sm text-gray-900">
                    {syncStatus.last_sync ? new Date(syncStatus.last_sync).toLocaleString('fr-FR') : 'Jamais'}
                  </span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Prochaine sync:</span>
                  <span className="ml-2 text-sm text-gray-900">
                    {syncStatus.next_sync ? new Date(syncStatus.next_sync).toLocaleString('fr-FR') : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Métriques d'upload */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md mb-8">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Téléversements d'Audiobooks
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Statistiques des uploads et métriques de stockage.
          </p>
        </div>
        <div className="border-t border-gray-200">
          <div className="px-4 py-5 sm:p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
              {/* Total uploadés */}
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 mx-auto rounded-lg flex items-center justify-center mb-2">
                  <span className="text-blue-600 dark:text-blue-400 text-xl">📚</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {metrics?.uploaded_audiobooks?.total || 0}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total uploadés</p>
              </div>

              {/* Réussis */}
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900 mx-auto rounded-lg flex items-center justify-center mb-2">
                  <span className="text-green-600 dark:text-green-400 text-xl">✓</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {metrics?.uploaded_audiobooks?.successful || 0}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Réussis</p>
              </div>

              {/* En cours */}
              <div className="text-center">
                <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900 mx-auto rounded-lg flex items-center justify-center mb-2">
                  <span className="text-yellow-600 dark:text-yellow-400 text-xl">⏳</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {metrics?.uploaded_audiobooks?.processing || 0}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">En cours</p>
              </div>

              {/* Stockage */}
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 mx-auto rounded-lg flex items-center justify-center mb-2">
                  <span className="text-purple-600 dark:text-purple-400 text-xl">💾</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Math.round(metrics?.uploaded_audiobooks?.total_size_gb || 0)}G
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Stockage</p>
              </div>
            </div>

            {/* Taux de succès et période */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Taux de succès
                </h4>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {metrics?.upload_success_rate || 0}%
                </p>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Uploads récents (24h)
                </h4>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {metrics?.uploaded_audiobooks?.last_24h || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Liste des instances */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Instances Audiobookshelf
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Vue d'ensemble de vos instances configurées.
          </p>
        </div>
        <div className="border-t border-gray-200">
          {instances && instances.length > 0 ? (
            <ul role="list" className="divide-y divide-gray-200">
              {instances.map((instance) => (
                <li key={instance.id} className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${
                        instance.status === 'online' ? 'bg-green-400' :
                        instance.status === 'offline' ? 'bg-yellow-400' : 'bg-red-400'
                      }`}></div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{instance.name}</p>
                        <p className="text-sm text-gray-500">{instance.base_url}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">
                        {instance.last_sync ? `Sync: ${new Date(instance.last_sync).toLocaleDateString('fr-FR')}` : 'Jamais synchronisé'}
                      </p>
                      {instance.version && (
                        <p className="text-xs text-gray-400">v{instance.version}</p>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-5 sm:p-6">
              <p className="text-gray-500 text-center">Aucune instance configurée pour le moment.</p>
              <p className="text-gray-400 text-sm text-center mt-2">
                Allez dans l'onglet "Instances" pour en ajouter une.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard