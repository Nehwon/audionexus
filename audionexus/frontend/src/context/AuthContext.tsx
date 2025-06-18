import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authService } from '../services/api';
import { getToken, clearToken as clearLocalToken } from '../utils/auth';

interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Vérifier l'état d'authentification au chargement
  useEffect(() => {
    const checkAuth = async () => {
      const token = getToken();
      if (token) {
        try {
          const response = await authService.getMe();
          setUser(response.data);
        } catch (error) {
          console.error('Erreur de vérification de l\'authentification:', error);
          clearLocalToken();
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await authService.login(email, password);
      const userResponse = await authService.getMe();
      setUser(userResponse.data);
    } catch (error) {
      console.error('Erreur de connexion:', error);
      throw error;
    }
  };

  const register = async (email: string, password: string, fullName: string) => {
    try {
      await authService.register(email, password, fullName);
      // Connecter automatiquement l'utilisateur après l'inscription
      await login(email, password);
    } catch (error) {
      console.error('Erreur d\'inscription:', error);
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {!isLoading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth doit être utilisé à l\'intérieur d\'un AuthProvider');
  }
  return context;
};

export default AuthContext;
