import type { FC, ReactNode } from 'react';
import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';
import theme from '../styles/theme';

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: FC<ThemeProviderProps> = ({ children }) => {
  return (
    <>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <ChakraProvider theme={theme}>
        {children}
      </ChakraProvider>
    </>
  );
};

export default ThemeProvider;
