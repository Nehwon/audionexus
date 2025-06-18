import { useState } from 'react';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  Text,
  useColorModeValue,
  useToast,
  FormErrorMessage,
  Heading,
  Flex,
  VStack,
  Link,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon, LockIcon, EmailIcon } from '@chakra-ui/icons';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useAuth } from '../context/AuthContext';
import { requireGuest } from '../utils/auth';

// Schéma de validation avec Yup
const loginSchema = yup.object().shape({
  email: yup.string().email('Email invalide').required('Email requis'),
  password: yup.string().required('Mot de passe requis'),
});

type LoginFormData = yup.InferType<typeof loginSchema>;

const LoginPage = () => {
  // Rediriger si déjà connecté
  requireGuest();
  
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  // Récupérer l'URL de redirection après connexion
  const from = location.state?.from?.pathname || '/';

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: yupResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      await login(data.email, data.password);
      
      // Afficher un message de succès
      toast({
        title: 'Connexion réussie',
        description: 'Vous êtes maintenant connecté.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      // Rediriger vers la page d'origine ou le tableau de bord
      navigate(from, { replace: true });
    } catch (error) {
      console.error('Erreur de connexion:', error);
      
      // Afficher un message d'erreur
      toast({
        title: 'Erreur de connexion',
        description: 'Email ou mot de passe incorrect',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Flex
      minH="100vh"
      align="center"
      justify="center"
      bg={useColorModeValue('gray.50', 'gray.900')}
      p={4}
    >
      <Box
        w="100%"
        maxW="md"
        p={8}
        borderWidth={1}
        borderRadius={8}
        boxShadow="lg"
        bg={useColorModeValue('white', 'gray.800')}
      >
        <VStack spacing={6} align="stretch">
          <Box textAlign="center">
            <Heading as="h1" size="xl" mb={2}>
              AudioNexus
            </Heading>
            <Text fontSize="lg" color={useColorModeValue('gray.600', 'gray.400')}>
              Connectez-vous à votre compte
            </Text>
          </Box>
          
          <form onSubmit={handleSubmit(onSubmit)}>
            <VStack spacing={4}>
              <FormControl id="email" isInvalid={!!errors.email}>
                <FormLabel>Adresse email</FormLabel>
                <InputGroup>
                  <InputLeftElement pointerEvents="none">
                    <EmailIcon color="gray.300" />
                  </InputLeftElement>
                  <Input
                    type="email"
                    placeholder="votre@email.com"
                    {...register('email')}
                    autoComplete="email"
                  />
                </InputGroup>
                <FormErrorMessage>
                  {errors.email?.message}
                </FormErrorMessage>
              </FormControl>

              <FormControl id="password" isInvalid={!!errors.password}>
                <FormLabel>Mot de passe</FormLabel>
                <InputGroup>
                  <InputLeftElement pointerEvents="none">
                    <LockIcon color="gray.300" />
                  </InputLeftElement>
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    {...register('password')}
                    autoComplete="current-password"
                  />
                  <InputRightElement>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowPassword(!showPassword)}
                      _hover={{ bg: 'transparent' }}
                    >
                      {showPassword ? <ViewOffIcon /> : <ViewIcon />}
                    </Button>
                  </InputRightElement>
                </InputGroup>
                <FormErrorMessage>
                  {errors.password?.message}
                </FormErrorMessage>
              </FormControl>

              <Box w="100%" pt={2} textAlign="right">
                <Link
                  as={RouterLink}
                  to="/forgot-password"
                  color="blue.500"
                  fontSize="sm"
                  _hover={{ textDecoration: 'underline' }}
                >
                  Mot de passe oublié ?
                </Link>
              </Box>

              <Button
                type="submit"
                colorScheme="blue"
                size="lg"
                width="100%"
                mt={4}
                isLoading={isLoading}
                loadingText="Connexion..."
              >
                Se connecter
              </Button>

              <Text textAlign="center" mt={4} fontSize="sm" color="gray.500">
                Vous n'avez pas de compte ?{' '}
                <Link
                  as={RouterLink}
                  to="/register"
                  color="blue.500"
                  fontWeight="medium"
                  _hover={{ textDecoration: 'underline' }}
                >
                  S'inscrire
                </Link>
              </Text>
            </VStack>
          </form>
        </VStack>
      </Box>
    </Flex>
  );
};

export default LoginPage;
