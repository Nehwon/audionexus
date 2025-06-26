# Documentation d'AudioNexus

Bienvenue dans la documentation du projet AudioNexus. Ce répertoire contient toute la documentation relative au projet.

## Structure des Dossiers

```
docs/
├── api/               # Documentation de l'API
├── architecture/      # Documentation d'architecture
├── decisions/         # Décisions techniques (ADR)
├── deployment/       # Guides de déploiement
├── development/       # Documentation pour les développeurs
├── images/            # Images pour la documentation
├── user-guide/        # Guide utilisateur
└── README.md          # Ce fichier
```

## Documentation de l'API

La documentation complète de l'API est disponible dans le dossier `api/`. Elle est générée automatiquement à partir des docstrings du code source.

Pour régénérer la documentation de l'API :

```bash
# Depuis la racine du projet
pdoc --html -o docs/api audionexus/backend/app --force
```

## Architecture

Le dossier `architecture/` contient :
- Des diagrammes d'architecture
- Des explications sur les choix techniques
- Les schémas de base de données
- Les flux de données

## Décisions Techniques (ADR)

Le dossier `decisions/` contient les Architectural Decision Records (ADR) qui documentent les décisions techniques importantes prises pendant le développement.

Format de nommage des fichiers ADR :
```
NNN-titre-en-minuscules-avec-tirets.md
```

Où `NNN` est un numéro séquentiel commençant à 001.

## Déploiement

Le dossier `deployment/` contient les guides de déploiement pour différents environnements :
- Développement local
- Préproduction
- Production

## Guide du Développeur

Le dossier `development/` contient des informations pour les développeurs :
- Configuration de l'environnement
- Standards de code
- Guide de contribution
- Processus de revue de code

## Guide Utilisateur

Le dossier `user-guide/` contient la documentation pour les utilisateurs finaux :
- Guide de prise en main
- Fonctionnalités
- FAQ
- Dépannage

## Comment Contribuer à la Documentation

1. Modifiez les fichiers Markdown dans le dossier approprié
2. Pour les images, ajoutez-les dans le dossier `images/`
3. Mettez à jour la table des matières si nécessaire
4. Soumettez une Pull Request avec vos modifications

## Génération de la Documentation

La documentation peut être générée localement avec MkDocs :

```bash
# Installer MkDocs et le thème Material
pip install mkdocs mkdocs-material

# Lancer le serveur de documentation
mkdocs serve
```

La documentation sera disponible à l'adresse http://127.0.0.1:8000/

## Licence

Cette documentation est sous licence [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/).
