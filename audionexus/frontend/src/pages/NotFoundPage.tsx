import { Box, Button, Heading, Text, VStack } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <Box textAlign="center" py={10} px={6} minH="100vh" display="flex" flexDirection="column" justifyContent="center" alignItems="center">
      <VStack spacing={6}>
        <Box>
          <Heading
            display="inline-block"
            as="h1"
            size="4xl"
            bgGradient="linear(to-r, blue.400, blue.600)"
            backgroundClip="text"
          >
            404
          </Heading>
          <Text fontSize="18px" mt={3} mb={2}>
            Page non trouvée
          </Text>
          <Text color={'gray.500'} mb={6}>
            La page que vous recherchez semble ne pas exister.
          </Text>
        </Box>
        
        <Button
          colorScheme="blue"
          bgGradient="linear(to-r, blue.400, blue.500, blue.600)"
          color="white"
          variant="solid"
          onClick={() => navigate('/')}
          _hover={{
            bgGradient: 'linear(to-r, blue.500, blue.600, blue.700)',
          }}
        >
          Retour à l'accueil
        </Button>
      </VStack>
    </Box>
  );
};

export default NotFoundPage;
