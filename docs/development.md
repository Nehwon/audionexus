# Guide de Développement AudioNexus

Ce document fournit des informations pour les développeurs souhaitant contribuer à AudioNexus.

## Table des Matières

1. [Environnement de Développement](#environnement-de-développement)
2. [Structure du Projet](#structure-du-projet)
3. [Standards de Code](#standards-de-code)
4. [Tests](#tests)
5. [Documentation](#documentation)
6. [Workflow Git](#workflow-git)
7. [Débogage](#débogage)
8. [Performance](#performance)
9. [Sécurité](#sécurité)
10. [Déploiement](#déploiement)

## Environnement de Développement

### Prérequis

- Docker 20.10+ et Docker Compose
- Python 3.9+
- Node.js 16+ et npm 8+
- Git

### Configuration Initiale

1. Cloner le dépôt :
   ```bash
   git clone https://gitea.lamachere.fr/fabrice/AudioNexus.git
   cd AudioNexus
   ```

2. Copier les fichiers d'environnement :
   ```bash
   cp .env.example .env
   ```

3. Démarrer les services :
   ```bash
   docker-compose up -d
   ```

4. Installer les dépendances du backend :
   ```bash
   docker-compose exec backend pip install -e ".[dev]"
   ```

5. Installer les dépendances du frontend :
   ```bash
   cd audionexus/frontend
   npm install
   ```

6. Appliquer les migrations :
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

## Structure du Projet

```
audionexus/
├── backend/                 # Code source du backend
│   ├── app/
│   │   ├── api/            # Points de terminaison API
│   │   ├── core/            # Configuration et utilitaires
│   │   ├── db/              # Modèles et migrations
│   │   ├── models/          # Modèles Pydantic
│   │   ├── services/        # Logique métier
│   │   └── main.py          # Point d'entrée
│   ├── tests/               # Tests du backend
│   └── alembic/             # Migrations de base de données
│
├── frontend/               # Application React
│   ├── public/
│   └── src/
│       ├── components/      # Composants React
│       ├── pages/           # Pages de l'application
│       ├── services/        # Services API
│       └── App.tsx          # Composant racine
│
├── docs/                   # Documentation
├── nginx/                   # Configuration Nginx
└── scripts/                 # Scripts utilitaires
```

## Standards de Code

### Backend (Python)

- Suivre [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utiliser des docstrings Google Style
- Type hints pour toutes les fonctions
- Maximum 120 caractères par ligne

Exemple :

```python
def get_user(user_id: int, db: Session) -> Optional[User]:
    """Récupère un utilisateur par son ID.
    
    Args:
        user_id: L'ID de l'utilisateur
        db: Session de base de données
        
    Returns:
        L'utilisateur ou None si non trouvé
    """
    return db.query(User).filter(User.id == user_id).first()
```

### Frontend (TypeScript/React)

- Fonctions composantes nommées
- TypeScript strict
- Hooks personnalisés pour la logique réutilisable
- CSS Modules pour le style

Exemple :

```tsx
interface UserProfileProps {
  userId: number;
  onUpdate: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ userId, onUpdate }) => {
  const [user, setUser] = useState<User | null>(null);
  
  useEffect(() => {
    const fetchUser = async () => {
      const data = await userService.getUser(userId);
      setUser(data);
    };
    
    fetchUser();
  }, [userId]);
  
  if (!user) return <div>Chargement...</div>;
  
  return (
    <div className={styles.profile}>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
};
```

## Tests

### Backend

Exécuter tous les tests :

```bash
docker-compose exec backend pytest
```

Exécuter un test spécifique :

```bash
docker-compose exec backend pytest tests/test_users.py -v
```

### Frontend

Exécuter les tests :

```bash
cd audionexus/frontend
npm test
```

### Couverture de Code

Backend :

```bash
docker-compose exec backend pytest --cov=app tests/
```

## Documentation

### Génération de la Documentation

Backend :

```bash
docker-compose exec backend pdoc --html -o docs/api app
```

Frontend :

```bash
cd audionexus/frontend
npm run build-storybook
```

## Workflow Git

1. Créer une branche :
   ```bash
   git checkout -b feature/nouvelle-fonctionnalite
   ```

2. Faire des commits atomiques :
   ```bash
   git commit -m "feat(users): ajouter la suppression d'utilisateur"
   ```

3. Pousser les modifications :
   ```bash
   git push -u origin feature/nouvelle-fonctionnalite
   ```

4. Créer une Pull Request

## Débogage

### Backend

Activer les logs de débogage :

```bash
docker-compose logs -f backend
```

### Frontend

Ouvrir les outils de développement du navigateur (F12)

## Performance

### Backend

- Utiliser `async/await` pour les opérations I/O
- Mettre en cache les requêtes fréquentes
- Utiliser des index de base de données appropriés

### Frontend

- Utiliser `React.memo` pour les composants coûteux
- Implémenter le chargement paresseux des routes
- Optimiser les re-rendus

## Sécurité

- Ne jamais exposer de données sensibles dans les logs
- Valider toutes les entrées utilisateur
- Utiliser des requêtes paramétrées pour la base de données
- Mettre à jour régulièrement les dépendances

## Déploiement

### Environnements

- **Développement** : `docker-compose up -d`
- **Staging** : `docker-compose -f docker-compose.staging.yml up -d`
- **Production** : Utiliser Kubernetes ou un service d'orchestration

### Migration des Données

Créer une nouvelle migration :

```bash
docker-compose exec backend alembic revision --autogenerate -m "description"
```

Appliquer les migrations :

```bash
docker-compose exec backend alembic upgrade head
```

## Support

Pour toute question, ouvrez une [issue](https://gitea.lamachere.fr/fabrice/AudioNexus/issues) ou contactez l'équipe de développement.
