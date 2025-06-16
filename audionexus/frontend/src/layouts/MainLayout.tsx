import { Box, Container } from '@chakra-ui/react';
import { type FC, type ReactNode } from 'react';
import Navbar from '../components/Navbar.tsx';

interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout: FC<MainLayoutProps> = ({ children }) => {
  return (
    <Box minH="100vh" display="flex" flexDirection="column">
      <Navbar />
      <Container maxW="container.xl" flex={1} py={8}>
        {children}
      </Container>
      {/* Footer pourrait être ajouté ici */}
    </Box>
  );
};

export default MainLayout;
