"""
Tests pour le modèle User.
"""
import pytest
from datetime import datetime, timedelta

from app.db.models import User, Role


def test_create_user(db_session):
    """Teste la création d'un utilisateur."""
    # Créer un rôle
    role = Role(name='test_role', description='Test Role')
    db_session.add(role)
    db_session.commit()
    
    # Créer un utilisateur
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpassword',
        is_active=True
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    
    # Vérifier que l'utilisateur a été créé
    assert user.id is not None
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('testpassword')
    assert user.is_active is True
    assert len(user.roles) == 1
    assert user.roles[0].name == 'test_role'
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_user_password_hashing():
    """Teste le hachage du mot de passe."""
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpassword')
    
    # Vérifier que le mot de passe est bien haché
    assert user.password_hash is not None
    assert user.password_hash != 'testpassword'
    
    # Vérifier que la vérification du mot de passe fonctionne
    assert user.check_password('testpassword') is True
    assert user.check_password('wrongpassword') is False


def test_user_roles(db_session):
    """Teste l'ajout de rôles à un utilisateur."""
    # Créer des rôles
    role1 = Role(name='admin', description='Administrator')
    role2 = Role(name='moderator', description='Moderator')
    db_session.add_all([role1, role2])
    db_session.commit()
    
    # Créer un utilisateur avec des rôles
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpassword'
    )
    user.roles.extend([role1, role2])
    db_session.add(user)
    db_session.commit()
    
    # Vérifier les rôles
    assert len(user.roles) == 2
    assert {role.name for role in user.roles} == {'admin', 'moderator'}


def test_user_repr():
    """Teste la représentation en chaîne d'un utilisateur."""
    user = User(username='testuser', email='test@example.com')
    assert repr(user) == "<User 'testuser'>"


def test_user_to_dict():
    """Teste la conversion d'un utilisateur en dictionnaire."""
    user = User(
        id=1,
        username='testuser',
        email='test@example.com',
        is_active=True
    )
    user_dict = user.to_dict()
    
    assert user_dict['id'] == 1
    assert user_dict['username'] == 'testuser'
    assert user_dict['email'] == 'test@example.com'
    assert user_dict['is_active'] is True
    assert 'password_hash' not in user_dict  # Le mot de passe ne doit pas être inclus


def test_user_last_seen(db_session):
    """Teste la mise à jour de la date de dernière connexion."""
    user = User(username='testuser', email='test@example.com', password='test')
    db_session.add(user)
    db_session.commit()
    
    # Vérifier que last_seen est initialement None
    assert user.last_seen is None
    
    # Mettre à jour last_seen
    now = datetime.utcnow()
    user.update_last_seen()
    db_session.commit()
    
    # Vérifier que last_seen a été mis à jour
    assert user.last_seen is not None
    assert (user.last_seen - now).total_seconds() < 5  # Moins de 5 secondes de différence


def test_user_avatar():
    """Teste la génération d'avatar par défaut."""
    user = User(email='test@example.com')
    
    # Vérifier que l'avatar est généré à partir de l'email
    assert user.avatar(128) == 'https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0?d=identicon&s=128'
    
    # Changer l'email et vérifier que l'avatar change
    user.email = 'another@example.com'
    assert user.avatar(128) == 'https://www.gravatar.com/avatar/5a7b858d208c7e7487d7f5bcc6b6f9a3?d=identicon&s=128'
