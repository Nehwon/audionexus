# Projet AudioNexus - Gestionnaire d'Audiothèques

## 🎯 Objectif
Développer une plateforme complète pour gérer et administrer plusieurs instances de bibliothèques audio à partir d'une interface unifiée, avec des fonctionnalités avancées de traitement et de gestion des livres audio.

## 🚀 Fonctionnalités

### 1. Authentification et Sécurité

#### Court terme
- [ ] Page de connexion sécurisée
  - Authentification par identifiant/mot de passe
  - Chiffrement et salage des mots de passe (bcrypt/Argon2)
  - Réinitialisation de mot de passe par email
  - Gestion des sessions

#### Moyen terme
- [ ] Authentification à deux facteurs (2FA)
- [ ] Gestion des rôles et permissions
- [ ] Limitation des tentatives de connexion
- [ ] Journalisation des accès

#### Long terme
- [ ] Intégration avec des fournisseurs d'identité (OAuth, LDAP)
- [ ] Gestion des clés API

### 2. Tableau de Bord Administrateur

#### Court terme
- [ ] Vue d'ensemble des fichiers en traitement
- [ ] État des instances Audiobookshelf connectées
- [ ] Liste des nouveaux fichiers non traités
- [ ] Métriques d'utilisation

#### Moyen terme
- [ ] Tableaux de bord personnalisables
- [ ] Rapports d'activité
- [ ] Alertes et notifications

### 3. Gestion des Fichiers

#### Court terme
- [ ] Zone de dépôt sécurisée avec analyse antivirus
- [ ] Téléchargement de fichiers compressés (ZIP, RAR, TAR.GZ)
- [ ] Extraction et validation des fichiers
- [ ] Prévisualisation des métadonnées
- [ ] Édition des métadonnées
- [ ] Génération de fichiers M4B

#### Moyen terme
- [ ] Téléchargement direct depuis des liens externes
- [ ] Détection automatique des chapitres
- [ ] Normalisation du volume audio
- [ ] Conversion de formats audio

#### Long terme
- [ ] Génération d'audiobooks à partir d'EPUB
- [ ] Synthèse vocale avancée

### 4. Gestion des Instances Audiobookshelf

#### Court terme
- [ ] Connexion à une instance Audiobookshelf
- [ ] Vue unifiée du contenu
- [ ] Transfert de fichiers vers une instance

#### Moyen terme
- [ ] Gestion de plusieurs instances
- [ ] Répartition de charge entre instances
- [ ] Synchronisation du contenu

#### Long terme
- [ ] Gestion de cluster Audiobookshelf
- [ ] Réplication automatique

## 🛠️ Architecture Technique

### Frontend
- Framework : React.js avec TypeScript
- UI : Chakra UI (bibliothèque principale)
- État : Redux Toolkit
- Requêtes : React Query
- Validation de formulaire : React Hook Form
- Gestion des thèmes : Chakra UI Theme
- Internationalisation : i18next

### Backend
- **Framework** : FastAPI (Python 3.10+)
- **Base de données** : PostgreSQL 14+
- **Cache** : Redis
- **File d'attente** : Celery avec Redis/RabbitMQ
- **Stockage** : Système de fichiers local/S3
- **Synchronisation** : Service de synchronisation des utilisateurs avec Audiobookshelf
- **Tâches asynchrones** : Gestion des opérations de synchronisation en arrière-plan

### Sécurité & Synchronisation
- **Authentification** : JWT avec refresh tokens
- **Hachage** : bcrypt/Argon2 pour les mots de passe
- **Protection** : CSRF/XSS
- **Validation** : Stricte des entrées
- **Synchronisation des utilisateurs** :
  - Mappage des rôles entre AudioNexus et Audiobookshelf
  - Synchronisation bidirectionnelle des comptes
  - Gestion des permissions unifiée
  - Journalisation des actions de synchronisation
- Protection CSRF, XSS, etc.

## 📊 Base de Données

### Modèles Principaux
- **Utilisateurs et Rôles**
  - Profils utilisateurs étendus
  - Mappage des rôles avec Audiobookshelf
  - Historique des synchronisations
- **Fichiers et Métadonnées**
  - Suivi des fichiers par utilisateur
  - Métadonnées étendues
- **Tâches de Traitements**
  - Tâches de synchronisation
  - File d'attente prioritaire
- **Instances Audiobookshelf**
  - Configuration de connexion
  - Statut de synchronisation
  - Métriques de performance
- **Journaux d'Activité**
  - Actions utilisateur
  - Événements de synchronisation
  - Erreurs et avertissements

## 📂 Structure de Stockage

```
/storage/
  /temp/                  # Fichiers temporaires
  /uploads/               # Fichiers téléchargés
  /processed/             # Fichiers traités
  /exports/               # Fichiers exportés
  /backups/               # Sauvegardes
```

## 🔄 Workflow de Traitement

1. Dépôt du fichier (upload ou lien)
2. Analyse antivirus/malware
3. Extraction et validation
4. Extraction des métadonnées
5. Révision/édition des métadonnées
6. Traitement (conversion, normalisation)
7. Transfert vers l'instance cible
8. Nettoyage et archivage

## 📅 Feuille de Route

### Version 0.3.0 (Courant)
- Authentification de base
- Interface administrateur minimale
- Gestion des fichiers de base

### Version 0.5.0
- Gestion avancée des utilisateurs
- Tableau de bord complet
- Traitement par lots

### Version 1.0.0
- Gestion multi-instances
- API complète
- Documentation utilisateur

## 📝 Notes Additionnelles

### Nom de Projet Officiel
AudioNexus
