#!/usr/bin/env python3
"""
Script d'initialisation asynchrone de la base de données.

Ce script crée toutes les tables nécessaires dans la base de données SQLite
en utilisant des opérations asynchrones compatibles avec aiosqlite.
"""
import asyncio
import sys
import logging
import os
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def init_db():
    """Initialise la base de données de manière asynchrone."""
    # Import inside the function to avoid circular imports
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    from app.config import settings
    from app.db.models.base import Base
    
    try:
        logger.info("Création des tables de la base de données...")
        
        # Get database URL from settings
        database_uri = settings.DATABASE_URI or "sqlite+aiosqlite:///./audionexus.db"
        
        # Make sure the directory exists for SQLite
        if database_uri.startswith("sqlite") and not database_uri.startswith("sqlite:///:memory:"):
            db_path = database_uri.split("///")[-1]
            if not os.path.exists(os.path.dirname(db_path)) and os.path.dirname(db_path):
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create async engine directly
        engine = create_async_engine(
            database_uri,
            echo=True,
            future=True
        )
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Tables créées avec succès !")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}", exc_info=True)
        return False

async def drop_db():
    """Supprime toutes les tables de la base de données de manière asynchrone."""
    from app.db.database import Base, async_engine
    
    try:
        logger.warning("Suppression de toutes les tables de la base de données...")
        
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Tables supprimées avec succès !")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des tables: {e}", exc_info=True)
        return False

async def recreate_db():
    """Réinitialise complètement la base de données de manière asynchrone."""
    if await drop_db():
        return await init_db()
    return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestion de la base de données asynchrone")
    subparsers = parser.add_subparsers(dest='command', help='Commande à exécuter')
    
    # Commande init
    init_parser = subparsers.add_parser('init', help='Initialiser la base de données')
    
    # Commande drop
    drop_parser = subparsers.add_parser('drop', help='Supprimer toutes les tables')
    
    # Commande recreate
    recreate_parser = subparsers.add_parser('recreate', help='Réinitialiser la base de données')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        result = asyncio.run(init_db())
        sys.exit(0 if result else 1)
    elif args.command == 'drop':
        result = asyncio.run(drop_db())
        sys.exit(0 if result else 1)
    elif args.command == 'recreate':
        result = asyncio.run(recreate_db())
        sys.exit(0 if result else 1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
