"""
Exceptions personnalisées pour l'intégration avec VoidAuth.
"""


class VoidAuthError(Exception):
    """Classe de base pour toutes les exceptions de VoidAuth."""

    pass


class VoidAuthConfigurationError(VoidAuthError):
    """Erreur de configuration de VoidAuth."""

    pass


class VoidAuthConnectionError(VoidAuthError):
    """Erreur de connexion au serveur VoidAuth."""

    pass


class VoidAuthAuthenticationError(VoidAuthError):
    """Erreur d'authentification avec VoidAuth."""

    pass


class VoidAuthAuthorizationError(VoidAuthError):
    """Erreur d'autorisation avec VoidAuth."""

    pass


class VoidAuthUserNotFoundError(VoidAuthError):
    """Utilisateur non trouvé dans VoidAuth."""

    pass


class VoidAuthUserAlreadyExistsError(VoidAuthError):
    """L'utilisateur existe déjà dans VoidAuth."""

    pass


class VoidAuthValidationError(VoidAuthError):
    """Erreur de validation des données pour VoidAuth."""

    pass


class VoidAuthServerError(VoidAuthError):
    """Erreur du serveur VoidAuth."""

    pass


class VoidAuthTokenError(VoidAuthError):
    """Erreur liée aux tokens JWT de VoidAuth."""

    pass


class VoidAuthRateLimitExceededError(VoidAuthError):
    """Limite de taux d'appels API dépassée."""

    pass
