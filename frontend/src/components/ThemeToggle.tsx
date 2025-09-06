import React from 'react'
import { Sun, Moon, Monitor } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

const ThemeToggle: React.FC = () => {
  const { theme, setTheme } = useTheme()

  const themes = [
    { value: 'light' as const, label: 'Clair', icon: Sun, ariaLabel: 'Basculer vers le thème clair' },
    { value: 'dark' as const, label: 'Sombre', icon: Moon, ariaLabel: 'Basculer vers le thème sombre' },
    { value: 'system' as const, label: 'Système', icon: Monitor, ariaLabel: 'Utiliser le thème système' },
  ]

  return (
    <div className="flex items-center space-x-1 border border-gray-200 dark:border-gray-700 rounded-md p-1 bg-white dark:bg-gray-800">
      {themes.map(({ value, label, icon: Icon, ariaLabel }) => (
        <button
          key={value}
          onClick={() => setTheme(value)}
          className={`flex items-center justify-center w-8 h-8 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 ${
            theme === value
              ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300'
              : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
          }`}
          aria-label={ariaLabel}
          aria-pressed={theme === value}
        >
          <Icon size={16} />
          <span className="sr-only">{label}</span>
        </button>
      ))}
    </div>
  )
}

export default ThemeToggle