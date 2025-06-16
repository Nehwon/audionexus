import { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputRightElement,
  Stack,
  Text,
  useColorModeValue,
  useToast,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// Schéma de validation avec Yup
const loginSchema = yup.object().shape({
  email: yup.string().email('Email invalide').required('Email requis'),
  password: yup.string().required('Mot de passe requis'),
});

type LoginFormData = yup.InferType<typeof loginSchema>;

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();

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
      // TODO: Implémenter la logique de connexion
      console.log('Login data:', data);
      
      // Simuler une requête API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Rediriger vers le tableau de bord après connexion réussie
      navigate('/dashboard');
      
      toast({
        title: 'Connexion réussie',
        description: 'Vous êtes maintenant connecté.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Erreur de connexion:', error);
      toast({
        title: 'Erreur de connexion',
        description: 'Email ou mot de passe incorrect.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Stack spacing={8} mx={'auto'} maxW={'lg'} py={12} px={6}>
      <Stack align={'center'}>
        <Text fontSize={'4xl'} fontWeight={'bold'} color={'brand.500'}>
          Se connecter
        </Text>
        <Text fontSize={'lg'} color={'gray.600'}>
          pour accéder à votre compte AudioNexus
        </Text>
      </Stack>
      <Box
        rounded={'lg'}
        bg={useColorModeValue('white', 'gray.700')}
        boxShadow={'lg'}
        p={8}
      >
        <form onSubmit={handleSubmit(onSubmit)}>
          <Stack spacing={4}>
            <FormControl id="email" isInvalid={!!errors.email}>
              <FormLabel>Email</FormLabel>
              <Input
                type="email"
                placeholder="votre@email.com"
                {...register('email')}
              />
              {errors.email && (
                <Text color="red.500" fontSize="sm" mt={1}>
                  {errors.email.message}
                </Text>
              )}
            </FormControl>
            <FormControl id="password" isInvalid={!!errors.password}>
              <FormLabel>Mot de passe</FormLabel>
              <InputGroup>
                <Input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  {...register('password')}
                />
                <InputRightElement h={'full'}>
                  <Button
                    variant={'ghost'}
                    onClick={() => setShowPassword((show) => !show)}
                  >
                    {showPassword ? <ViewOffIcon /> : <ViewIcon />}
                  </Button>
                </InputRightElement>
              </InputGroup>
              {errors.password && (
                <Text color="red.500" fontSize="sm" mt={1}>
                  {errors.password.message}
                </Text>
              )}
            </FormControl>
            <Stack spacing={10} pt={2}>
              <Button
                loadingText="Connexion en cours..."
                size="lg"
                colorScheme="brand"
                type="submit"
                isLoading={isLoading}
              >
                Se connecter
              </Button>
            </Stack>
            <Stack pt={6}>
              <Text align={'center'}>
                Pas encore de compte ?{' '}
                <RouterLink to="/register" style={{ color: '#3182ce' }}>
                  S'inscrire
                </RouterLink>
              </Text>
              <Text align={'center'} mt={2}>
                <RouterLink to="/forgot-password" style={{ color: '#3182ce' }}>
                  Mot de passe oublié ?
                </RouterLink>
              </Text>
            </Stack>
          </Stack>
        </form>
      </Box>
    </Stack>
  );
};

export default LoginPage;
