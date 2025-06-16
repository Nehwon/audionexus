import { Box, Heading, Text, Button, VStack } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

const HomePage = () => {
  return (
    <VStack spacing={8} textAlign="center" py={20} px={4}>
      <Heading as="h1" size="2xl" mb={4}>
        Bienvenue sur AudioNexus
      </Heading>
      <Text fontSize="xl" maxW="2xl" color="gray.600" _dark={{ color: 'gray.300' }}>
        Gestionnaire d'audiothèques puissant et intuitif pour gérer plusieurs instances Audiobookshelf
      </Text>
      <Box>
        <Button as={RouterLink} to="/login" colorScheme="brand" size="lg" mr={4}>
          Se connecter
        </Button>
        <Button as={RouterLink} to="/register" variant="outline" size="lg">
          S'inscrire
        </Button>
      </Box>
    </VStack>
  );
};

export default HomePage;
