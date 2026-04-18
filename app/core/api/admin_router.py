"""
Routeur API pour les fonctionnalités administrateur.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.models import Audiobook, AudiobookProgress, Book, Library, User
from app.db.session import get_db

router = APIRouter()


@router.get("/metrics")
async def get_admin_metrics(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Récupère toutes les métriques administrateur."""

    # TODO: Ajouter vérification admin basée sur is_superuser
    # if not current_user.is_superuser:
    #     raise HTTPException(status_code=403, detail="Accès administrateur requis")

    # Utilisateurs
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    superusers = (
        db.query(func.count(User.id)).filter(User.is_superuser == True).scalar()
    )

    # Audiobooks locaux et synchronisés
    total_audiobookshelf_books = db.query(func.count(Audiobook.id)).scalar()
    total_local_books = db.query(func.count(Book.id)).scalar()
    total_books = total_audiobookshelf_books + total_local_books

    # Progression d'écoute
    total_progress_entries = db.query(func.count(AudiobookProgress.id)).scalar()
    finished_books = (
        db.query(func.count(AudiobookProgress.id))
        .filter(AudiobookProgress.is_finished == True)
        .scalar()
    )

    # Stockage
    total_audiobookshelf_storage = db.query(func.sum(Audiobook.file_size)).scalar() or 0
    total_local_storage = db.query(func.sum(Book.size)).scalar() or 0
    total_storage = total_audiobookshelf_storage + total_local_storage

    # Collections/Bibliothèques
    unique_libraries_audiobookshelf = db.query(
        func.count(func.distinct(Audiobook.library_id))
    ).scalar()
    unique_libraries_local = db.query(func.count(func.distinct(Library.id))).scalar()
    total_libraries = max(
        unique_libraries_audiobookshelf, unique_libraries_local
    )  # Approximation

    # Utilisation récente (derniers 30 jours)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_users = (
        db.query(func.count(User.id)).filter(User.last_seen >= thirty_days_ago).scalar()
    )
    recent_progress = (
        db.query(func.count(AudiobookProgress.id))
        .filter(AudiobookProgress.updated_at >= thirty_days_ago)
        .scalar()
    )

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "superusers": superusers,
            "recent": recent_users,
        },
        "books": {
            "total": total_books,
            "audiobookshelf": total_audiobookshelf_books,
            "local": total_local_books,
            "finished": finished_books,
        },
        "usage": {
            "total_progress": total_progress_entries,
            "recent_activity": recent_progress,
        },
        "storage": {
            "total": total_storage,
            "audiobookshelf": total_audiobookshelf_storage,
            "local": total_local_storage,
        },
        "collections": {"total_libraries": total_libraries},
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/trends")
async def get_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Récupère les données de tendance sur les derniers jours."""

    # Données simplifiées pour les tendances (à étendre avec historique réel)
    trends = []
    base_date = datetime.utcnow() - timedelta(days=days)

    for i in range(days):
        date = base_date + timedelta(days=i)
        next_date = date + timedelta(days=1)

        # Comptages par jour (simulation - à remplacer par vraies données historiques)
        daily_users = (
            db.query(func.count(User.id)).filter(User.created_at <= next_date).scalar()
        )
        daily_books = (
            db.query(func.count(Book.id)).filter(Book.created_at <= next_date).scalar()
            + db.query(func.count(Audiobook.id))
            .filter(Audiobook.created_at <= next_date)
            .scalar()
        )

        trends.append(
            {
                "date": date.date().isoformat(),
                "users": daily_users,
                "books": daily_books,
                "storage": 0,  # À implémenter avec historique
            }
        )

    return trends


@router.get("/upload-tasks")
async def get_upload_tasks(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Récupère les tâches d'upload en cours."""

    # TODO: Implémenter récupération de vraies tâches d'upload
    # Pour l'instant, retourner des tâches simulées
    tasks = [
        {
            "id": "1",
            "filename": "livres_audio.zip",
            "status": "processing",
            "progress": 65,
            "total_files": 10,
            "processed_files": 6,
            "created_at": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(minutes=3)).isoformat(),
        },
        {
            "id": "2",
            "filename": "romans_historiques.rar",
            "status": "extracting",
            "progress": 30,
            "total_files": 15,
            "processed_files": 4,
            "created_at": (datetime.utcnow() - timedelta(minutes=8)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(minutes=2)).isoformat(),
        },
    ]

    return tasks


@router.get("/health")
async def get_system_health(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Vérifie la santé du système."""
    try:
        # Test connexion DB
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "error"

    return {"database": db_status, "timestamp": datetime.utcnow().isoformat()}


@router.get("/notifications")
async def get_notifications(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Récupère les notifications système."""

    # Notifications simulées - à étendre avec vrai système de notifications
    notifications = [
        {
            "id": "1",
            "type": "info",
            "title": "Synchronisation terminée",
            "message": "La synchronisation avec l'instance Audiobookshelf a été effectuée avec succès.",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "read": False,
        },
        {
            "id": "2",
            "type": "warning",
            "title": "Stockage élevé",
            "message": "Le stockage utilisé dépasse 80% de la capacité.",
            "timestamp": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
            "read": True,
        },
    ]

    return notifications
