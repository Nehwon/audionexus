import React, { createContext, useContext, useState, ReactNode } from 'react'

interface Track {
  id: string
  title: string
  artist: string
  duration: number
  url: string
}

interface AudioPlayerContextType {
  tracks: Track[]
  currentTrackIndex: number
  isMinimized: boolean
  setTracks: (tracks: Track[]) => void
  setCurrentTrackIndex: (index: number) => void
  toggleMinimize: () => void
  addTrack: (track: Track) => void
  removeTrack: (id: string) => void
  playTrackById: (id: string) => void
}

const AudioPlayerContext = createContext<AudioPlayerContextType | undefined>(undefined)

export const useAudioPlayer = () => {
  const context = useContext(AudioPlayerContext)
  if (!context) {
    throw new Error('useAudioPlayer must be used within an AudioPlayerProvider')
  }
  return context
}

interface AudioPlayerProviderProps {
  children: ReactNode
}

export const AudioPlayerProvider: React.FC<AudioPlayerProviderProps> = ({ children }) => {
  const [tracks, setTracksState] = useState<Track[]>([])
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0)
  const [isMinimized, setIsMinimized] = useState(false)

  const setTracks = (newTracks: Track[]) => {
    setTracksState(newTracks)
    setCurrentTrackIndex(0)
  }

  const addTrack = (track: Track) => {
    setTracksState(prev => {
      const exists = prev.find(t => t.id === track.id)
      if (exists) return prev
      return [...prev, track]
    })
  }

  const removeTrack = (id: string) => {
    setTracksState(prev => {
      const newTracks = prev.filter(t => t.id !== id)
      // Adjust current index if necessary
      if (currentTrackIndex >= newTracks.length && newTracks.length > 0) {
        setCurrentTrackIndex(newTracks.length - 1)
      }
      return newTracks
    })
  }

  const playTrackById = (id: string) => {
    const index = tracks.findIndex(t => t.id === id)
    if (index !== -1) {
      setCurrentTrackIndex(index)
    }
  }

  const toggleMinimize = () => {
    setIsMinimized(prev => !prev)
  }

  const value: AudioPlayerContextType = {
    tracks,
    currentTrackIndex,
    isMinimized,
    setTracks,
    setCurrentTrackIndex,
    toggleMinimize,
    addTrack,
    removeTrack,
    playTrackById,
  }

  return (
    <AudioPlayerContext.Provider value={value}>
      {children}
    </AudioPlayerContext.Provider>
  )
}