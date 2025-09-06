import React, { useState, useRef, useEffect } from 'react'
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX } from 'lucide-react'

interface Track {
  id: string
  title: string
  artist: string
  duration: number
  url: string
}

interface AudioPlayerProps {
  tracks: Track[]
  currentTrackIndex: number
  onTrackChange: (index: number) => void
  isMinimized?: boolean
  onToggleMinimize?: () => void
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({
  tracks,
  currentTrackIndex,
  onTrackChange,
  isMinimized = false,
  onToggleMinimize
}) => {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)

  const currentTrack = tracks[currentTrackIndex]

  useEffect(() => {
    const audio = audioRef.current
    if (!audio || !currentTrack) return

    audio.src = currentTrack.url
    audio.load()
  }, [currentTrack])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setDuration(audio.duration || 0)

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('ended', handleNext)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('ended', handleNext)
    }
  }, [currentTrackIndex])

  const togglePlay = async () => {
    const audio = audioRef.current
    if (!audio) return

    try {
      if (isPlaying) {
        audio.pause()
        setIsPlaying(false)
      } else {
        await audio.play()
        setIsPlaying(true)
      }
    } catch (error) {
      console.error('Erreur lors de la lecture:', error)
    }
  }

  const handlePrevious = () => {
    const newIndex = currentTrackIndex > 0 ? currentTrackIndex - 1 : tracks.length - 1
    onTrackChange(newIndex)
  }

  const handleNext = () => {
    const newIndex = currentTrackIndex < tracks.length - 1 ? currentTrackIndex + 1 : 0
    onTrackChange(newIndex)
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current
    if (!audio) return

    const time = parseFloat(e.target.value)
    audio.currentTime = time
    setCurrentTime(time)
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value)
    setVolume(newVolume)

    const audio = audioRef.current
    if (audio) {
      audio.volume = newVolume
    }

    if (newVolume > 0 && isMuted) {
      setIsMuted(false)
    }
  }

  const toggleMute = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isMuted) {
      audio.volume = volume
      setIsMuted(false)
    } else {
      audio.volume = 0
      setIsMuted(true)
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  if (!currentTrack) {
    return null
  }

  return (
    <div className={`fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg transition-all duration-300 z-50 ${
      isMinimized ? 'h-16' : 'h-24'
    }`}>
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center space-x-4">
        <audio ref={audioRef} />

        {/* Informations de la piste */}
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center">
            <span className="text-gray-500 text-xs">♪</span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium truncate">{currentTrack.title}</div>
            <div className="text-xs text-gray-500 truncate">{currentTrack.artist}</div>
          </div>
        </div>

        {/* Contrôles principaux */}
        <div className="flex flex-col items-center space-y-2 flex-1">
          <div className="flex items-center space-x-4">
            <button
              onClick={handlePrevious}
              className="p-2 text-gray-600 hover:text-gray-900"
            >
              <SkipBack size={20} />
            </button>
            <button
              onClick={togglePlay}
              className="p-3 bg-indigo-600 text-white rounded-full hover:bg-indigo-700"
            >
              {isPlaying ? <Pause size={20} /> : <Play size={20} />}
            </button>
            <button
              onClick={handleNext}
              className="p-2 text-gray-600 hover:text-gray-900"
            >
              <SkipForward size={20} />
            </button>
          </div>

          {/* Barre de progression */}
          {!isMinimized && (
            <div className="flex items-center space-x-2 w-full max-w-md">
              <span className="text-xs text-gray-500 w-10 text-right">
                {formatTime(currentTime)}
              </span>
              <input
                type="range"
                min="0"
                max={duration || 0}
                value={currentTime}
                onChange={handleSeek}
                className="flex-1 h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-xs text-gray-500 w-10">
                {formatTime(duration)}
              </span>
            </div>
          )}
        </div>

        {/* Contrôles volume */}
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleMute}
            className="p-2 text-gray-600 hover:text-gray-900"
          >
            {isMuted || volume === 0 ? <VolumeX size={20} /> : <Volume2 size={20} />}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
            className="w-20 h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Bouton de minimisation */}
        {onToggleMinimize && (
          <button
            onClick={onToggleMinimize}
            className="p-2 text-gray-600 hover:text-gray-900"
          >
            <span className="text-xs">{isMinimized ? '▲' : '▼'}</span>
          </button>
        )}
      </div>

      {/* Playlist minimisée */}
      {isMinimized && tracks.length > 1 && (
        <div className="absolute bottom-16 left-4 right-4 bg-white border rounded-lg shadow-lg p-2 max-h-48 overflow-y-auto">
          <div className="text-xs font-medium text-gray-700 mb-2">
            Playlist ({tracks.length} pistes)
          </div>
          {tracks.map((track, index) => (
            <button
              key={track.id}
              onClick={() => onTrackChange(index)}
              className={`w-full text-left px-2 py-1 text-xs rounded ${
                index === currentTrackIndex
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'hover:bg-gray-100'
              }`}
            >
              <div className="truncate">{track.title}</div>
              <div className="text-gray-500 truncate">{track.artist}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default AudioPlayer