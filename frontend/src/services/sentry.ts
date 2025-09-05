import * as Sentry from '@sentry/react'

// @ts-ignore
const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN
// @ts-ignore
const ENVIRONMENT = import.meta.env.VITE_ENVIRONMENT || 'development'

// Configuration Sentry
export const initSentry = () => {
  if (!SENTRY_DSN) {
    console.warn('Sentry DSN non configuré, monitoring désactivé')
    return
  }

  Sentry.init({
    dsn: SENTRY_DSN,
    environment: ENVIRONMENT,
    // Performance Monitoring basique
    tracesSampleRate: ENVIRONMENT === 'production' ? 0.1 : 1.0,

    // Configuration des erreurs
    beforeSend(event, hint) {
      // Filtrer les erreurs non critiques
      const error = hint.originalException as Error
      if (error instanceof Error) {
        // Ignorer les erreurs de réseau courantes
        if (error.message.includes('Failed to fetch') ||
            error.message.includes('NetworkError')) {
          return null
        }
      }
      return event
    },
  })
}

// Service de monitoring simplifié
export const monitoringService = {
  // Tracking des erreurs utilisateur
  trackError: (error: Error, context?: Record<string, any>) => {
    Sentry.captureException(error, {
      tags: context,
    })
  },

  // Tracking des performances de base
  trackPerformance: (name: string, startTime: number) => {
    const duration = Date.now() - startTime
    // Log des performances lentes (>1s)
    if (duration > 1000) {
      console.warn(`Performance: ${name} took ${duration}ms`)
      Sentry.captureMessage(`Slow performance: ${name}`, 'warning')
    }
  },

  // Tracking de l'utilisation des fonctionnalités
  trackFeatureUsage: (feature: string, _userId?: string) => {
    Sentry.captureMessage(`Feature used: ${feature}`, 'info')
  },
}

export default Sentry