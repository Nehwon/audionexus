#!/usr/bin/env python3
"""
Script CLI pour la synchronisation avec Audiobookshelf.

Ce script permet de lancer manuellement des synchronisations avec Audiobookshelf
ot de configurer une tâche planifiée.
"""
import argparse
import logging
import sys
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import SessionLocal
from app.services.audiobookshelf_sync import AudiobookshelfSyncService

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Synchronisation avec Audiobookshelf")

    # Arguments principaux
    parser.add_argument(
        "--full",
        action="store_true",
        help="Effectue une synchronisation complète (même les éléments non modifiés)",
    )

    # Options de filtrage
    parser.add_argument(
        "--libraries",
        nargs="+",
        help="Liste des IDs de bibliothèques à synchroniser (toutes par défaut)",
    )

    # Options de sortie
    parser.add_argument(
        "--quiet", action="store_true", help="Réduit la verbosité des logs"
    )

    # Mode démon
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Lance le service en mode démon avec synchronisation périodique",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Intervalle de synchronisation en secondes (défaut: 3600)",
    )

    return parser.parse_args()


def run_sync(db: Session, full: bool = False, library_ids: list = None):
    """
    Exécute une synchronisation avec Audiobookshelf.

    Args:
        db: Session de base de données
        full: Si True, force une synchronisation complète
        library_ids: Liste des IDs de bibliothèques à synchroniser (toutes si None)

    Returns:
        dict: Statistiques de la synchronisation
    """
    logger.info("Démarrage de la synchronisation avec Audiobookshelf...")
    start_time = datetime.now()

    try:
        # Initialiser le service de synchronisation
        sync_service = AudiobookshelfSyncService(db=db)

        # Exécuter la synchronisation
        stats = sync_service.sync_all(full_sync=full)

        # Calculer la durée
        duration = (datetime.now() - start_time).total_seconds()

        # Journaliser les résultats
        logger.info(
            "Synchronisation terminée en %.2f secondes. "
            "Bibliothèques: %d, Livres: %d, Progression: %d, Erreurs: %d",
            duration,
            stats.get("libraries_synced", 0),
            stats.get("audiobooks_synced", 0),
            stats.get("progress_updated", 0),
            stats.get("errors", 0),
        )

        return stats

    except Exception as e:
        logger.error("Erreur lors de la synchronisation: %s", str(e), exc_info=True)
        raise


def run_daemon(db: Session, interval: int = 3600, full_first: bool = False):
    """
    Lance le service de synchronisation en mode démon.

    Args:
        db: Session de base de données
        interval: Intervalle entre les synchronisations en secondes
        full_first: Si True, effectue une synchronisation complète au démarrage
    """
    import time
    from threading import Event

    logger.info("Démarrage du service de synchronisation (intervalle: %ds)", interval)

    if full_first:
        logger.info("Première synchronisation complète...")
        run_sync(db, full=True)

    # Boucle principale
    stop_event = Event()
    try:
        while not stop_event.is_set():
            next_run = datetime.now().timestamp() + interval

            # Attendre jusqu'au prochain cycle
            while datetime.now().timestamp() < next_run and not stop_event.is_set():
                time.sleep(1)

            if not stop_event.is_set():
                logger.info("Démarrage d'une synchronisation planifiée...")
                run_sync(db, full=False)

    except KeyboardInterrupt:
        logger.info("Arrêt du service de synchronisation...")
    except Exception as e:
        logger.error(
            "Erreur dans le service de synchronisation: %s", str(e), exc_info=True
        )
    finally:
        db.close()


def main():
    """Fonction principale."""
    args = parse_args()

    # Ajuster le niveau de log
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Initialiser la session de base de données
    db = SessionLocal()

    try:
        # Exécuter en mode démon ou une seule fois
        if args.daemon:
            run_daemon(db, interval=args.interval, full_first=args.full)
        else:
            run_sync(db, full=args.full, library_ids=args.libraries)
    finally:
        db.close()


if __name__ == "__main__":
    main()
