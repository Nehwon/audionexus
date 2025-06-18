import { Box, Heading, Text, VStack, Tabs, TabList, TabPanels, Tab, TabPanel, FormControl, FormLabel, Input, Button, useToast } from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../context/AuthContext';

interface ProfileFormData {
  email: string;
  fullName: string;
}

const SettingsPage = () => {
  const { user } = useAuth();
  const toast = useToast();
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<ProfileFormData>({
    defaultValues: {
      email: user?.email || '',
      fullName: user?.full_name || '',
    },
  });

  const onSubmit = async (data: ProfileFormData) => {
    try {
      // TODO: Implémenter la mise à jour du profil
      console.log('Updating profile with:', data);
      
      toast({
        title: 'Profil mis à jour',
        description: 'Vos informations ont été mises à jour avec succès.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error updating profile:', error);
      
      toast({
        title: 'Erreur',
        description: 'Une erreur est survenue lors de la mise à jour de votre profil.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading as="h1" size="xl" mb={2}>
            Paramètres
          </Heading>
          <Text color="gray.600">
            Gérez les paramètres de votre compte et de l'application
          </Text>
        </Box>

        <Tabs variant="enclosed">
          <TabList>
            <Tab>Profil</Tab>
            <Tab>Mot de passe</Tab>
            <Tab>Préférences</Tab>
          </TabList>

          <TabPanels>
            <TabPanel p={6} bg="white" borderRadius="lg" boxShadow="sm" borderWidth="1px">
              <form onSubmit={handleSubmit(onSubmit)}>
                <VStack spacing={4} align="stretch">
                  <FormControl id="email">
                    <FormLabel>Adresse email</FormLabel>
                    <Input type="email" {...register('email')} />
                  </FormControl>
                  
                  <FormControl id="fullName">
                    <FormLabel>Nom complet</FormLabel>
                    <Input {...register('fullName')} />
                  </FormControl>
                  
                  <Button
                    mt={4}
                    colorScheme="blue"
                    type="submit"
                    isLoading={isSubmitting}
                    loadingText="Enregistrement..."
                  >
                    Enregistrer les modifications
                  </Button>
                </VStack>
              </form>
            </TabPanel>
            
            <TabPanel p={6} bg="white" borderRadius="lg" boxShadow="sm" borderWidth="1px">
              <Text>Fonctionnalité de changement de mot de passe à venir.</Text>
            </TabPanel>
            
            <TabPanel p={6} bg="white" borderRadius="lg" boxShadow="sm" borderWidth="1px">
              <Text>Préférences de l'application à venir.</Text>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>
    </Box>
  );
};

export default SettingsPage;
