import {
  Box,
  Flex,
  Button,
  useColorModeValue,
  Stack,
  useColorMode,
  Heading,
  HStack,
  IconButton,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  useDisclosure,
} from '@chakra-ui/react';
import { MoonIcon, SunIcon, HamburgerIcon, CloseIcon } from '@chakra-ui/icons';
import { Link as RouterLink } from 'react-router-dom';

const Navbar = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bg = useColorModeValue('white', 'gray.800');

  return (
    <Box bg={bg} px={4} boxShadow="sm">
      <Flex h={16} alignItems={'center'} justifyContent={'space-between'} maxW="container.xl" mx="auto">
        <HStack spacing={4} alignItems="center">
          <IconButton
            size="md"
            icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
            aria-label="Ouvrir le menu"
            display={{ md: 'none' }}
            onClick={isOpen ? onClose : onOpen}
          />
          <Heading as={RouterLink} to="/" size="md" color="brand.500" _hover={{ textDecoration: 'none' }}>
            AudioNexus
          </Heading>
        </HStack>

        <HStack as={'nav'} spacing={4} display={{ base: 'none', md: 'flex' }}>
          <Button as={RouterLink} to="/dashboard" variant="ghost">Tableau de bord</Button>
          <Button as={RouterLink} to="/library" variant="ghost">Bibliothèque</Button>
          <Button as={RouterLink} to="/upload" variant="ghost">Téléverser</Button>
        </HStack>

        <Flex alignItems={'center'}>
          <Stack direction={'row'} spacing={4}>
            <IconButton
              onClick={toggleColorMode}
              icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
              aria-label="Changer le thème"
              variant="ghost"
            />
            <Menu>
              <MenuButton
                as={Button}
                rounded={'full'}
                variant={'link'}
                cursor={'pointer'}
                minW={0}
              >
                <Avatar
                  size={'sm'}
                  name="Utilisateur"
                  src=""
                />
              </MenuButton>
              <MenuList>
                <MenuItem as={RouterLink} to="/profile">Profil</MenuItem>
                <MenuItem as={RouterLink} to="/settings">Paramètres</MenuItem>
                <MenuDivider />
                <MenuItem color="red.500">Déconnexion</MenuItem>
              </MenuList>
            </Menu>
          </Stack>
        </Flex>
      </Flex>

      {isOpen ? (
        <Box pb={4} display={{ md: 'none' }}>
          <Stack as={'nav'} spacing={4}>
            <Button as={RouterLink} to="/dashboard" variant="ghost" justifyContent="flex-start">Tableau de bord</Button>
            <Button as={RouterLink} to="/library" variant="ghost" justifyContent="flex-start">Bibliothèque</Button>
            <Button as={RouterLink} to="/upload" variant="ghost" justifyContent="flex-start">Téléverser</Button>
          </Stack>
        </Box>
      ) : null}
    </Box>
  );
};

export default Navbar;
