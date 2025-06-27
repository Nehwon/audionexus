# Notes sur la migration Pydantic v2 et SQLAlchemy 2.0 asynchrone

## Contexte

Le projet est en cours de migration vers une stack technique plus moderne :
- Pydantic v2 (migration depuis v1)
- SQLAlchemy 2.0 avec support natif asynchrone
- FastAPI avec support asynchrone

## État actuel

### Problèmes identifiés
1. **Incompatibilité de versions** :
   - FastAPI 0.115.14 + Pydantic 2.11.7 installés
   - Mais le code est écrit pour Pydantic v1.x
   - Erreur `TypeAdapter[typing.Annotated[ForwardRef('JoinTransactionMode')...` typique d'une incompatibilité

2. **Structure du projet** :
   - Correction des doublons de dossiers backend
   - Standardisation sur l'utilisation de sessions asynchrones
   - Migration des modèles SQLAlchemy vers la syntaxe 2.0

### Modifications récentes
- Migration complète des modèles ORM vers SQLAlchemy 2.0 asynchrone
- Refactorisation de l'exposition des modèles dans `models/__init__.py`
- Mise à jour de la documentation et de la structure du projet
- Correction des chemins d'importation

## Prochaines étapes

1. **Mise à jour des dépendances** :
   - Mettre à jour `pyproject.toml` et `requirements.txt`
   - S'assurer de la compatibilité entre FastAPI et Pydantic v2

2. **Migration du code** :
   - Adapter les schémas Pydantic pour la v2
   - Mettre à jour la configuration FastAPI
   - Tester les endpoints critiques

3. **Tests** :
   - Vérifier le fonctionnement de l'authentification
   - Tester la création d'utilisateur via /register
   - Valider les performances avec la nouvelle stack asynchrone

## Notes techniques

### Modèles SQLAlchemy
- Utilisation de `Mapped` et `mapped_column`
- Relations définies avec `relationship` et chargement lazy optimisé
- Gestion des timezones avec `timezone=True`

### Schémas Pydantic
- Migration vers Pydantic v2 avec `model_config`
- Validation des champs avec `Field`
- Gestion des types optionnels avec `Optional`

## Références
- [Documentation Pydantic v2](https://docs.pydantic.dev/latest/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [FastAPI avec SQLAlchemy 2.0](https://fastapi.tiangolo.com/advanced/sql-databases-peewee/)
