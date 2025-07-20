# Documentation d'AudioNexus

Bienvenue dans la documentation du projet AudioNexus. Ce répertoire contient toute la documentation relative au projet, organisée de manière thématique.

## 📁 Structure des Dossiers

```
documentation/
├── api/               # Documentation complète de l'API
│   └── index.md       # Vue d'ensemble de l'API
├── architecture/      # Documentation d'architecture
├── contributing/      # Guides pour les contributeurs
│   ├── CODE_OF_CONDUCT.md
│   ├── CONTRIBUTING.md
│   └── DEVELOPMENT.md
├── decisions/         # Décisions techniques (ADR)
├── guides/            # Guides pratiques
│   ├── installation.md
│   ├── audiobookshelf_integration.md
│   └── examples/
├── images/            # Images pour la documentation
├── reference/         # Documentation de référence
├── user-guide/        # Guide utilisateur
│   └── usage.md
├── CHANGELOG.md       # Journal des modifications
├── ETAT_DU_PROJET.md  # État actuel du projet
└── README.md          # Ce fichier
```

## 📚 Vue d'ensemble

### Pour les Utilisateurs
- [Guide d'installation](guides/installation.md) - Comment installer et configurer AudioNexus
- [Guide d'utilisation](user-guide/usage.md) - Comment utiliser l'application
- [Exemples d'utilisation](guides/examples/) - Exemples concrets

### Pour les Développeurs
- [Documentation de l'API](api/) - Référence complète de l'API
- [Guide du développeur](development/) - Configuration de l'environnement de développement
- [Architecture](architecture/) - Vue d'ensemble de l'architecture
- [Décisions techniques](decisions/) - Archives des décisions d'architecture (ADR)

### Pour les Contributeurs
- [Guide de contribution](contributing/CONTRIBUTING.md) - Comment contribuer au projet
- [Code de conduite](contributing/CODE_OF_CONDUCT.md) - Règles de la communauté
- [Processus de développement](contributing/DEVELOPMENT.md) - Workflow et bonnes pratiques

## 🔍 Génération de la Documentation

### Documentation de l'API

Pour régénérer la documentation de l'API :

```bash
# Depuis la racine du projet
pdoc --html -o documentation/api app --force
```

## 🔄 Mise à Jour

Cette documentation est mise à jour en continu. Consultez régulièrement le [journal des modifications](CHANGELOG.md) pour suivre les évolutions.

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez notre [guide de contribution](contributing/CONTRIBUTING.md) pour commencer.

## 📜 Licence

Ce projet est sous licence [AGPL-3.0-or-later](LICENSE).
