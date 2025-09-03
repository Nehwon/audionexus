"""
Configuration des fixtures partagées pour les tests.
"""
import pytest
from datetime import datetime, timedelta

from app import create_app, db as _db
from app.db.models import User, Role


class TestConfig:
    """Configuration pour les tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Utilisation de la mémoire pour les tests
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    JWT_SECRET_KEY = 'test-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    MAIL_SUPPRESS_SEND = True  # Désactive l'envoi d'emails pendant les tests
    
    # Configuration VoidAuth pour les tests
    VOIDAUTH_SERVER_URL = "http://localhost:8080"
    VOIDAUTH_REALM = "master"  # Utiliser le royaume master pour les tests
    VOIDAUTH_CLIENT_ID = "test-client"
    VOIDAUTH_CLIENT_SECRET = "test-secret"
    VOIDAUTH_ADMIN_USER = "admin"
    VOIDAUTH_ADMIN_PASSWORD = "admin"
    
    # Désactiver la vérification SSL pour les tests
    OIDC_DISABLE_SSL_VERIFICATION = True


@pytest.fixture(scope='session')
def app():
    """Crée une application Flask pour les tests."""
    # Créer l'application avec la configuration de test
    _app = create_app(TestConfig)
    
    # Créer un contexte d'application
    with _app.app_context():
        # Créer les tables de la base de données
        _db.create_all()
        
        # Créer les rôles par défaut
        _setup_test_data(_db)
        
        yield _app
        
        # Nettoyage après les tests
        _db.session.remove()
        _db.drop_all()

def _setup_test_data(db_session):
    """Configure les données de test initiales."""
    # Vérifier si les rôles existent déjà pour éviter les doublons
    if not db_session.query(Role).first():
        # Créer les rôles par défaut
        roles = [
            Role(name='admin', description='Administrateur du système'),
            Role(name='user', description='Utilisateur standard'),
            Role(name='moderator', description='Modérateur')
        ]
        
        db_session.add_all(roles)
        db_session.commit()


@pytest.fixture(scope='session')
def db(app):
    """Fournit une instance de la base de données pour les tests."""
    return _db


@pytest.fixture
def db_session(app, db):
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
def client(app):
    """Crée un client de test pour les requêtes HTTP."""
    return app.test_client()


@pytest.fixture
def test_user(db_session):
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
        is_active=True,
        roles=[user_role]
    )
    db_session.add(user)
    db_session.commit()
    
    return user


@pytest.fixture
def admin_user(db_session):
    """Crée un utilisateur administrateur de test."""
    # Vérifier si le rôle admin existe déjà
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrateur')
        db_session.add(admin_role)
        db_session.commit()
    
    # Créer l'utilisateur admin de test
    admin = User(
        username='adminuser',
        email='admin@example.com',
        password='adminpassword',
        is_active=True,
        roles=[admin_role]
    )
    db_session.add(admin)
    db_session.commit()
    
    return admin


@pytest.fixture
def test_token(app, test_user):
    """Génère un token JWT valide pour les tests."""
    from app.services.auth import create_access_token
    
    # Créer un token d'accès
    access_token = create_access_token(identity=test_user.id)
    return access_token


@pytest.fixture
def admin_token(app, admin_user):
    """Génère un token JWT admin valide pour les tests."""
    from app.services.auth import create_access_token
    
    # Créer un token d'accès pour l'admin
    access_token = create_access_token(identity=admin_user.id)
    return access_token


@pytest.fixture
def authenticated_client(client, test_token):
    """Crée un client de test authentifié."""
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {test_token}'
    return client


@pytest.fixture
def authenticated_admin_client(client, admin_token):
    """Crée un client de test authentifié en tant qu'admin."""
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {admin_token}'
    return client


@pytest.fixture
def mock_send_email(mocker):
    """Mock pour l'envoi d'emails."""
    return mocker.patch('app.services.email.send_email')


@pytest.fixture
def mock_send_password_reset_email(mocker):
    """Mock pour l'envoi d'emails de réinitialisation de mot de passe."""
    return mocker.patch('app.services.email.send_password_reset_email')


@pytest.fixture
def mock_generate_password_reset_token(mocker):
    """Mock pour la génération de token de réinitialisation de mot de passe."""
    return mocker.patch('app.services.auth.generate_password_reset_token')


@pytest.fixture
def mock_verify_password_reset_token(mocker):
    """Mock pour la vérification de token de réinitialisation de mot de passe."""
    return mocker.patch('app.services.auth.verify_password_reset_token')
