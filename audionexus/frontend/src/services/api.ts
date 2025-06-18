import axios, { type AxiosInstance, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';
import { getToken, clearToken, setToken } from '@/utils/auth';

// Configuration de base de l'API
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Création d'une instance Axios avec la configuration de base
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token JWT aux requêtes
export const setupInterceptors = (): void => {
  api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Gestion des erreurs 401 (non autorisé)
  api.interceptors.response.use(
    (response: AxiosResponse) => response,
    async (error) => {
      const originalRequest = error.config;
      
      // Si l'erreur est 401 et que ce n'est pas une tentative de rafraîchissement
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        
        try {
          // Essayer de rafraîchir le token
          const refreshToken = localStorage.getItem('refreshToken');
          if (refreshToken) {
            const response = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refreshToken });
            const { access_token, refresh_token } = response.data;
            
            // Mettre à jour les tokens
            setToken(access_token, refresh_token);
            
            // Répéter la requête originale avec le nouveau token
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return api(originalRequest);
          }
        } catch (error) {
          // En cas d'échec de rafraîchissement, déconnecter l'utilisateur
          clearToken();
          window.location.href = '/login';
        }
      }
      
      return Promise.reject(error);
    }
  );
};

// Méthodes pour l'authentification
export const authService = {
  // Connexion
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Stocker le token et le refresh token
    if (response.data.access_token && response.data.refresh_token) {
      setToken(response.data.access_token, response.data.refresh_token);
    }
    
    return response.data;
  },
  
  // Inscription
  register: async (email: string, password: string, fullName: string) => {
    return api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
  },
  
  // Récupérer les informations de l'utilisateur connecté
  getMe: async () => {
    return api.get('/auth/me');
  },
  
  // Déconnexion
  logout: () => {
    clearToken();
    // Rediriger vers la page de connexion
    window.location.href = '/login';
  },
};

export default api;
