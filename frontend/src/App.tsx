import React, { Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/contexts/AuthContext'
import { AudioPlayerProvider, useAudioPlayer } from '@/contexts/AudioPlayerContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import useWebVitals from '@/hooks/useWebVitals'
import Layout from '@/components/Layout'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import './styles/index.css'

// Lazy load components with loading fallbacks
const AudioPlayer = React.lazy(() => import('@/components/AudioPlayer'))
const Dashboard = React.lazy(() => import('@/pages/Dashboard'))
const Instances = React.lazy(() => import('@/pages/Instances'))
const Sync = React.lazy(() => import('@/pages/Sync'))
const Login = React.lazy(() => import('@/pages/Login'))
const Upload = React.lazy(() => import('@/pages/Upload'))
const AdminDashboard = React.lazy(() => import('@/pages/AdminDashboard'))
const Search = React.lazy(() => import('@/pages/Search'))

// Loading component optimized for mobile
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[200px] sm:min-h-[400px]">
    <div className="animate-spin rounded-full h-8 w-8 sm:h-12 sm:w-12 border-b-2 border-indigo-600"></div>
    <span className="sr-only">Chargement...</span>
  </div>
)

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function AppContent() {
  const { tracks, currentTrackIndex, setCurrentTrackIndex, isMinimized, toggleMinimize } = useAudioPlayer()

  // Performance monitoring for mobile
  useWebVitals()

  return (
    <>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              <Route index element={<Dashboard />} />
              <Route path="search" element={<Search />} />
              <Route path="instances" element={<Instances />} />
              <Route path="sync" element={<Sync />} />
              <Route path="upload" element={<Upload />} />
              <Route path="admin" element={<AdminDashboard />} />
            </Route>
          </Routes>
        </Suspense>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'var(--toast-bg, #363636)',
              color: 'var(--toast-color, #fff)',
            },
          }}
        />
      </div>

      {/* Lecteur audio */}
      {tracks.length > 0 && (
        <Suspense fallback={
          <div className="fixed bottom-4 right-4 bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg flex items-center space-x-2">
            <div className="animate-pulse w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <span className="sr-only">Chargement lecteur audio...</span>
          </div>
        }>
          <AudioPlayer
            tracks={tracks}
            currentTrackIndex={currentTrackIndex}
            onTrackChange={setCurrentTrackIndex}
            isMinimized={isMinimized}
            onToggleMinimize={toggleMinimize}
          />
        </Suspense>
      )}
    </>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <AudioPlayerProvider>
            <Router>
              <AppContent />
            </Router>
          </AudioPlayerProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App