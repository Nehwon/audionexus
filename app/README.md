# Application Audiobooks Manager

Ce dossier contient le code source de l'application de gestion d'audiobooks.

## Structure des dossiers

- `api/` : Définition des routes et points d'entrée de l'API
- `core/` : Logique métier principale de l'application
- `db/` : Configuration et modèles de base de données
  - `models/` : Modèles SQLAlchemy
  - `database.py` : Configuration de la connexion à la base de données
- `schemas/` : Schémas Pydantic pour la validation des données
- `services/` : Services métier et logique d'application
- `static/` : Fichiers statiques (CSS, JS, images)
- `tests/` : Tests unitaires et d'intégration
- `utils/` : Utilitaires et helpers
- `config.py` : Configuration de l'application
- `main.py` : Point d'entrée de l'application

## Développement

### Configuration requise

- Python 3.8+
- PostgreSQL
- Dépendances listées dans `requirements.txt`

### Installation

1. Créer un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OU
   .\venv\Scripts\activate  # Windows
   ```

2. Installer les dépendances :
   ```bash
   pip install -e .[dev]  # Pour le développement avec les dépendances optionnelles
   ```

3. Configurer les variables d'environnement (voir `.env.example`)

### Exécution

```bash
uvicorn app.main:app --reload
```

### Tests

```bash
pytest
```
