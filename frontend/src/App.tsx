import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/contexts/AuthContext'
import { AudioPlayerProvider, useAudioPlayer } from '@/contexts/AudioPlayerContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import AudioPlayer from '@/components/AudioPlayer'
import Layout from '@/components/Layout'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import Dashboard from '@/pages/Dashboard'
import Instances from '@/pages/Instances'
import Sync from '@/pages/Sync'
import Login from '@/pages/Login'
import Upload from '@/pages/Upload'
import './styles/index.css'

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

  return (
    <>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Dashboard />} />
            <Route path="instances" element={<Instances />} />
            <Route path="sync" element={<Sync />} />
            <Route path="upload" element={<Upload />} />
          </Route>
        </Routes>
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
        <AudioPlayer
          tracks={tracks}
          currentTrackIndex={currentTrackIndex}
          onTrackChange={setCurrentTrackIndex}
          isMinimized={isMinimized}
          onToggleMinimize={toggleMinimize}
        />
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