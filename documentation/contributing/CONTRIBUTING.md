# Guide de Contribution pour AudioNexus

Merci de votre intérêt pour le projet AudioNexus ! Ce document explique comment contribuer de manière efficace.

## Table des matières

1. [Code de Conduite](#code-de-conduite)
2. [Comment Contribuer](#comment-contribuer)
   - [Signaler un Problème](#signaler-un-problème)
   - [Proposer une Amélioration](#proposer-une-amélioration)
   - [Soumettre une Pull Request](#soumettre-une-pull-request)
3. [Environnement de Développement](#environnement-de-développement)
4. [Conventions de Code](#conventions-de-code)
5. [Tests](#tests)
6. [Documentation](#documentation)
7. [Questions](#questions)

## Code de Conduite

En participant à ce projet, vous acceptez de respecter notre [Code de Conduite](CODE_OF_CONDUCT.md).

## Comment Contribuer

### Signaler un Problème

Avant de signaler un problème :

1. Vérifiez qu'il n'a pas déjà été signalé dans les [issues](https://gitea.lamachere.fr/fabrice/AudioNexus/issues).
2. Si le problème n'existe pas, créez une nouvelle issue.
3. Utilisez le modèle d'issue fourni et remplissez toutes les sections demandées.
4. Fournissez des étapes claires pour reproduire le problème.
5. Incluez des captures d'écran ou des exemples de code si nécessaire.

### Proposer une Amélioration

1. Vérifiez qu'une issue n'existe pas déjà pour cette amélioration.
2. Si ce n'est pas le cas, créez une nouvelle issue en utilisant le modèle "Feature Request".
3. Décrivez clairement l'amélioration proposée et son intérêt.
4. Attendez la validation de l'équipe avant de commencer le développement.

### Soumettre une Pull Request

1. **Fork** le dépôt et créez une branche pour votre fonctionnalité :
   ```
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```
2. Si vous avez ajouté du code, ajoutez des tests.
3. Si vous avez modifié des API, mettez à jour la documentation.
4. Assurez-vous que la suite de tests passe.
5. Assurez-vous que votre code respecte les conventions de style.
6. Mettez à jour la documentation si nécessaire.
7. Poussez votre branche et créez une Pull Request.

## Environnement de Développement

### Prérequis

- Python 3.9+
- Node.js 16+
- Docker et Docker Compose
- PostgreSQL 13+
- Redis

### Configuration Initiale

1. Clonez le dépôt :
   ```
   git clone https://gitea.lamachere.fr/fabrice/AudioNexus.git
   cd AudioNexus
   ```

2. Configurez l'environnement :
   ```
   cp .env.example .env
   # Modifiez les variables selon votre configuration
   ```

3. Lancez les services avec Docker :
   ```
   docker-compose up -d
   ```

4. Installez les dépendances du backend :
   ```
   cd audionexus/backend
   python -m pip install -e ".[dev]"
   ```

5. Installez les dépendances du frontend :
   ```
   cd ../frontend
   npm install
   ```

6. Appliquez les migrations de base de données :
   ```
   cd ../../
   docker-compose exec backend alembic upgrade head
   ```

7. Lancez le serveur de développement :
   - Backend : `docker-compose exec backend uvicorn app.main:app --reload`
   - Frontend : `cd audionexus/frontend && npm run dev`

## Conventions de Code

### Backend (Python)

- Suivez le style de code [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utilisez des docstrings pour documenter les fonctions et les classes
- Utilisez des noms de variables descriptifs
- Générez la documentation avec `pdoc`

### Frontend (TypeScript/React)

- Suivez les [React Hooks Rules](https://reactjs.org/docs/hooks-rules.html)
- Utilisez TypeScript pour le typage fort
- Structurez vos composants de manière logique
- Utilisez des noms de variables et de fonctions descriptifs

### Messages de Commit

Suivez le format [Conventional Commits](https://www.conventionalcommits.org/) :

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Exemples :
- `feat(auth): add login functionality`
- `fix(api): resolve 500 error on user creation`
- `docs: update README with new setup instructions`

## Tests

### Backend

Exécutez les tests avec :

```bash
pytest
```

### Frontend

Exécutez les tests avec :

```bash
cd audionexus/frontend
npm test
```

## Documentation

- Mettez à jour la documentation lorsque vous ajoutez ou modifiez des fonctionnalités
- Utilisez des commentaires clairs et concis dans le code
- Documentez les décisions techniques importantes dans `documentation/decisions/`

## Questions

Pour toute question, ouvrez une [discussion](https://gitea.lamachere.fr/fabrice/AudioNexus/discussions) ou contactez l'équipe de développement à l'adresse fabrice@lamachere.fr.
