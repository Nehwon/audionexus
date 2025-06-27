"""
Configuration de la journalisation (logging) pour l'application AudioNexus.

Ce module configure la journalisation avec des formateurs personnalisés et des gestionnaires
pour la sortie console et les fichiers de logs.
"""
import logging
import sys
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from loguru import logger
from pydantic import BaseModel, Field, field_validator


class LoggingConfig(BaseModel):
    """Configuration de la journalisation pour l'application."""
    
    # Niveau de log par défaut
    level: str = Field("INFO", description="Niveau de journalisation global")
    
    # Format des logs
    format: str = Field(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level> | "
        "{extra}",
        description="Format des messages de log"
    )
    
    # Dossier des logs
    log_dir: str = Field("logs", description="Dossier de stockage des fichiers de log")
    
    # Fichier de log principal
    log_file: str = Field("audionexus.log", description="Nom du fichier de log principal")
    
    # Fichier de log d'erreurs
    error_log_file: str = Field("audionexus_error.log", description="Nom du fichier de log d'erreurs")
    
    # Niveau de log pour le fichier d'erreurs
    error_level: str = Field("ERROR", description="Niveau de journalisation pour le fichier d'erreurs")
    
    # Rotation des logs
    rotation: str = Field("10 MB", description="Taille maximale avant rotation des fichiers de log")
    retention: str = Field("30 days", description="Durée de conservation des fichiers de log")
    
    # Niveaux de log valides
    VALID_LOG_LEVELS = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
    
    @field_validator('level', 'error_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valide que le niveau de log est valide."""
        v_upper = v.upper()
        if v_upper not in cls.VALID_LOG_LEVELS:
            raise ValueError(f"Niveau de log invalide: {v}. Doit être l'un de: {', '.join(cls.VALID_LOG_LEVELS)}")
        return v_upper
    
    @property
    def log_file_path(self) -> Path:
        """Retourne le chemin complet vers le fichier de log principal."""
        log_dir = Path(self.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / self.log_file
    
    @property
    def error_log_file_path(self) -> Path:
        """Retourne le chemin complet vers le fichier de log d'erreurs."""
        log_dir = Path(self.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / self.error_log_file


def serialize(record: Dict[str, Any]) -> str:
    """Sérialise un enregistrement de log au format JSON."""
    subset = {
        "timestamp": record["time"].timestamp(),
        "level": record["level"].name,
        "message": record["message"],
        "name": record["name"],
        "function": record["function"],
        "line": record["line"],
    }
    
    # Ajoute les champs supplémentaires si présents
    if "extra" in record and record["extra"]:
        subset["extra"] = record["extra"]
    
    # Gestion des exceptions
    if "exception" in record and record["exception"]:
        subset["exception"] = str(record["exception"])
    
    return json.dumps(subset, ensure_ascii=False)


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """
    Configure la journalisation de l'application.
    
    Args:
        config: Configuration de la journalisation. Si None, utilise les valeurs par défaut.
    """
    if config is None:
        config = LoggingConfig()
    
    # Supprime les gestionnaires par défaut
    logger.remove()
    
    # Configuration du gestionnaire pour la console
    logger.add(
        sys.stderr,
        level=config.level,
        format=config.format,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # Configuration du gestionnaire pour le fichier de log principal
    logger.add(
        str(config.log_file_path),
        level=config.level,
        format=config.format,
        rotation=config.rotation,
        retention=config.retention,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        encoding="utf-8",
    )
    
    # Configuration du gestionnaire pour le fichier de log d'erreurs (format JSON)
    logger.add(
        str(config.error_log_file_path),
        level=config.error_level,
        format=serialize,
        rotation=config.rotation,
        retention=config.retention,
        enqueue=True,
        backtrace=True,
        diagnose=False,  # Désactivé pour éviter des informations sensibles dans les logs de production
        serialize=True,  # Active la sérialisation JSON
        encoding="utf-8",
    )
    
    # Configuration du niveau de log pour les bibliothèques tierces
    logging.getLogger("uvicorn").setLevel("WARNING")
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("sqlalchemy.engine").setLevel("WARNING")
    logging.getLogger("sqlalchemy.orm").setLevel("WARNING")
    logging.getLogger("passlib").setLevel("ERROR")
    
    logger.info("Journalisation configurée avec succès", extra={"log_file": str(config.log_file_path)})


# Configuration par défaut au chargement du module
setup_logging()

# Exporte le logger pour une utilisation dans toute l'application
logger = logger
