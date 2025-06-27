// Configuration pour les tests avec Vitest et Testing Library
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

// Nettoyage après chaque test
// Cela garantit que chaque test est isolé et ne laisse pas d'effets de bord
afterEach(() => {
  cleanup();
});

// Configuration globale pour les tests
// Ici, vous pouvez ajouter des configurations supplémentaires si nécessaire
