import React, { useState, useCallback, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileAudio, AlertCircle, CheckCircle, X, Play, Pause } from 'lucide-react'
import toast from 'react-hot-toast'

interface UploadTask {
  task_id: string
  status: 'processing' | 'completed' | 'failed' | 'cancelled'
  filename: string
  file_size: number
  progress: number
  current_step: string
  error_message?: string
  metadata?: {
    title?: string
    artist?: string
    album?: string
    year?: string
    genre?: string
    duration?: number
    format?: string
  }
}

interface AudiobookUploaderProps {
  onUploadComplete?: (task: UploadTask) => void
  maxFileSize?: number // en MB
}

const AudiobookUploader: React.FC<AudiobookUploaderProps> = ({
  onUploadComplete,
  maxFileSize = 500
}) => {
  const [uploadTasks, setUploadTasks] = useState<UploadTask[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Formats acceptés
  const acceptedFormats = {
    'application/zip': ['.zip'],
    'application/x-rar-compressed': ['.rar'],
    'application/x-7z-compressed': ['.7z'],
    'application/x-tar': ['.tar.gz', '.tar.bz2']
  }

  // Validation côté client
  const validateFile = (file: File): string | null => {
    // Vérification de la taille
    if (file.size > maxFileSize * 1024 * 1024) {
      return `Fichier trop volumineux (max: ${maxFileSize}MB)`
    }

    // Vérification du type MIME
    const allowedMimes = Object.keys(acceptedFormats)
    if (!allowedMimes.includes(file.type) && file.type !== '') {
      // Vérifier aussi l'extension si le type MIME n'est pas reconnu
      const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
      const isValidExtension = Object.values(acceptedFormats)
        .some(extensions => extensions.includes(extension))

      if (!isValidExtension) {
        return 'Format non supporté. Utilisez ZIP, RAR, 7Z ou TAR'
      }
    }

    return null
  }

  // Gestionnaire d'upload
  const handleUpload = async (files: File[]) => {
    if (files.length === 0) return

    const file = files[0] // Un seul fichier à la fois
    const validationError = validateFile(file)

    if (validationError) {
      toast.error(validationError)
      return
    }

    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/v1/upload/upload', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Erreur lors de l\'upload')
      }

      const data = await response.json()
      const newTask: UploadTask = {
        task_id: data.task_id,
        status: 'processing',
        filename: data.filename,
        file_size: file.size,
        progress: 0,
        current_step: 'upload',
        metadata: {}
      }

      setUploadTasks(prev => [...prev, newTask])
      toast.success('Upload démarré !')

      // Démarrer le monitoring du statut
      monitorUploadStatus(data.task_id)

    } catch (error) {
      console.error('Erreur upload:', error)
      toast.error(error instanceof Error ? error.message : 'Erreur lors de l\'upload')
    } finally {
      setIsUploading(false)
    }
  }

  // Monitoring du statut d'upload
  const monitorUploadStatus = async (taskId: string) => {
    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/v1/upload/upload/status/${taskId}`, {
          credentials: 'include'
        })

        if (!response.ok) {
          throw new Error('Erreur récupération statut')
        }

        const statusData = await response.json()

        setUploadTasks(prev => prev.map(task =>
          task.task_id === taskId
            ? { ...task, ...statusData }
            : task
        ))

        // Continuer le monitoring si en cours
        if (statusData.status === 'processing') {
          setTimeout(pollStatus, 2000) // Poll toutes les 2 secondes
        } else if (statusData.status === 'completed') {
          toast.success('Upload terminé avec succès !')
          if (onUploadComplete) {
            onUploadComplete(statusData)
          }
        } else if (statusData.status === 'failed') {
          toast.error(`Upload échoué: ${statusData.error_message || 'Erreur inconnue'}`)
        }

      } catch (error) {
        console.error('Erreur monitoring:', error)
        toast.error('Erreur lors de la surveillance de l\'upload')
      }
    }

    // Démarrer le monitoring
    pollStatus()
  }

  // Gestionnaire d'annulation
  const handleCancelUpload = async (taskId: string) => {
    try {
      const response = await fetch(`/api/v1/upload/upload/${taskId}`, {
        method: 'DELETE',
        credentials: 'include'
      })

      if (response.ok) {
        setUploadTasks(prev => prev.filter(task => task.task_id !== taskId))
        toast.success('Upload annulé')
      } else {
        throw new Error('Erreur lors de l\'annulation')
      }
    } catch (error) {
      toast.error('Impossible d\'annuler l\'upload')
    }
  }

  // Gestionnaire de retry
  const handleRetryUpload = async (taskId: string) => {
    try {
      const response = await fetch(`/api/v1/upload/upload/${taskId}/retry`, {
        method: 'POST',
        credentials: 'include'
      })

      if (response.ok) {
        // Remettre le statut à processing
        setUploadTasks(prev => prev.map(task =>
          task.task_id === taskId
            ? { ...task, status: 'processing', progress: 0, current_step: 'retry' }
            : task
        ))
        toast.success('Relance démarrée')
        monitorUploadStatus(taskId)
      } else {
        throw new Error('Erreur lors de la relance')
      }
    } catch (error) {
      toast.error('Impossible de relancer l\'upload')
    }
  }

  // Configuration react-dropzone
  const onDrop = useCallback((acceptedFiles: File[]) => {
    handleUpload(acceptedFiles)
  }, [])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: acceptedFormats,
    multiple: false,
    disabled: isUploading
  })

  // Formatage de la taille de fichier
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  // Formatage de la durée
  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  // Couleur du statut
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600'
      case 'failed': return 'text-red-600'
      case 'cancelled': return 'text-gray-600'
      case 'processing': return 'text-blue-600'
      default: return 'text-gray-600'
    }
  }

  // Icône du statut
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'failed': return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'cancelled': return <X className="w-5 h-5 text-gray-600" />
      case 'processing': return <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      default: return <Upload className="w-5 h-5 text-gray-600" />
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      {/* Zone de dépôt */}
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
            : isDragReject
            ? 'border-red-400 bg-red-50 dark:bg-red-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-400'
        } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} ref={fileInputRef} />

        <div className="flex flex-col items-center space-y-4">
          <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
            <Upload className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {isDragActive
                ? 'Déposez votre archive ici'
                : 'Téléversez votre audiobook'
              }
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Glissez-déposez une archive ZIP ou RAR, ou cliquez pour sélectionner
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500">
              Formats supportés: ZIP, RAR, 7Z, TAR • Taille max: {maxFileSize}MB
            </p>
          </div>

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Choisir un fichier
          </button>
        </div>
      </div>

      {/* Liste des tâches d'upload */}
      {uploadTasks.length > 0 && (
        <div className="mt-6 space-y-4">
          <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
            Tâches d'upload ({uploadTasks.length})
          </h4>

          {uploadTasks.map((task) => (
            <div key={task.task_id} className="border rounded-lg p-4 bg-white dark:bg-gray-800 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(task.status)}
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {task.filename}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {formatFileSize(task.file_size)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-medium ${getStatusColor(task.status)}`}>
                    {task.status === 'processing' && task.current_step
                      ? `Traitement: ${task.current_step}`
                      : task.status.charAt(0).toUpperCase() + task.status.slice(1)
                    }
                  </span>

                  {(task.status === 'failed' || task.status === 'cancelled') && (
                    <button
                      onClick={() => handleRetryUpload(task.task_id)}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                    >
                      Relancer
                    </button>
                  )}

                  {task.status === 'processing' && (
                    <button
                      onClick={() => handleCancelUpload(task.task_id)}
                      className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                    >
                      Annuler
                    </button>
                  )}
                </div>
              </div>

              {/* Barre de progression */}
              {task.status === 'processing' && (
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-3">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.max(task.progress, 5)}%` }}
                  />
                </div>
              )}

              {/* Métadonnées extraites */}
              {task.metadata && (
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {task.metadata.title && (
                    <div>
                      <span className="font-medium text-gray-600 dark:text-gray-400">Titre:</span>
                      <span className="ml-2 text-gray-900 dark:text-white">{task.metadata.title}</span>
                    </div>
                  )}
                  {task.metadata.artist && (
                    <div>
                      <span className="font-medium text-gray-600 dark:text-gray-400">Artiste:</span>
                      <span className="ml-2 text-gray-900 dark:text-white">{task.metadata.artist}</span>
                    </div>
                  )}
                  {task.metadata.album && (
                    <div>
                      <span className="font-medium text-gray-600 dark:text-gray-400">Album:</span>
                      <span className="ml-2 text-gray-900 dark:text-white">{task.metadata.album}</span>
                    </div>
                  )}
                  {task.metadata.duration && (
                    <div>
                      <span className="font-medium text-gray-600 dark:text-gray-400">Durée:</span>
                      <span className="ml-2 text-gray-900 dark:text-white">
                        {formatDuration(task.metadata.duration)}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Message d'erreur */}
              {task.error_message && (
                <div className="mt-3 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
                  <p className="text-sm text-red-600 dark:text-red-400">
                    <AlertCircle className="w-4 h-4 inline mr-2" />
                    {task.error_message}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AudiobookUploader