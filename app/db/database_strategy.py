"""
Stratégie de base de données unifiée pour AudioNexus.

Implémente le pattern Strategy pour basculer entre SQLite (dev/tests) et MySQL (production).
Permet une migration sécurisée et unifiée des configurations.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.config import DatabaseType, settings

logger = logging.getLogger(__name__)


class DatabaseStrategy(ABC):
    """Interface abstraite pour les stratégies de base de données."""

    @abstractmethod
    def get_engine_config(self, database_uri: str) -> Dict[str, Any]:
        """Retourne la configuration du moteur pour ce type de base de données."""
        pass

    @abstractmethod
    def get_connection_string(self) -> str:
        """Retourne la chaîne de connexion pour ce type de base de données."""
        pass

    @abstractmethod
    def is_production_ready(self) -> bool:
        """Vérifie si cette stratégie est prête pour la production."""
        pass


class SQLiteStrategy(DatabaseStrategy):
    """Stratégie pour SQLite (développement et tests)."""

    def get_engine_config(self, database_uri: str) -> Dict[str, Any]:
        """Configuration du moteur pour SQLite."""
        connect_args = {"check_same_thread": False}
        pool_class = None

        # Configuration spécifique pour la mémoire (tests)
        if ":memory:" in database_uri:
            from sqlalchemy.pool import StaticPool
            pool_class = StaticPool

        config = {
            'database_uri': database_uri,
            'echo': settings.database.echo,
            'pool_pre_ping': True,
            'pool_recycle': settings.database.pool_recycle,
            'connect_args': connect_args,
        }

        if pool_class:
            config['poolclass'] = pool_class

        return config

    def get_connection_string(self) -> str:
        """Chaîne de connexion SQLite."""
        if settings.testing:
            return "sqlite+aiosqlite:///:memory:"
        return f"sqlite+aiosqlite:///{settings.database.sqlite_path}"

    def is_production_ready(self) -> bool:
        """SQLite n'est pas recommandé pour la production."""
        return False


class MySQLStrategy(DatabaseStrategy):
    """Stratégie pour MySQL (production)."""

    def get_engine_config(self, database_uri: str) -> Dict[str, Any]:
        """Configuration du moteur pour MySQL."""
        return {
            'database_uri': database_uri,
            'echo': settings.database.echo,
            'pool_pre_ping': True,
            'pool_recycle': settings.database.pool_recycle,
            'pool_size': settings.database.pool_size,
            'max_overflow': settings.database.max_overflow,
            'pool_timeout': settings.database.pool_timeout,
        }

    def get_connection_string(self) -> str:
        """Chaîne de connexion MySQL."""
        return f"mysql+aiomysql://{settings.database.user}:{settings.database.password}@{settings.database.host}:{settings.database.port or 3306}/{settings.database.name}"

    def is_production_ready(self) -> bool:
        """MySQL est prêt pour la production."""
        return True


class DatabaseStrategyFactory:
    """Factory pour créer les stratégies de base de données."""

    _strategies = {
        DatabaseType.SQLITE: SQLiteStrategy,
        DatabaseType.MYSQL: MySQLStrategy,
    }

    @classmethod
    def get_strategy(cls, db_type: DatabaseType) -> DatabaseStrategy:
        """Retourne la stratégie appropriée pour le type de base de données."""
        strategy_class = cls._strategies.get(db_type)
        if not strategy_class:
            raise ValueError(f"Stratégie non supportée pour le type: {db_type}")
        return strategy_class()

    @classmethod
    def get_current_strategy(cls) -> DatabaseStrategy:
        """Retourne la stratégie pour la configuration actuelle."""
        return cls.get_strategy(settings.database.type)


# Instance globale pour utilisation facile
current_strategy = DatabaseStrategyFactory.get_current_strategy()


def validate_database_configuration() -> bool:
    """Valide la configuration de base de données actuelle."""
    try:
        strategy = DatabaseStrategyFactory.get_current_strategy()
        uri = strategy.get_connection_string()

        # Vérifications basiques
        if not uri:
            logger.error("URI de base de données vide")
            return False

        # Vérification production
        if settings.is_production() and not strategy.is_production_ready():
            logger.warning("Configuration de base de données non optimale pour la production")
            # Ne bloque pas, mais log un avertissement

        logger.info(f"Configuration de base de données validée: {settings.database.type.value}")
        return True

    except Exception as e:
        logger.error(f"Erreur de validation de la configuration DB: {e}")
        return False


def get_migration_info() -> Dict[str, Any]:
    """Retourne les informations pour la migration entre bases de données."""
    return {
        'current_type': settings.database.type.value,
        'production_ready': current_strategy.is_production_ready(),
        'connection_string': current_strategy.get_connection_string(),
        'requires_migration': settings.database.type == DatabaseType.SQLITE and settings.is_production(),
    }