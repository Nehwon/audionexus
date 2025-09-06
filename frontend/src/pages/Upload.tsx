import React from 'react'
import AudiobookUploader from '@/components/AudiobookUploader'

const Upload: React.FC = () => {
  const handleUploadComplete = (task: any) => {
    console.log('Upload terminé:', task)
    // TODO: Intégrer avec la gestion des audiobooks existants
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Téléverser un Audiobook
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Téléversez une archive contenant vos fichiers audio. Le système extrait automatiquement
            les métadonnées et convertit vers le format M4B optimisé.
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6">
            <AudiobookUploader
              onUploadComplete={handleUploadComplete}
              maxFileSize={500}
            />
          </div>
        </div>

        {/* Informations sur les formats supportés */}
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
            Formats supportés
          </h3>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">
                Formats d'archive
              </h4>
              <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                <li>• ZIP (.zip)</li>
                <li>• RAR (.rar)</li>
                <li>• 7-Zip (.7z)</li>
                <li>• TAR (.tar.gz, .tar.bz2)</li>
              </ul>
            </div>

            <div>
              <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">
                Formats audio
              </h4>
              <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                <li>• MP3</li>
                <li>• M4A, M4B</li>
                <li>• AAC</li>
                <li>• FLAC</li>
                <li>• OGG</li>
                <li>• WMA</li>
                <li>• WAV</li>
              </ul>
            </div>
          </div>

          <div className="mt-4 p-3 bg-blue-100 dark:bg-blue-800/30 rounded">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              <strong>Note:</strong> Les fichiers seront automatiquement convertis vers le format M4B
              avec optimisation pour la lecture sur appareils mobiles.
            </p>
          </div>
        </div>

        {/* Fonctionnalités */}
        <div className="mt-8 grid md:grid-cols-3 gap-6">
          <div className="text-center p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900 mx-auto rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Extraction automatique
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Décompression automatique des archives et organisation des fichiers audio.
            </p>
          </div>

          <div className="text-center p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 mx-auto rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Métadonnées ID3
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Extraction et correction automatique des métadonnées des fichiers audio.
            </p>
          </div>

          <div className="text-center p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 mx-auto rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Format optimisé
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Conversion vers M4B avec optimisation pour la lecture et réduction de poids.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Upload