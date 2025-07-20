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

## Sécurité

- Ne partagez jamais les identifiants d'administration
- Utilisez toujours HTTPS pour les connexions distantes
- Limitez l'accès aux endpoints d'administration
