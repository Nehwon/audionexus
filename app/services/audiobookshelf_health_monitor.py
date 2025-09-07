"""
Service de monitoring de santé pour les instances Audiobookshelf.

Ce service surveille la santé des instances connectées, effectue des health checks
automatiques et collecte des métriques détaillées pour le monitoring.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.api.audiobookshelf import AudiobookshelfClient
from app.db.models.audiobookshelf_instance import AudiobookshelfInstance
from app.db.session import SessionLocal
from app.services.audiobookshelf_instance_service import AudiobookshelfInstanceService

logger = logging.getLogger(__name__)


@dataclass
class HealthMetrics:
    """Métriques de santé d'une instance."""

    instance_id: int
    instance_name: str
    status: str
    response_time_ms: int
    last_check: datetime
    consecutive_failures: int
    total_checks: int
    uptime_percentage: float
    version: Optional[str] = None
    libraries_count: int = 0
    audiobooks_count: int = 0


@dataclass
class SystemHealth:
    """État de santé global du système."""

    total_instances: int
    healthy_instances: int
    unhealthy_instances: int
    degraded_instances: int
    average_response_time: float
    overall_uptime_percentage: float
    last_updated: datetime


class AudiobookshelfHealthMonitor:
    """Monitor de santé pour les instances Audiobookshelf."""

    def __init__(self, db: Session = None, check_interval: int = 60):
        """Initialise le monitor de santé."""
        self.db = db or SessionLocal()
        self.instance_service = AudiobookshelfInstanceService(self.db)
        self.check_interval = check_interval  # Intervalle en secondes
        self._metrics: Dict[int, HealthMetrics] = {}
        self._last_system_health: Optional[SystemHealth] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def __del__(self):
        """Ferme la session de base de données."""
        if hasattr(self, "db") and self.db:
            self.db.close()

    async def start_monitoring(self):
        """Démarre le monitoring automatique."""
        if self._running:
            logger.warning("Le monitoring est déjà en cours")
            return

        self._running = True
        self._task = asyncio.create_task(self._monitoring_loop())
        logger.info(
            f"Monitoring de santé démarré avec intervalle de {self.check_interval}s"
        )

    async def stop_monitoring(self):
        """Arrête le monitoring automatique."""
        if not self._running:
            logger.warning("Le monitoring n'est pas en cours")
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Monitoring de santé arrêté")

    async def _monitoring_loop(self):
        """Boucle principale du monitoring."""
        while self._running:
            try:
                await self._perform_health_checks()
                await self._update_system_health()

                # Attendre l'intervalle configuré
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Erreur dans la boucle de monitoring: {str(e)}")
                await asyncio.sleep(
                    min(self.check_interval, 30)
                )  # Retry plus rapide en cas d'erreur

    async def _perform_health_checks(self):
        """Effectue les health checks pour toutes les instances."""
        instances = self.instance_service.get_instances(only_active=True)

        for instance in instances:
            try:
                metrics = await self._check_instance_health(instance)
                self._metrics[instance.id] = metrics

                # Mettre à jour la base de données
                await self._update_instance_health_in_db(instance.id, metrics)

            except Exception as e:
                logger.error(
                    f"Erreur lors du health check de {instance.name}: {str(e)}"
                )
                # Créer des métriques d'erreur
                error_metrics = HealthMetrics(
                    instance_id=instance.id,
                    instance_name=instance.name,
                    status="error",
                    response_time_ms=0,
                    last_check=datetime.utcnow(),
                    consecutive_failures=getattr(
                        self._metrics.get(instance.id), "consecutive_failures", 0
                    )
                    + 1,
                    total_checks=getattr(
                        self._metrics.get(instance.id), "total_checks", 0
                    )
                    + 1,
                    uptime_percentage=0.0,
                )
                self._metrics[instance.id] = error_metrics

    async def _check_instance_health(
        self, instance: AudiobookshelfInstance
    ) -> HealthMetrics:
        """
        Effectue un health check complet pour une instance.

        Args:
            instance: Instance à vérifier

        Returns:
            Métriques de santé
        """
        start_time = time.time()

        try:
            # Récupérer le token décrypté
            token = self.instance_service.get_decrypted_token(instance.id)
            if not token:
                raise Exception("Impossible de récupérer le token")

            # Créer le client
            client = AudiobookshelfClient(instance.base_url, token)

            # Test de connectivité basique
            client._make_request("GET", "/api/status")

            # Récupérer des informations supplémentaires
            libraries = client.get_libraries()
            libraries_count = len(libraries)

            # Calculer le temps de réponse
            response_time = int((time.time() - start_time) * 1000)

            # Récupérer les métriques existantes
            existing_metrics = self._metrics.get(instance.id)
            consecutive_failures = 0 if existing_metrics else 0
            total_checks = (
                (existing_metrics.total_checks + 1) if existing_metrics else 1
            )

            # Calculer le pourcentage de disponibilité
            uptime_percentage = self._calculate_uptime_percentage(
                instance.id, True, total_checks
            )

            return HealthMetrics(
                instance_id=instance.id,
                instance_name=instance.name,
                status="healthy",
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                consecutive_failures=consecutive_failures,
                total_checks=total_checks,
                uptime_percentage=uptime_percentage,
                version=instance.version,
                libraries_count=libraries_count,
                audiobooks_count=0,  # À calculer si nécessaire
            )

        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)

            # Récupérer les métriques existantes
            existing_metrics = self._metrics.get(instance.id)
            consecutive_failures = (
                (existing_metrics.consecutive_failures + 1) if existing_metrics else 1
            )
            total_checks = (
                (existing_metrics.total_checks + 1) if existing_metrics else 1
            )

            uptime_percentage = self._calculate_uptime_percentage(
                instance.id, False, total_checks
            )

            return HealthMetrics(
                instance_id=instance.id,
                instance_name=instance.name,
                status="unhealthy",
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                consecutive_failures=consecutive_failures,
                total_checks=total_checks,
                uptime_percentage=uptime_percentage,
            )

    def _calculate_uptime_percentage(
        self, instance_id: int, success: bool, total_checks: int
    ) -> float:
        """
        Calcule le pourcentage de disponibilité basé sur les checks passés.

        Args:
            instance_id: ID de l'instance
            success: Si le dernier check a réussi
            total_checks: Nombre total de checks

        Returns:
            Pourcentage de disponibilité
        """
        if total_checks == 0:
            return 100.0

        # Pour une estimation simple, on utilise les métriques récentes
        # Dans un vrai système, on stockerait plus d'historique
        base_uptime = self._metrics.get(instance_id)
        if not base_uptime:
            return 100.0 if success else 0.0

        # Calcul simple basé sur la tendance
        success_rate = (
            base_uptime.total_checks - base_uptime.consecutive_failures
        ) / base_uptime.total_checks
        return success_rate * 100.0

    async def _update_instance_health_in_db(
        self, instance_id: int, metrics: HealthMetrics
    ):
        """
        Met à jour les métriques de santé dans la base de données.

        Args:
            instance_id: ID de l'instance
            metrics: Métriques à mettre à jour
        """
        try:
            # Mettre à jour les métriques dans la base de données
            self.instance_service.update_connection_status(
                db=self.db,
                instance_id=instance_id,
                status=metrics.status,
                error=(
                    f"Response time: {metrics.response_time_ms}ms"
                    if metrics.status == "unhealthy"
                    else None
                ),
            )

            # Mettre à jour les compteurs spécifiques
            instance = self.instance_service.get_instance(instance_id)
            if instance:
                # Ici on pourrait ajouter des champs spécifiques pour stocker
                # response_time_ms, consecutive_failures, etc.
                pass

        except Exception as e:
            logger.error(
                f"Erreur lors de la mise à jour DB pour l'instance {instance_id}: {str(e)}"
            )

    async def _update_system_health(self):
        """Met à jour l'état de santé global du système."""
        if not self._metrics:
            return

        total_instances = len(self._metrics)
        healthy_count = sum(1 for m in self._metrics.values() if m.status == "healthy")
        unhealthy_count = sum(
            1 for m in self._metrics.values() if m.status == "unhealthy"
        )

        # Considérer dégradé si santé < 70%
        degraded_count = sum(
            1
            for m in self._metrics.values()
            if m.status == "healthy" and m.uptime_percentage < 70.0
        )

        avg_response_time = sum(
            m.response_time_ms for m in self._metrics.values()
        ) / max(total_instances, 1)

        # Calculer la disponibilité globale pondérée
        total_weighted_uptime = sum(m.uptime_percentage for m in self._metrics.values())
        overall_uptime = total_weighted_uptime / max(total_instances, 1)

        self._last_system_health = SystemHealth(
            total_instances=total_instances,
            healthy_instances=healthy_count,
            unhealthy_instances=unhealthy_count,
            degraded_instances=degraded_count,
            average_response_time=avg_response_time,
            overall_uptime_percentage=overall_uptime,
            last_updated=datetime.utcnow(),
        )

    def get_instance_health(self, instance_id: int) -> Optional[HealthMetrics]:
        """
        Retourne les métriques de santé d'une instance spécifique.

        Args:
            instance_id: ID de l'instance

        Returns:
            Métriques de santé ou None
        """
        return self._metrics.get(instance_id)

    def get_all_health_metrics(self) -> Dict[int, HealthMetrics]:
        """
        Retourne les métriques de santé de toutes les instances.

        Returns:
            Dict des métriques par instance
        """
        return self._metrics.copy()

    def get_system_health(self) -> Optional[SystemHealth]:
        """
        Retourne l'état de santé global du système.

        Returns:
            État de santé système ou None
        """
        return self._last_system_health

    async def force_health_check_all(self):
        """Force un health check immédiat pour toutes les instances."""
        logger.info("Health check forcé pour toutes les instances")
        await self._perform_health_checks()
        await self._update_system_health()

    def get_health_summary(self) -> Dict:
        """
        Retourne un résumé de santé pour le monitoring.

        Returns:
            Dict avec le résumé
        """
        system_health = self.get_system_health()
        if not system_health:
            return {
                "status": "unknown",
                "message": "Aucune donnée de santé disponible",
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Déterminer le statut global
        if system_health.unhealthy_instances > 0:
            status = "critical"
        elif system_health.degraded_instances > 0:
            status = "warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "total_instances": system_health.total_instances,
            "healthy_instances": system_health.healthy_instances,
            "unhealthy_instances": system_health.unhealthy_instances,
            "degraded_instances": system_health.degraded_instances,
            "average_response_time_ms": system_health.average_response_time,
            "overall_uptime_percentage": system_health.overall_uptime_percentage,
            "last_updated": system_health.last_updated.isoformat(),
            "instances": {
                metrics.instance_name: {
                    "status": metrics.status,
                    "response_time_ms": metrics.response_time_ms,
                    "uptime_percentage": metrics.uptime_percentage,
                    "consecutive_failures": metrics.consecutive_failures,
                }
                for metrics in self._metrics.values()
            },
        }
