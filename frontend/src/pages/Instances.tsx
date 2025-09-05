import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useInstances } from '@/hooks/useDashboard'
import * as instancesApi from '@/services/instancesApi'
import { AudiobookshelfInstanceCreate } from '@/types/api'
import toast from 'react-hot-toast'

const Instances: React.FC = () => {
  const { data: instances, isLoading } = useInstances()
  const queryClient = useQueryClient()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState<AudiobookshelfInstanceCreate>({
    name: '',
    base_url: '',
    username: '',
    password: ''
  })

  const createMutation = useMutation({
    mutationFn: instancesApi.createInstance,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instances'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-metrics'] })
      setShowCreateForm(false)
      setFormData({ name: '', base_url: '', username: '', password: '' })
      toast.success('Instance créée avec succès')
    },
    onError: (error: any) => {
      toast.error(`Erreur lors de la création: ${error.message}`)
    }
  })

  const testMutation = useMutation({
    mutationFn: ({ id }: { id: number }) => instancesApi.testInstance(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['instances'] })
      toast.success(`Test réussi - Version: ${data.version || 'N/A'}`)
    },
    onError: (error: any) => {
      toast.error(`Test échoué: ${error.message}`)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: ({ id }: { id: number }) => instancesApi.deleteInstance(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instances'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-metrics'] })
      toast.success('Instance supprimée')
    },
    onError: (error: any) => {
      toast.error(`Erreur lors de la suppression: ${error.message}`)
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.name || !formData.base_url || !formData.username || !formData.password) {
      toast.error('Tous les champs sont requis')
      return
    }
    createMutation.mutate(formData)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-100 text-green-800'
      case 'offline': return 'bg-yellow-100 text-yellow-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online': return 'En ligne'
      case 'offline': return 'Hors ligne'
      case 'error': return 'Erreur'
      default: return 'Inconnu'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestion des instances</h1>
          <p className="text-gray-600 mt-1">
            Gérez vos instances Audiobookshelf et leurs connexions
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {showCreateForm ? 'Annuler' : 'Ajouter une instance'}
        </button>
      </div>

      {/* Formulaire de création */}
      {showCreateForm && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Nouvelle instance</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Nom de l'instance
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Mon Audiobookshelf"
                />
              </div>
              <div>
                <label htmlFor="base_url" className="block text-sm font-medium text-gray-700">
                  URL de base
                </label>
                <input
                  type="url"
                  id="base_url"
                  name="base_url"
                  value={formData.base_url}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="http://localhost:13378"
                />
              </div>
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                  Nom d'utilisateur
                </label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Mot de passe
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Création...' : 'Créer'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Liste des instances */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul role="list" className="divide-y divide-gray-200">
          {instances && instances.length > 0 ? instances.map((instance) => (
            <li key={instance.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(instance.status)}`}>
                    {getStatusText(instance.status)}
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">{instance.name}</h3>
                    <p className="text-sm text-gray-500">{instance.base_url}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-sm text-gray-500">
                    {instance.last_sync ? (
                      <span>Dernière sync: {new Date(instance.last_sync).toLocaleDateString('fr-FR')}</span>
                    ) : (
                      <span className="text-gray-400">Jamais synchronisé</span>
                    )}
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => testMutation.mutate({ id: instance.id })}
                      disabled={testMutation.isPending}
                      className="text-indigo-600 hover:text-indigo-900 text-sm font-medium disabled:opacity-50"
                    >
                      Tester
                    </button>
                    <button
                      onClick={() => {
                        if (window.confirm(`Êtes-vous sûr de vouloir supprimer l'instance "${instance.name}" ?`)) {
                          deleteMutation.mutate({ id: instance.id })
                        }
                      }}
                      disabled={deleteMutation.isPending}
                      className="text-red-600 hover:text-red-900 text-sm font-medium disabled:opacity-50"
                    >
                      Supprimer
                    </button>
                  </div>
                </div>
              </div>
            </li>
          )) : (
            <li className="px-6 py-8">
              <div className="text-center">
                <p className="text-gray-500 text-sm">Aucune instance configurée</p>
                <p className="text-gray-400 text-xs mt-1">
                  Cliquez sur "Ajouter une instance" pour commencer
                </p>
              </div>
            </li>
          )}
        </ul>
      </div>
    </div>
  )
}

export default Instances