#!/usr/bin/env python3
"""
Script d'initialisation de la base de données.

Ce script crée toutes les tables nécessaires dans la base de données
en fonction des modèles SQLAlchemy définis dans l'application.
"""
import sys
import logging
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def init_db():
    """Initialise la base de données en créant toutes les tables."""
    from app.db.database import Base, engine
    from app.db.models.audiobook import Audiobook, AudiobookProgress
    
    try:
        logger.info("Création des tables de la base de données...")
        
        # Créer toutes les tables définies dans les modèles
        Base.metadata.create_all(bind=engine)
        
        logger.info("Tables créées avec succès !")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}", exc_info=True)
        return False

def drop_db():
    """Supprime toutes les tables de la base de données."""
    from app.db.database import Base, engine
    
    try:
        logger.warning("Suppression de toutes les tables de la base de données...")
        
        # Supprimer toutes les tables
        Base.metadata.drop_all(bind=engine)
        
        logger.info("Tables supprimées avec succès !")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des tables: {e}", exc_info=True)
        return False

def recreate_db():
    """Réinitialise complètement la base de données."""
    if drop_db():
        return init_db()
    return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestion de la base de données")
    subparsers = parser.add_subparsers(dest='command', help='Commande à exécuter')
    
    # Commande init
    init_parser = subparsers.add_parser('init', help='Initialiser la base de données')
    
    # Commande drop
    drop_parser = subparsers.add_parser('drop', help='Supprimer toutes les tables')
    
    # Commande recreate
    recreate_parser = subparsers.add_parser('recreate', help='Réinitialiser la base de données')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        sys.exit(0 if init_db() else 1)
    elif args.command == 'drop':
        sys.exit(0 if drop_db() else 1)
    elif args.command == 'recreate':
        sys.exit(0 if recreate_db() else 1)
    else:
        parser.print_help()
        sys.exit(1)
