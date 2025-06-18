import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
  redirectTo?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles = [],
  redirectTo = '/login',
}) => {
  const { isAuthenticated, user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    // Afficher un indicateur de chargement pendant la vérification de l'authentification
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Si l'utilisateur n'est pas authentifié, rediriger vers la page de connexion
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // Vérifier les rôles si nécessaire
  if (requiredRoles.length > 0) {
    const hasRequiredRole = requiredRoles.some(role => {
      // Ici, vous pouvez implémenter votre propre logique de vérification de rôle
      // Par exemple, vérifier si l'utilisateur a le rôle requis
      return user?.is_superuser; // Exemple simple
    });

    if (!hasRequiredRole) {
      // Rediriger vers une page d'erreur ou une page d'accueil
      return <Navigate to="/unauthorized" state={{ from: location }} replace />;
    }
  }

  // Si l'utilisateur est authentifié et a les rôles requis, afficher les enfants
  return <>{children}</>;
};

export default ProtectedRoute;
