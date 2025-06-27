import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ChakraProvider } from '@chakra-ui/react';
import LoginPage from '../LoginPage';

import { vi, describe, it, expect, beforeEach } from 'vitest';

// Mock de useAuth
const mockLogin = vi.fn();

// Mock du contexte d'authentification
vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    login: mockLogin,
    isAuthenticated: false,
    isLoading: false,
  }),
}));

// Mock de requireGuest pour éviter les redirections
vi.mock('../../utils/auth', () => ({
  requireGuest: vi.fn(),
}));

describe('LoginPage', () => {
  const renderLoginPage = () => {
    return render(
      <ChakraProvider>
        <BrowserRouter>
          <LoginPage />
        </BrowserRouter>
      </ChakraProvider>
    );
  };

  beforeEach(() => {
    // Réinitialiser les mocks avant chaque test
    vi.clearAllMocks();
  });

  it('affiche le formulaire de connexion', () => {
    renderLoginPage();
    
    // Vérifier que le titre est affiché (le texte est dans un composant Text, pas un heading)
    expect(screen.getByText(/connectez-vous à votre compte/i)).toBeInTheDocument();
    
    // Vérifier que les champs du formulaire sont présents
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/mot de passe/i)).toBeInTheDocument();
    
    // Vérifier que le bouton de connexion est présent (le texte peut être en majuscules)
    expect(screen.getByRole('button', { name: /se connecter/i })).toBeInTheDocument();
  });

  it('affiche un lien vers la page d\'inscription', () => {
    renderLoginPage();
    
    // Vérifier que le lien d'inscription est présent
    const signupLink = screen.getByRole('link', { name: /s'inscrire/i });
    expect(signupLink).toBeInTheDocument();
    expect(signupLink).toHaveAttribute('href', '/register');
  });
});
