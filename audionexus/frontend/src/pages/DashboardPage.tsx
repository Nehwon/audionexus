import { Box, Heading, Text, VStack } from '@chakra-ui/react';
import { useAuth } from '../context/AuthContext';

const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading as="h1" size="xl" mb={2}>
            Tableau de bord
          </Heading>
          <Text color="gray.600">
            Bienvenue, {user?.email}
          </Text>
        </Box>

        <Box
          p={6}
          bg="white"
          borderRadius="lg"
          boxShadow="sm"
          borderWidth="1px"
        >
          <Heading as="h2" size="lg" mb={4}>
            Vue d'ensemble
          </Heading>
          <Text>Contenu du tableau de bord à venir...</Text>
        </Box>
      </VStack>
    </Box>
  );
};

export default DashboardPage;
