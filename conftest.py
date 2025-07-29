"""
Configuration des fixtures et hooks pour les tests pytest.
"""
import os
import sys
from pathlib import Path
from typing import Generator, Any, Dict

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db as _db
from app.db.models import Base, User, Role


@pytest.fixture(scope="session")
def app() -> Generator[Flask, None, None]:
    """Crée une application Flask pour les tests."""
    # Configuration pour les tests
    test_config: Dict[str, Any] = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.getenv(
            "TEST_DATABASE_URL", "sqlite:///:memory:"
        ),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
        "JWT_SECRET_KEY": "test-jwt-secret",
    }

    # Créer l'application avec la configuration de test
    _app = create_app(test_config)
    
    # Créer un contexte d'application
    ctx = _app.app_context()
    ctx.push()

    # Créer les tables de la base de données
    _db.create_all()

    yield _app

    # Nettoyage après les tests
    _db.drop_all()
    ctx.pop()


@pytest.fixture(scope="session")
def db(app: Flask) -> Generator[SQLAlchemy, None, None]:
    """Fournit une instance de la base de données pour les tests."""
    with app.app_context():
        yield _db


@pytest.fixture
def db_session(db: SQLAlchemy) -> Generator[Any, None, None]:
    """Crée une nouvelle session de base de données pour chaque test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    
    db.session = session
    
    yield session
    
    # Nettoyage après chaque test
    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def client(app: Flask) -> Any:
    """Crée un client de test pour les requêtes HTTP."""
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def runner(app: Flask) -> Any:
    """Crée un runner pour les commandes CLI."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(db_session: Any) -> User:
    """Crée un utilisateur de test."""
    # Vérifier si le rôle utilisateur existe déjà
    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user', description='Utilisateur standard')
        db_session.add(user_role)
        db_session.commit()
    
    # Créer l'utilisateur de test
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpassword',
        is_active=True
    )
    user.roles.append(user_role)
    db_session.add(user)
    db_session.commit()
    
    return user


@pytest.fixture
def test_token(app: Flask, test_user: User) -> str:
    """Génère un token JWT valide pour les tests."""
    from app.services.auth import create_access_token
    return create_access_token(identity=test_user.id)


# Hook pour les tests d'intégration
def pytest_configure(config: Any) -> None:
    """Configuration des tests d'intégration."""
    # Marqueurs personnalisés
    config.addinivalue_line("markers", "integration: marque les tests d'intégration")
    config.addinivalue_line("markers", "unit: marque les tests unitaires")
    config.addinivalue_line("markers", "slow: marque les tests lents")
