"""
Exceptions personnalisées pour l'application AudioNexus.

Ce module définit les exceptions personnalisées utilisées dans toute l'application.
"""


class AudioNexusError(Exception):
    """Classe de base pour toutes les exceptions de l'application."""

    status_code = 400
    message = "Une erreur est survenue"

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        """Convertit l'exception en dictionnaire pour la réponse API."""
        rv = dict(self.payload or ())
        rv["message"] = self.message
        rv["status"] = "error"
        rv["code"] = self.status_code
        return rv


class AuthenticationError(AudioNexusError):
    """Erreur d'authentification."""

    status_code = 401
    message = "Authentification requise"


class AuthorizationError(AudioNexusError):
    """Erreur d'autorisation."""

    status_code = 403
    message = "Accès non autorisé"


class NotFoundError(AudioNexusError):
    """Ressource non trouvée."""

    status_code = 404
    message = "Ressource non trouvée"


class ValidationError(AudioNexusError):
    """Erreur de validation des données."""

    status_code = 400
    message = "Erreur de validation"


class UserAlreadyExistsError(ValidationError):
    """Un utilisateur avec cet email existe déjà."""

    message = "Un utilisateur avec cet email existe déjà"


class UserNotActiveError(AuthenticationError):
    """Le compte utilisateur est désactivé."""

    status_code = 403
    message = "Ce compte est désactivé"


class InvalidTokenError(AuthenticationError):
    """Le token fourni est invalide ou expiré."""

    message = "Token invalide ou expiré"


class InvalidCredentialsError(AuthenticationError):
    """Les identifiants fournis sont incorrects."""

    message = "Email ou mot de passe incorrect"


class ResourceExistsError(ValidationError):
    """La ressource que vous essayez de créer existe déjà."""

    message = "Cette ressource existe déjà"


class RateLimitExceededError(AudioNexusError):
    """La limite de requêtes a été dépassée."""

    status_code = 429
    message = "Trop de requêtes. Veuillez réessayer plus tard."
