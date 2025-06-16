# Secrets nécessaires pour le pipeline CI/CD Gitea

## Configuration du registre de conteneurs Gitea
- `DOCKER_USERNAME`: Votre nom d'utilisateur Gitea
- `DOCKER_PASSWORD`: Votre token d'accès Gitea avec les permissions d'écriture sur le registre

## Environnements de déploiement

### Staging
- `STAGING_SSH_KEY`: Clé privée SSH pour la connexion au serveur de staging
- `STAGING_SSH_USER`: Utilisateur SSH pour le serveur de staging
- `STAGING_HOST`: Adresse du serveur de staging
- `STAGING_KNOWN_HOSTS`: Entrée known_hosts pour le serveur de staging

### Production
- `PROD_SSH_KEY`: Clé privée SSH pour la connexion au serveur de production
- `PROD_SSH_USER`: Utilisateur SSH pour le serveur de production
- `PROD_HOST`: Adresse du serveur de production
- `PROD_KNOWN_HOSTS`: Entrée known_hosts pour le serveur de production

## Configuration requise sur Gitea

1. Activer les Actions dans les paramètres du dépôt
2. Configurer les secrets dans les paramètres du dépôt sous "Secrets"
3. S'assurer que le registre de conteneurs est activé pour le dépôt

## Configuration requise sur les serveurs

1. Docker et Docker Compose doivent être installés
2. Le répertoire de l'application doit contenir un `docker-compose.yml` configuré
3. Les variables d'environnement nécessaires doivent être définies dans un fichier `.env`
4. L'utilisateur SSH doit avoir les permissions nécessaires pour exécuter les commandes Docker
