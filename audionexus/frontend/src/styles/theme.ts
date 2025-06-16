import { extendTheme, type ThemeConfig, type ThemeOverride } from '@chakra-ui/react';

// Configuration du mode sombre/clair
const config: ThemeConfig = {
  initialColorMode: 'light',
  useSystemColorMode: true,
};

// Couleurs personnalisées
const colors = {
  brand: {
    50: '#e6f7ff',
    100: '#b3e0ff',
    200: '#80c9ff',
    300: '#4db3ff',
    400: '#1a9cff',
    500: '#0080ff', // Couleur principale
    600: '#0066cc',
    700: '#004d99',
    800: '#003366',
    900: '#001a33',
  },
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
};

// Styles globaux
const styles = {
  global: (props: { colorMode: string }) => ({
    'html, body': {
      bg: props.colorMode === 'dark' ? 'gray.900' : 'gray.50',
      color: props.colorMode === 'dark' ? 'whiteAlpha.900' : 'gray.800',
      lineHeight: 'tall',
    },
    a: {
      color: props.colorMode === 'dark' ? 'teal.300' : 'teal.500',
      _hover: {
        textDecoration: 'underline',
      },
    },
  }),
};

// Configuration des composants
const components = {
  Button: {
    baseStyle: {
      fontWeight: 'semibold',
      borderRadius: 'md',
    },
    defaultProps: {
      colorScheme: 'brand',
    },
  },
  Input: {
    defaultProps: {
      focusBorderColor: 'brand.500',
    },
  },
  Textarea: {
    defaultProps: {
      focusBorderColor: 'brand.500',
    },
  },
  Select: {
    defaultProps: {
      focusBorderColor: 'brand.500',
    },
  },
};

// Création du thème étendu
const theme = extendTheme({
  config,
  colors,
  styles,
  components,
  // Ajoutez d'autres personnalisations ici
} as ThemeOverride);

export default theme;
