import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts'
import { useAdminMetrics } from '@/hooks/useDashboard'
import { useQuery } from '@tanstack/react-query'

const AdminDashboard: React.FC = () => {
  const { data: adminMetrics, isLoading } = useAdminMetrics()

  // Mock trends data for charts
  const trendsData = [
    { date: '2025-01', users: 10, books: 100 },
    { date: '2025-02', users: 15, books: 150 },
    { date: '2025-03', users: 25, books: 250 },
    { date: '2025-04', users: 30, books: 320 },
    { date: '2025-05', users: 35, books: 380 },
    { date: '2025-06', users: 40, books: 450 },
  ]

  const storageData = [
    { name: 'Audiobookshelf', value: adminMetrics?.storage.audiobookshelf || 0 },
    { name: 'Local', value: adminMetrics?.storage.local || 0 },
  ]

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042']

  // Mock upload tasks
  const uploadTasks = [
    { id: '1', filename: 'test.zip', progress: 65, status: 'processing' },
    { id: '2', filename: 'romans.rar', progress: 30, status: 'extracting' }
  ]

  const notifications = [
    { id: '1', type: 'warning', title: 'Stockage élevé', message: 'Storage dépassant 80%', timestamp: '2025-01-01T10:00:00' },
    { id: '2', type: 'info', title: 'Sync terminée', message: 'Synchronisation réussie', timestamp: '2025-01-01T09:30:00' }
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard Administrateur</h1>
        <p className="text-gray-600 dark:text-gray-300 mt-2">
          Vue d'ensemble complète du système AudioNexus
        </p>
      </div>

      {/* Métriques principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">U</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Utilisateurs actifs
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-white">
                    {adminMetrics?.users.active || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">L</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Livres audio
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-white">
                    {adminMetrics?.books.total || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">S</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Stockage total
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-white">
                    {(adminMetrics?.storage.total || 0) / (1024 * 1024 * 1024)}.2f GB
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">C</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Collections
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-white">
                    {adminMetrics?.collections.total_libraries || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Tendance Utilisation</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="users" stroke="#8884d8" strokeWidth={2} />
              <Line type="monotone" dataKey="books" stroke="#82ca9d" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Répartition Stockage</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={storageData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                label
              >
                {storageData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tâches d'upload */}
      <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md mb-8">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
            Tâches d'upload en cours
          </h3>
        </div>
        <div className="border-t border-gray-200 dark:border-gray-700">
          {uploadTasks.length > 0 ? (
            <ul role="list" className="divide-y divide-gray-200 dark:divide-gray-700">
              {uploadTasks.map((task) => (
                <li key={task.id} className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{task.filename}</div>
                      <div className="ml-2 text-xs text-gray-500 dark:text-gray-400">({task.progress}%)</div>
                    </div>
                    <div className="flex items-center">
                      <div className="flex-1 min-w-0 ml-4">
                        <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                          <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${task.progress}%` }}></div>
                        </div>
                      </div>
                      <div className="ml-4 text-sm text-gray-500 dark:text-gray-400">{task.status}</div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-5 sm:p-6">
              <p className="text-gray-500 dark:text-gray-400 text-center">Aucune tâche en cours</p>
            </div>
          )}
        </div>
      </div>

      {/* Notifications */}
      <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
            Notifications et Alertes
          </h3>
        </div>
        <div className="border-t border-gray-200 dark:border-gray-700">
          {notifications.length > 0 ? (
            <ul role="list" className="divide-y divide-gray-200 dark:divide-gray-700">
              {notifications.map((notif) => (
                <li key={notif.id} className="px-4 py-4 sm:px-6">
                  <div className="flex items-start">
                    <div className={`flex-shrink-0 w-3 h-3 rounded-full mt-1 ${
                      notif.type === 'info' ? 'bg-blue-400' :
                      notif.type === 'warning' ? 'bg-yellow-400' :
                      'bg-red-400'
                    }`}></div>
                    <div className="ml-3 flex-1">
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white">{notif.title}</h4>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{notif.message}</p>
                      <p className="text-xs text-gray-400">{new Date(notif.timestamp).toLocaleString('fr-FR')}</p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-5 sm:p-6">
              <p className="text-gray-500 dark:text-gray-400 text-center">Aucune notification</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard