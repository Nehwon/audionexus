// Clés de stockage local
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

/**
 * Stocke les tokens d'authentification
 */
export const setToken = (accessToken: string, refreshToken: string): void => {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};

/**
 * Récupère le token d'accès
 */
export const getToken = (): string | null => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

/**
 * Récupère le token de rafraîchissement
 */
export const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

/**
 * Vérifie si l'utilisateur est authentifié
 */
export const isAuthenticated = (): boolean => {
  return !!getToken();
};

/**
 * Supprime les tokens d'authentification
 */
export const clearToken = (): void => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

/**
 * Récupère l'en-tête d'autorisation
 */
export const getAuthHeader = (): { Authorization: string } | {} => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Redirige vers la page de connexion si l'utilisateur n'est pas authentifié
 */
export const requireAuth = (): void => {
  if (!isAuthenticated()) {
    window.location.href = '/login';
  }
};

/**
 * Redirige vers le tableau de bord si l'utilisateur est déjà authentifié
 */
export const requireGuest = (): void => {
  if (isAuthenticated()) {
    window.location.href = '/dashboard';
  }
};
