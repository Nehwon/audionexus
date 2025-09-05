"""
Pattern Strategy pour la gestion des différentes bases de données.
Permet le basculement transparent entre MySQL et SQLite selon la configuration.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.engine import Engine

from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseStrategy(ABC):
    """Interface abstraite pour les stratégies de base de données."""

    @abstractmethod
    def get_connection_params(self, database_uri: str, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """Retourne les paramètres de connexion spécifiques à la base de données."""
        pass

    @abstractmethod
    def get_engine_kwargs(self, database_uri: str) -> Dict[str, Any]:
        """Retourne les paramètres spécifiques pour la création du moteur."""
        pass


class SQLiteStrategy(DatabaseStrategy):
    """Stratégie pour les bases de données SQLite."""

    def get_connection_params(self, database_uri: str, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """Retourne les paramètres de connexion pour SQLite."""
        params = base_params.copy()
        params.update({
            'connect_args': {'check_same_thread': False},
        })

        # Pour les tests en mémoire ou les bases de données temporaires
        if ':memory:' in database_uri or database_uri.endswith('.db'):
            params['poolclass'] = StaticPool

        return params

    def get_engine_kwargs(self, database_uri: str) -> Dict[str, Any]:
        """Retourne les paramètres pour SQLite."""
        return {
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'echo': settings.debug if hasattr(settings, 'debug') else False,
        }


class MySQLStrategy(DatabaseStrategy):
    """Stratégie pour les bases de données MySQL."""

    def get_connection_params(self, database_uri: str, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """Retourne les paramètres de connexion pour MySQL."""
        params = base_params.copy()
        params.update({
            'pool_size': getattr(settings.database, 'pool_size', 5),
            'max_overflow': getattr(settings.database, 'max_overflow', 10),
            'pool_timeout': getattr(settings.database, 'pool_timeout', 30),
            'pool_recycle': 3600,
            'connect_args': {
                'connect_timeout': 10,
                'charset': 'utf8mb4',
            }
        })
        return params

    def get_engine_kwargs(self, database_uri: str) -> Dict[str, Any]:
        """Retourne les paramètres pour MySQL."""
        return {
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'echo': settings.debug if hasattr(settings, 'debug') else False,
        }


class DatabaseStrategyFactory:
    """Factory pour créer les stratégies de base de données."""

    _strategies = {
        'sqlite': SQLiteStrategy,
        'mysql': MySQLStrategy,
    }

    @classmethod
    def get_strategy(cls, database_uri: str) -> DatabaseStrategy:
        """
        Retourne la stratégie appropriée selon l'URI de la base de données.

        Args:
            database_uri: URI de connexion à la base de données

        Returns:
            DatabaseStrategy: Instance de la stratégie appropriée

        Raises:
            ValueError: Si le type de base de données n'est pas supporté
        """
        if database_uri.startswith('sqlite'):
            return cls._strategies['sqlite']()
        elif 'mysql' in database_uri:
            return cls._strategies['mysql']()
        else:
            raise ValueError(f"Type de base de données non supporté pour l'URI: {database_uri}")


class UnifiedDatabaseManager:
    """Gestionnaire unifié des connexions de base de données."""

    def __init__(self):
        self._engine: Optional[Engine] = None
        self._strategy: Optional[DatabaseStrategy] = None

    def initialize_engine(self, database_uri: str = None) -> Engine:
        """
        Initialise le moteur de base de données avec la stratégie appropriée.

        Args:
            database_uri: URI de la base de données (optionnel, utilise settings sinon)

        Returns:
            Engine: Le moteur SQLAlchemy configuré
        """
        if database_uri is None:
            database_uri = settings.get_database_uri()

        logger.info(f"Initialisation du moteur avec stratégie pour: {database_uri}")

        # Créer la stratégie appropriée
        self._strategy = DatabaseStrategyFactory.get_strategy(database_uri)

        # Obtenir les paramètres de base et spécifiques
        base_params = self._strategy.get_engine_kwargs(database_uri)
        connection_params = self._strategy.get_connection_params(database_uri, base_params)

        # Créer le moteur
        self._engine = create_engine(database_uri, **connection_params)

        logger.info("✅ Moteur de base de données initialisé avec succès")
        return self._engine

    @property
    def engine(self) -> Engine:
        """Retourne le moteur de base de données (l'initialise si nécessaire)."""
        if self._engine is None:
            self.initialize_engine()
        return self._engine

    @property
    def strategy(self) -> DatabaseStrategy:
        """Retourne la stratégie actuelle."""
        return self._strategy


# Instance globale du gestionnaire unifié
database_manager = UnifiedDatabaseManager()