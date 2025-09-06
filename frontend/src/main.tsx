import React from 'react'
import ReactDOM from 'react-dom/client'
import App from '@/App'
import { initSentry } from '@/services/sentry'
import './styles/index.css'

// Initialiser Sentry
initSentry()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)