"""
Configuration spécifique pour les tests unitaires.
Ce fichier crée une configuration de test qui ignore complètement les variables d'environnement système.
"""
import os
from typing import Dict, Any
from pydantic import Field, ConfigDict
from pydantic_settings import SettingsConfigDict
from app.config import Settings as BaseSettings

# Configuration pour les tests qui ignore les variables d'environnement système
class _TestSettings(BaseSettings):
    # Configuration de base pour les tests
    DEBUG: bool = True
    TESTING: bool = True
    
    # Configuration de la base de données
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_USER: str = "testuser"
    DB_PASSWORD: str = "testpass"
    DB_NAME: str = "testdb"
    DATABASE_URI: str = "sqlite+aiosqlite:///:memory:"  # Utilisation de SQLite en mémoire pour les tests
    
    # Configuration JWT
    JWT_SECRET: str = "test-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1h pour les tests
    
    # Configuration Pydantic v2
    model_config = SettingsConfigDict(
        # Ignorer les variables d'environnement
        env_file=None,
        env_file_encoding=None,
        env_nested_delimiter=None,
        
        # Désactiver le chargement des fichiers .env
        env_prefix="",
        case_sensitive=True,
        
        # Désactiver le chargement des variables d'environnement
        env_ignore_empty=True,
        
        # Configuration personnalisée des sources
        env_customise_sources=lambda *args, **kwargs: (
            args[0],  # init_settings
            args[2],  # file_secret_settings
        )
    )

# Créer une instance de la configuration de test
test_settings = _TestSettings()

def apply_test_settings() -> None:
    """
    Applique les paramètres de test à l'application.
    
    Cette fonction configure l'application pour utiliser une base de données SQLite en mémoire
    lors des tests, indépendamment de la configuration de l'environnement.
    """
    import sys
    import os
    import importlib
    
    # Forcer l'utilisation de SQLite en mémoire pour les tests
    os.environ["TESTING"] = "true"
    
    # Remplacer la configuration dans le module app.config
    import app.config as config_module
    config_module.settings = test_settings
    
    # Recharger les modules qui dépendent de la configuration
    modules_to_reload = [
        'app.core.security',
        'app.api.deps',
        'app.db.session',
        'app.db.database',
        'app.db.session_manager',
    ]
    
    # Recharger les modules pour s'assurer qu'ils utilisent la nouvelle configuration
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
    
    # S'assurer que la configuration de test est bien appliquée
    assert "sqlite" in test_settings.DATABASE_URI, "La base de données de test doit utiliser SQLite"

# Appliquer les paramètres de test lors de l'importation
apply_test_settings()
