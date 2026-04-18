import { useEffect } from 'react'
import { monitoringService } from '@/services/sentry'

type WebVitalsMetric = {
  name: string
  value: number | string
  id: string
}

export const useWebVitals = () => {
  useEffect(() => {
    // Fonction utilitaire pour mesurer les Core Web Vitals
    const reportWebVitals = (metric: WebVitalsMetric) => {
      // Conversion en millisecondes pour CLS (qui est en décimales)
      const value = metric.name === 'CLS' ? metric.value * 1000 : metric.value

      // Logging des métriques
      console.log(`${metric.name}:`, value)

      // Tracking avec Sentry
      monitoringService.trackPerformance(`web_vitals_${metric.name}`, Date.now() - value)
    }

    // Mesure FCP (First Contentful Paint)
    const measureFCP = () => {
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.name === 'first-contentful-paint') {
            reportWebVitals({
              name: 'FCP',
              value: entry.startTime,
              id: 'fcp'
            })
          }
        }
      }).observe({ entryTypes: ['paint'] })
    }

    // Mesure LCP (Largest Contentful Paint)
    const measureLCP = () => {
      new PerformanceObserver((list) => {
        let maxLCP = 0
        for (const entry of list.getEntries()) {
          if (entry.startTime > maxLCP) {
            maxLCP = entry.startTime
          }
        }
        if (maxLCP > 0) {
          reportWebVitals({
            name: 'LCP',
            value: maxLCP,
            id: 'lcp'
          })
        }
      }).observe({ entryTypes: ['largest-contentful-paint'] })
    }

    // Mesure CLS (Cumulative Layout Shift)
    const measureCLS = () => {
      let clsValue = 0
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value
          }
        }
        // Rapport final quand la page devient cachée
        if (document.visibilityState === 'hidden') {
          reportWebVitals({
            name: 'CLS',
            value: clsValue,
            id: 'cls'
          })
        }
      }).observe({ entryTypes: ['layout-shift'] })
    }

    // Mesure FID (First Input Delay)
    const measureFID = () => {
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          reportWebVitals({
            name: 'FID',
            value: (entry as any).processingStart - entry.startTime,
            id: 'fid'
          })
        }
      }).observe({ entryTypes: ['first-input'] })
    }

    // Mesurer TTFB (Time to First Byte)
    const measureTTFB = () => {
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          reportWebVitals({
            name: 'TTFB',
            value: (entry as any).responseStart - (entry as any).requestStart,
            id: 'ttfb'
          })
        }
      }).observe({ entryTypes: ['navigation'] })
    }

    // Informations de réseau et device mobile
    const measureMobileInfo = () => {
      if ('connection' in navigator) {
        const connection = (navigator as any).connection
        if (connection) {
          reportWebVitals({
            name: 'Network_Type',
            value: connection.effectiveType,
            id: 'network-type'
          })
          reportWebVitals({
            name: 'Network_Speed',
            value: connection.downlink,
            id: 'network-speed'
          })
        }
      }

      // Battery API si disponible
      if ('getBattery' in navigator) {
        (navigator as any).getBattery().then((battery: any) => {
          reportWebVitals({
            name: 'Battery_Level',
            value: Math.round(battery.level * 100),
            id: 'battery-level'
          })
        })
      }
    }

    // Démarrer toutes les mesures
    measureFCP()
    measureLCP()
    measureCLS()
    measureFID()
    measureTTFB()
    measureMobileInfo()

    // Cleanup
    return () => {
      // Les observers se nettoient automatiquement quand le composant est démonté
    }
  }, [])
}

export default useWebVitals