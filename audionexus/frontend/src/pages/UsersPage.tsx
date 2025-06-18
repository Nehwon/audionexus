import { Box, Heading, Text, VStack, Table, Thead, Tbody, Tr, Th, Td } from '@chakra-ui/react';

const UsersPage = () => {
  // TODO: Remplacer par des données réelles de l'API
  const users = [
    { id: 1, email: 'admin@example.com', role: 'Admin' },
    { id: 2, email: 'user@example.com', role: 'Utilisateur' },
  ];

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading as="h1" size="xl" mb={2}>
            Gestion des utilisateurs
          </Heading>
          <Text color="gray.600">
            Gérez les utilisateurs et leurs permissions
          </Text>
        </Box>

        <Box
          p={6}
          bg="white"
          borderRadius="lg"
          boxShadow="sm"
          borderWidth="1px"
          overflowX="auto"
        >
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>ID</Th>
                <Th>Email</Th>
                <Th>Rôle</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {users.map((user) => (
                <Tr key={user.id}>
                  <Td>{user.id}</Td>
                  <Td>{user.email}</Td>
                  <Td>{user.role}</Td>
                  <Td>
                    {/* Boutons d'action à implémenter */}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      </VStack>
    </Box>
  );
};

export default UsersPage;
