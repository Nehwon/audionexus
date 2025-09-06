"""
Service de load balancing intelligent pour les instances Audiobookshelf.

Ce service distribue intelligemment les requêtes entre plusieurs instances
en fonction de leur santé, charge actuelle et priorité configurée.
"""
import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.audiobookshelf_instance_service import AudiobookshelfInstanceService
from app.db.session import SessionLocal
from app.db.models.audiobookshelf_instance import AudiobookshelfInstance

logger = logging.getLogger(__name__)


@dataclass
class LoadBalancerMetrics:
    """Métriques de load balancing pour une instance."""
    instance_id: int
    active_requests: int
    total_requests: int
    error_rate: float
    avg_response_time: float
    last_used: datetime
    score: float


class AudiobookshelfLoadBalancer:
    """Load balancer intelligent pour les instances Audiobookshelf."""

    def __init__(self, db: Session = None):
        """Initialise le load balancer."""
        self.db = db or SessionLocal()
        self.instance_service = AudiobookshelfInstanceService(self.db)
        self._metrics: Dict[int, LoadBalancerMetrics] = {}
        self._lock = asyncio.Lock()
        self._last_cleanup = datetime.utcnow()

    def __del__(self):
        """Ferme la session de base de données."""
        if hasattr(self, 'db') and self.db:
            self.db.close()

    async def get_best_instance(self, operation_type: str = "read") -> Optional[AudiobookshelfInstance]:
        """
        Sélectionne la meilleure instance disponible pour une opération.

        Args:
            operation_type: Type d'opération (read/write/admin)

        Returns:
            Instance sélectionnée ou None si aucune disponible
        """
        async with self._lock:
            await self._cleanup_metrics_if_needed()

            candidates = self._get_eligible_instances(operation_type)
            if not candidates:
                logger.warning(f"Aucune instance éligible trouvée pour {operation_type}")
                return None

            scored_candidates = []
            for instance in candidates:
                score = self._calculate_instance_score(instance, operation_type)
                scored_candidates.append((instance, score))

            # Trier par score décroissant (meilleur en premier)
            scored_candidates.sort(key=lambda x: x[1], reverse=True)

            selected_instance = scored_candidates[0][0]

            # Mettre à jour les métriques
            await self._update_metrics_on_selection(selected_instance.id)

            logger.debug(f"Instance sélectionnée pour {operation_type}: {selected_instance.name} (score: {scored_candidates[0][1]:.3f})")
            return selected_instance

    def _get_eligible_instances(self, operation_type: str) -> List[AudiobookshelfInstance]:
        """
        Récupère les instances éligibles pour une opération donnée.

        Args:
            operation_type: Type d'opération

        Returns:
            Liste des instances éligibles
        """
        all_instances = self.instance_service.get_instances(only_active=True, only_sync_enabled=True)

        eligible = []
        for instance in all_instances:
            if self._is_instance_eligible(instance, operation_type):
                eligible.append(instance)

        return eligible

    def _is_instance_eligible(self, instance: AudiobookshelfInstance, operation_type: str) -> bool:
        """
        Vérifie si une instance est éligible pour une opération.

        Args:
            instance: Instance à vérifier
            operation_type: Type d'opération

        Returns:
            True si éligible
        """
        # Vérifications de base
        if not instance.is_active or not instance.sync_enabled:
            return False

        # Vérification du statut
        if instance.status not in ["active", "healthy"]:
            return False

        # Vérification des health checks récents
        if instance.health_check_timestamp:
            health_age = (datetime.utcnow() - instance.health_check_timestamp).total_seconds()
            if health_age > 300:  # 5 minutes
                return False

        # Pour les écritures, vérifier que l'instance est considérée comme saine
        if operation_type in ["write", "admin"]:
            if instance.get_health_score() < 0.7:  # Seuil plus strict pour écritures
                return False

        # Vérifications des métriques de charge
        metrics = self._metrics.get(instance.id)
        if metrics:
            # Limiter les requêtes actives pour éviter la surcharge
            if metrics.active_requests > 10:
                return False

            # Vérifier le taux d'erreur
            if metrics.error_rate > 0.1:  # > 10% d'erreurs
                return False

        return True

    def _calculate_instance_score(self, instance: AudiobookshelfInstance, operation_type: str) -> float:
        """
        Calcule un score pour une instance basé sur divers critères.

        Args:
            instance: Instance à scorer
            operation_type: Type d'opération

        Returns:
            Score entre 0.0 et 1.0
        """
        score = 0.0

        # Score de santé (pondération élevée)
        health_score = instance.get_health_score()
        score += health_score * 0.4

        # Score de priorité (inversé : priorité basse = score élevé)
        priority_score = 1.0 - (instance.priority - 1) / 10.0  # Normalisé 0-1
        score += priority_score * 0.2

        # Score de charge (moins de charge = score plus élevé)
        load_score = self._calculate_load_score(instance.id)
        score += load_score * 0.2

        # Score de performance (temps de réponse plus bas = score plus élevé)
        performance_score = self._calculate_performance_score(instance)
        score += performance_score * 0.2

        return min(1.0, max(0.0, score))

    def _calculate_load_score(self, instance_id: int) -> float:
        """
        Calcule le score de charge d'une instance.

        Returns:
            Score entre 0.0 (surchargé) et 1.0 (libre)
        """
        metrics = self._metrics.get(instance_id)
        if not metrics:
            return 1.0  # Pas de métriques = considéré comme libre

        # Score basé sur les requêtes actives (inversé)
        active_penalty = min(metrics.active_requests / 5.0, 1.0)  # Pénalité max à 5 requêtes actives
        return 1.0 - active_penalty

    def _calculate_performance_score(self, instance: AudiobookshelfInstance) -> float:
        """
        Calcule le score de performance basé sur le temps de réponse.

        Returns:
            Score entre 0.0 et 1.0
        """
        if not instance.response_time_ms:
            return 0.5  # Score neutre si pas de données

        # Score inversément proportionnel au temps de réponse
        # 500ms = score 1.0, 5000ms = score 0.0
        response_time = instance.response_time_ms
        if response_time <= 500:
            return 1.0
        elif response_time >= 5000:
            return 0.0
        else:
            return 1.0 - (response_time - 500) / 4500

    async def _update_metrics_on_selection(self, instance_id: int):
        """
        Met à jour les métriques lors de la sélection d'une instance.

        Args:
            instance_id: ID de l'instance sélectionnée
        """
        if instance_id not in self._metrics:
            self._metrics[instance_id] = LoadBalancerMetrics(
                instance_id=instance_id,
                active_requests=0,
                total_requests=0,
                error_rate=0.0,
                avg_response_time=0,
                last_used=datetime.utcnow(),
                score=0.0
            )

        metrics = self._metrics[instance_id]
        metrics.last_used = datetime.utcnow()

    async def record_request_start(self, instance_id: int):
        """
        Enregistre le début d'une requête pour une instance.

        Args:
            instance_id: ID de l'instance
        """
        async with self._lock:
            if instance_id not in self._metrics:
                self._metrics[instance_id] = LoadBalancerMetrics(
                    instance_id=instance_id,
                    active_requests=0,
                    total_requests=0,
                    error_rate=0.0,
                    avg_response_time=0,
                    last_used=datetime.utcnow(),
                    score=0.0
                )

            self._metrics[instance_id].active_requests += 1

    async def record_request_end(self, instance_id: int, response_time_ms: int, success: bool):
        """
        Enregistre la fin d'une requête pour une instance.

        Args:
            instance_id: ID de l'instance
            response_time_ms: Temps de réponse en millisecondes
            success: Si la requête a réussi
        """
        async with self._lock:
            if instance_id not in self._metrics:
                return

            metrics = self._metrics[instance_id]
            metrics.active_requests = max(0, metrics.active_requests - 1)
            metrics.total_requests += 1

            # Mise à jour du temps de réponse moyen (moyenne mobile)
            if metrics.avg_response_time == 0:
                metrics.avg_response_time = response_time_ms
            else:
                metrics.avg_response_time = (metrics.avg_response_time + response_time_ms) / 2

            # Mise à jour du taux d'erreur
            if not success:
                # Approximation simple du taux d'erreur
                metrics.error_rate = (metrics.error_rate + 1) / metrics.total_requests
            else:
                metrics.error_rate = metrics.error_rate * 0.99  # Decay progressif

    async def _cleanup_metrics_if_needed(self):
        """
        Nettoie les métriques obsolètes si nécessaire.
        """
        now = datetime.utcnow()
        if (now - self._last_cleanup).total_seconds() > 300:  # Toutes les 5 minutes
            await self._cleanup_old_metrics()
            self._last_cleanup = now

    async def _cleanup_old_metrics(self):
        """
        Supprime les métriques anciennes et inutilisées.
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        to_remove = []

        for instance_id, metrics in self._metrics.items():
            if metrics.last_used < cutoff_time and metrics.active_requests == 0:
                to_remove.append(instance_id)

        for instance_id in to_remove:
            del self._metrics[instance_id]

        if to_remove:
            logger.debug(f"Nettoyé {len(to_remove)} métriques obsolètes")

    def get_load_distribution(self) -> Dict[str, any]:
        """
        Retourne la distribution de charge actuelle.

        Returns:
            Dict avec les statistiques de distribution
        """
        total_active = sum(m.active_requests for m in self._metrics.values())
        total_requests = sum(m.total_requests for m in self._metrics.values())

        instance_stats = {}
        for instance_id, metrics in self._metrics.items():
            instance = self.instance_service.get_instance(instance_id)
            if instance:
                instance_stats[instance.name] = {
                    "active_requests": metrics.active_requests,
                    "total_requests": metrics.total_requests,
                    "error_rate": metrics.error_rate,
                    "avg_response_time": metrics.avg_response_time,
                    "load_percentage": (metrics.active_requests / max(total_active, 1)) * 100
                }

        return {
            "total_active_requests": total_active,
            "total_requests": total_requests,
            "instances": instance_stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def force_refresh_health_checks(self):
        """
        Force un rafraîchissement des health checks pour toutes les instances.
        """
        logger.info("Début du rafraîchissement forcé des health checks")
        instances = self.instance_service.get_instances(only_active=True)

        for instance in instances:
            try:
                result = self.instance_service.test_connection(instance.id)
                logger.debug(f"Health check pour {instance.name}: {result}")
            except Exception as e:
                logger.error(f"Erreur lors du health check de {instance.name}: {str(e)}")

        logger.info("Rafraîchissement des health checks terminé")