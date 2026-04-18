import React, { useState } from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import ThemeToggle from './ThemeToggle'
import SkipToContent from './SkipToContent'
import { Menu, X } from 'lucide-react'

const Layout: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen)
  }

  if (!isAuthenticated) {
    return <Outlet />
  }

  return (
    <>
      <SkipToContent />
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50" role="banner">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              {/* Mobile menu button */}
              <button
                onClick={toggleMobileMenu}
                className="md:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 mr-3 min-h-[44px] min-w-[44px] flex items-center justify-center"
                aria-expanded={mobileMenuOpen}
                aria-label={mobileMenuOpen ? "Fermer le menu de navigation" : "Ouvrir le menu de navigation"}
                aria-controls="mobile-menu"
              >
                <span className="sr-only">
                  {mobileMenuOpen ? "Fermer le menu" : "Ouvrir le menu"}
                </span>
                {mobileMenuOpen ? (
                  <X className="h-6 w-6" aria-hidden="true" />
                ) : (
                  <Menu className="h-6 w-6" aria-hidden="true" />
                )}
              </button>

              <Link
                to="/"
                className="text-xl font-semibold text-gray-900 dark:text-gray-100 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded min-h-[44px] flex items-center"
                aria-label="Aller à la page d'accueil AudioNexus"
              >
                AudioNexus
              </Link>
            </div>

            {/* Desktop navigation */}
            <nav className="hidden md:flex items-center space-x-4" role="navigation" aria-label="Navigation principale">
              <span className="text-sm text-gray-700 dark:text-gray-300" aria-live="polite">
                Bonjour, {user?.username}
              </span>
              <ThemeToggle />
              <button
                onClick={handleLogout}
                className="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:ring-offset-2 dark:focus:ring-offset-gray-800 min-h-[44px] min-w-[44px]"
                aria-label="Se déconnecter de l'application"
              >
                Déconnexion
              </button>
            </nav>
          </div>
        </div>

        {/* Mobile menu overlay */}
        {mobileMenuOpen && (
          <div id="mobile-menu" className="md:hidden bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700" role="region" aria-label="Menu de navigation mobile">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              <nav role="navigation" aria-label="Navigation mobile">
                <div className="px-3 py-2 border-t border-gray-200 dark:border-gray-700 mt-3">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300" aria-live="polite">
                    Bonjour, {user?.username}
                  </span>
                </div>
                <div className="px-3 py-2">
                  <ThemeToggle />
                </div>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-3 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-md min-h-[44px]"
                  aria-label="Se déconnecter de l'application"
                >
                  Déconnexion
                </button>
              </nav>
            </div>
          </div>
        )}
      </header>

      <div className="flex">
        {/* Sidebar - Hidden on mobile, visible on md+ */}
        <aside className="hidden md:block w-64 bg-white dark:bg-gray-800 shadow-sm min-h-screen border-r border-gray-200 dark:border-gray-700" role="complementary" aria-label="Navigation secondaire">
          <div className="p-4">
            <nav aria-label="Navigation des pages">
              <ul className="space-y-2" role="list">
                <li role="listitem">
                  <Link
                    to="/"
                    className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-indigo-50 dark:focus:bg-indigo-900 min-h-[44px] flex items-center"
                    aria-label="Accéder au tableau de bord"
                  >
                    Dashboard
                  </Link>
                </li>
                <li role="listitem">
                  <Link
                    to="/upload"
                    className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-indigo-50 dark:focus:bg-indigo-900 min-h-[44px] flex items-center"
                    aria-label="Téléverser des audiobooks"
                  >
                    Téléversement
                  </Link>
                </li>
                <li role="listitem">
                  <Link
                    to="/instances"
                    className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-indigo-50 dark:focus:bg-indigo-900 min-h-[44px] flex items-center"
                    aria-label="Gérer les instances Audiobookshelf"
                  >
                    Instances
                  </Link>
                </li>
                <li role="listitem">
                  <Link
                    to="/sync"
                    className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-indigo-50 dark:focus:bg-indigo-900 min-h-[44px] flex items-center"
                    aria-label="Gérer la synchronisation"
                  >
                    Synchronisation
                  </Link>
                </li>
              </ul>
            </nav>
          </div>
        </aside>

        {/* Main content */}
        <main
          id="main-content"
          className="flex-1 p-4 md:p-6 bg-gray-50 dark:bg-gray-900 min-h-screen"
          role="main"
          aria-label="Contenu principal"
        >
          <Outlet />
        </main>
      </div>
    </div>
    </>
  )
}

export default Layout