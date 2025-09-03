# Intégration Audiobookshelf

Ce document explique comment configurer et utiliser l'intégration entre AudioNexus et Audiobookshelf.

## Prérequis

- Un serveur Audiobookshelf fonctionnel
- Les identifiants d'administration Audiobookshelf
- Les variables d'environnement configurées dans `.env`

## Configuration

### Variables d'environnement

Assurez-vous que les variables suivantes sont définies dans votre fichier `.env` :

```env
# Configuration Audiobookshelf
ABS_API_URL=http://votre-serveur:13378/api
ABS_USERNAME=admin
ABS_PASSWORD=votre-mot-de-passe
```

### Installation des dépendances

Assurez-vous que toutes les dépendances sont installées :

```bash
pip install -r requirements.txt
```

## Utilisation du script de synchronisation

Le script `sync_audiobookshelf.py` permet de synchroniser les données entre AudioNexus et Audiobookshelf.

### Synchronisation manuelle

Pour lancer une synchronisation manuelle :

```bash
python -m app.cli.sync_audiobookshelf
```

Options disponibles :

- `--full` : Effectue une synchronisation complète (même les éléments non modifiés)
- `--libraries ID1 ID2` : Limite la synchronisation à certaines bibliothèques
- `--quiet` : Réduit la verbosité des logs

Exemple :

```bash
python -m app.cli.sync_audiobookshelf --full --libraries lib1 lib2
```

### Mode démon

Pour lancer le service en arrière-plan avec synchronisation périodique :

```bash
python -m app.cli.sync_audiobookshelf --daemon --interval 3600
```

Options du mode démon :

- `--daemon` : Active le mode démon
- `--interval SECONDS` : Définit l'intervalle entre les synchronisations (par défaut: 3600 secondes)
- `--full` : Effectue une synchronisation complète au démarrage

### Intégration avec systemd (Linux)

Pour exécuter le service au démarrage du système, créez un fichier de service systemd :

```ini
# /etc/systemd/system/audionexus-sync.service
[Unit]
Description=AudioNexus Audiobookshelf Sync Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/chemin/vers/audionexus
Environment="PATH=/chemin/vers/venv/bin"
ExecStart=/chemin/vers/venv/bin/python -m app.cli.sync_audiobookshelf --daemon
Restart=always

[Install]
WantedBy=multi-user.target
```

Activez et démarrez le service :

```bash
sudo systemctl daemon-reload
sudo systemctl enable audionexus-sync
sudo systemctl start audionexus-sync
```

## API REST

L'API expose les endpoints suivants sous le préfixe `/api/v1/audiobookshelf/` :

### Bibliothèques

- `GET /libraries` : Liste des bibliothèques
- `GET /libraries/{library_id}` : Détails d'une bibliothèque

### Livres audio

- `GET /recently-added` : Livres récemment ajoutés
- `GET /items/{item_id}` : Détails d'un livre audio
- `GET /search` : Recherche de livres audio
- `POST /upload` : Téléverser un nouveau livre audio

### Collections

- `GET /collections` : Liste des collections

### Progression de lecture

- `GET /progress/{user_id}/{item_id}` : Récupérer la progression
- `POST /progress/{user_id}/{item_id}` : Mettre à jour la progression

### Administration

- `GET /admin/users` : Liste des utilisateurs (admin)

## Dépannage

### Erreurs d'authentification

Vérifiez que :
- L'URL de l'API est correcte et accessible
- Les identifiants sont corrects
- L'utilisateur a les droits d'administration

### Problèmes de synchronisation

- Vérifiez les logs pour des erreurs spécifiques
- Essayez une synchronisation complète avec `--full`
- Vérifiez que la base de données est accessible

## Intégration Docker Optimisée

### Configuration Containerisée

AudioNexus v0.6.0 inclut des optimisations significatives pour l'intégration Docker avec Audiobookshelf :

#### 1. Services Optimisés
```yaml
# docker-compose.yml optimisé
version: '3.8'

services:
  audionexus:
    image: audionexus:latest
    depends_on:
      - database
      - audiobookshelf
    environment:
      - ABS_API_URL=http://audiobookshelf:13378/api
      - ABS_USERNAME=${ABS_USERNAME}
      - ABS_PASSWORD=${ABS_PASSWORD}
    volumes:
      - ./config:/app/config:ro
      - sync_data:/app/sync
    networks:
      - audio_network

  audiobookshelf:
    image: ghcr.io/advplyr/audiobookshelf:latest
    container_name: audiobookshelf
    environment:
      - AUDIOBOOKSHELF_UID=999
      - AUDIOBOOKSHELF_GID=999
    volumes:
      - abs_config:/config
      - abs_metadata:/metadata
      - abs_audiobooks:/audiobooks
    ports:
      - "13378:80"
    networks:
      - audio_network

  database:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=audionexus
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - audio_network

volumes:
  abs_config:
  abs_metadata:
  abs_audiobooks:
  mysql_data:
  sync_data:

networks:
  audio_network:
    driver: bridge
```

#### 2. Optimisations de Performance

**Synchronisation par lots :**
- Traitement par groupes de 50 éléments pour réduire la charge mémoire
- Cache intelligent des métadonnées pour éviter les requêtes répétées
- Compression des données de synchronisation

**Gestion des connexions :**
- Pool de connexions réutilisables avec Audiobookshelf
- Timeouts optimisés pour les environnements à haut débit
- Retry automatique avec backoff exponentiel

#### 3. Monitoring et Health Checks

```yaml
# Health checks intégrés
services:
  audionexus:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  audiobookshelf:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/healthcheck"]
      interval: 60s
      timeout: 10s
      retries: 5
```

#### 4. Variables d'Environnement Avancées

```env
# Configuration de synchronisation avancée
ABS_SYNC_INTERVAL=3600
ABS_SYNC_BATCH_SIZE=50
ABS_MAX_CONNECTIONS=10
ABS_TIMEOUT_SECONDS=30
ABS_RETRY_ATTEMPTS=3

# Optimisations de cache
ABS_CACHE_TTL=7200
ABS_CACHE_MAX_SIZE=500MB

# Métriques et monitoring
ABS_METRICS_ENABLED=true
ABS_METRICS_ENDPOINT=/metrics
```

### Commandes Docker Optimisées

#### Synchronisation Automatisée
```bash
# Démarrage des services avec synchronisation
docker-compose up -d audionexus audiobookshelf

# Vérification de l'état des services
docker-compose ps

# Consultation des logs de synchronisation
docker-compose logs -f audionexus | grep "sync"

# Exécution manuelle de synchronisation
docker-compose exec audionexus python -m app.cli.sync_audiobookshelf --full
```

#### Gestion des Volumes
```bash
# Backup des données
docker run --rm -v audionexus_sync_data:/data -v $(pwd):/backup alpine tar czf /backup/sync_backup.tar.gz -C /data .

# Monitoring de l'espace disque
docker system df

# Nettoyage des volumes inutilisés
docker volume prune -f
```

#### Scaling et Haute Disponibilité
```yaml
# Configuration multi-instance
version: '3.8'

services:
  audionexus-sync-1:
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

  audiobookshelf:
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure

# Load balancer avec Traefik
  traefik:
    image: traefik:v2.5
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - audio_network
```

## Sécurité

- Ne partagez jamais les identifiants d'administration
- Utilisez toujours HTTPS pour les connexions distantes
- Limitez l'accès aux endpoints d'administration
- Utilisez des secrets Docker pour les mots de passe sensibles
- Activez l'audit trail pour les opérations de synchronisation
