"""
Tests pour le service d'emails.
"""
import pytest
from unittest.mock import patch, MagicMock
from flask import current_app

from app.services.email import send_email, send_password_reset_email, send_welcome_email

def test_send_email_success(app):
    """Teste l'envoi d'un email avec succès."""
    with app.app_context():
        # Configuration pour les tests
        app.config.update(
            MAIL_ENABLED=True,
            MAIL_SERVER='smtp.example.com',
            MAIL_PORT=587,
            MAIL_USE_TLS=True,
            MAIL_USERNAME='test@example.com',
            MAIL_PASSWORD='password',
            MAIL_DEFAULT_SENDER='noreply@example.com'
        )
        
        with patch('smtplib.SMTP') as mock_smtp:
            # Configuration du mock SMTP
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            mock_server.__enter__.return_value = mock_server
            
            # Appel de la fonction à tester
            result = send_email(
                to_email='recipient@example.com',
                subject='Test Email',
                html_content='<h1>Test</h1>',
                text_content='Test'
            )
            
            # Vérifications
            assert result is True
            mock_smtp.assert_called_once_with('smtp.example.com', 587, timeout=10)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with('test@example.com', 'password')
            mock_server.send_message.assert_called_once()

def test_send_email_disabled(app):
    """Teste que l'envoi d'email est désactivé quand MAIL_ENABLED=False."""
    with app.app_context():
        app.config.update(MAIL_ENABLED=False)
        
        with patch('smtplib.SMTP') as mock_smtp:
            result = send_email(
                to_email='recipient@example.com',
                subject='Test Email',
                html_content='<h1>Test</h1>'
            )
            
            assert result is False
            mock_smtp.assert_not_called()

def test_send_password_reset_email(app):
    """Teste l'envoi d'un email de réinitialisation de mot de passe."""
    with app.app_context():
        app.config.update(
            MAIL_ENABLED=True,
            FRONTEND_URL='http://localhost:3000'
        )
        
        with patch('app.services.email.send_email') as mock_send_email:
            # Appel de la fonction à tester
            token = 'test-token-123'
            result = send_password_reset_email('user@example.com', token)
            
            # Vérifications
            assert result is not None
            mock_send_email.assert_called_once()
            
            # Vérifie que l'URL de réinitialisation est correcte
            args, _ = mock_send_email.call_args
            assert args[0] == 'user@example.com'
            assert 'Réinitialisation de votre mot de passe' in args[1]
            assert token in args[2]  # Le token doit être dans le contenu HTML

def test_send_welcome_email(app):
    """Teste l'envoi d'un email de bienvenue."""
    with app.app_context():
        app.config.update(MAIL_ENABLED=True)
        
        with patch('app.services.email.send_email') as mock_send_email:
            # Appel de la fonction à tester
            result = send_welcome_email('newuser@example.com', 'newuser')
            
            # Vérifications
            assert result is not None
            mock_send_email.assert_called_once()
            
            # Vérifie que le nom d'utilisateur est dans le contenu
            args, _ = mock_send_email.call_args
            assert 'newuser' in args[2]  # Le nom d'utilisateur doit être dans le contenu HTML
