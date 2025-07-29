# Scripts d'administration

Ce répertoire contient des scripts utiles pour l'administration et la maintenance de l'application AudioNexus.

## Scripts disponibles

### `init_db.py`

Gestion de l'initialisation et de la réinitialisation de la base de données.

#### Utilisation

```bash
# Afficher l'aide
python -m scripts.init_db --help

# Initialiser la base de données (créer les tables)
python -m scripts.init_db init

# Supprimer toutes les tables (ATTENTION : supprime toutes les données !)
python -m scripts.init_db drop

# Réinitialiser complètement la base de données (supprimer et recréer les tables)
python -m scripts.init_db recreate
```

#### Variables d'environnement

Le script utilise les mêmes variables d'environnement que l'application principale pour se connecter à la base de données. Assurez-vous que les variables suivantes sont définies dans votre fichier `.env` :

```env
# Configuration de la base de données
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=audionexus

# Ou utilisez directement l'URL de connexion
# DATABASE_URI=postgresql://user:password@localhost/dbname
```

### `sync_audiobookshelf.py`

Script pour synchroniser les données avec un serveur Audiobookshelf distant.

#### Utilisation

```bash
# Afficher l'aide
python -m app.cli.sync_audiobookshelf --help

# Lancer une synchronisation manuelle
python -m app.cli.sync_audiobookshelf

# Lancer une synchronisation complète (même les éléments non modifiés)
python -m app.cli.sync_audiobookshelf --full

# Lancer le service en arrière-plan avec synchronisation toutes les heures
python -m app.cli.sync_audiobookshelf --daemon --interval 3600
```

#### Variables d'environnement

Assurez-vous que les variables suivantes sont définies dans votre fichier `.env` :

```env
# Configuration Audiobookshelf
ABS_API_URL=http://votre-serveur:13378/api
ABS_USERNAME=admin
ABS_PASSWORD=votre-mot-de-passe
```

## Bonnes pratiques

1. **Sauvegarde** : Toujours sauvegarder votre base de données avant d'exécuter des scripts de modification.
2. **Environnement** : Exécutez les scripts dans un environnement de test avant la production.
3. **Permissions** : Assurez-vous que l'utilisateur de la base de données a les permissions nécessaires.
4. **Journaux** : Consultez les journaux pour détecter les erreurs potentielles.
5. **Maintenance** : Planifiez des fenêtres de maintenance pour les opérations critiques.

## Dépannage

### Erreurs de connexion à la base de données

- Vérifiez que le serveur PostgreSQL est en cours d'exécution.
- Vérifiez les informations d'identification dans le fichier `.env`.
- Vérifiez que l'utilisateur a les droits nécessaires sur la base de données.

### Tables non créées

- Vérifiez les erreurs dans la sortie du script.
- Assurez-vous que les modèles SQLAlchemy sont correctement importés.
- Vérifiez que la base de données spécifiée existe.

### Problèmes de synchronisation Audiobookshelf

- Vérifiez que le serveur Audiobookshelf est accessible depuis votre machine.
- Vérifiez les identifiants d'administration.
- Consultez les journaux du serveur Audiobookshelf pour des erreurs potentielles.
