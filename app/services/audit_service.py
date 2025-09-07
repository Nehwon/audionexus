"""
Service d'audit trail pour la conformité enterprise.
Gère la journalisation des opérations sécurisées et des événements de conformité.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.encryption import encrypt_data
from app.db.models.audit import AuditLog, ComplianceLog, SecurityEvent


class AuditService:
    """
    Service centralisé pour l'audit trail et la conformité enterprise.
    """

    @staticmethod
    async def log_security_event(
        db: Session,
        action: str,
        resource: str,
        method: str,
        ip_address: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        status_code: Optional[int] = None,
        user_agent: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        csrf_token_used: Optional[str] = None,
        duration_ms: Optional[int] = None,
        severity: str = "info",
        compliance_flags: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Log un événement de sécurité dans l'audit trail.

        Args:
            db: Session de base de données
            action: Action effectuée (login, logout, password_change, etc.)
            resource: Ressource concernée (auth, user, audiobook, etc.)
            method: Méthode HTTP (GET, POST, etc.)
            ip_address: Adresse IP du client
            user_id: ID de l'utilisateur (optionnel)
            username: Nom d'utilisateur (optionnel)
            status_code: Code de statut HTTP (optionnel)
            user_agent: User-Agent du client (optionnel)
            request_data: Données de la requête (optionnel)
            response_data: Données de la réponse (optionnel)
            session_id: ID de session (optionnel)
            csrf_token_used: Token CSRF utilisé (optionnel)
            duration_ms: Durée de l'opération en ms (optionnel)
            severity: Sévérité (info, warning, error, critical)
            compliance_flags: Flags de conformité (optionnel)

        Returns:
            AuditLog: L'instance de log créée
        """
        # Chiffrement des données sensibles
        encrypted_request = None
        if request_data:
            sensitive_fields = ["password", "token", "secret", "key"]
            encrypted_request = {}
            for key, value in request_data.items():
                if any(
                    field in key.lower() for field in sensitive_fields
                ) and isinstance(value, str):
                    encrypted_request[key] = encrypt_data(value)
                else:
                    encrypted_request[key] = value

        encrypted_response = None
        if response_data:
            encrypted_response = {}
            for key, value in response_data.items():
                if isinstance(value, str) and any(
                    field in key.lower() for field in ["token", "secret", "key"]
                ):
                    encrypted_response[key] = encrypt_data(value)
                else:
                    encrypted_response[key] = value

        # Création du log d'audit
        audit_log = AuditLog(
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            action=action,
            resource=resource,
            method=method,
            status_code=status_code,
            user_agent=user_agent,
            request_data=encrypted_request,
            response_data=encrypted_response,
            session_id=session_id,
            csrf_token_used=csrf_token_used,
            duration_ms=duration_ms,
            severity=severity,
            compliance_flags=compliance_flags,
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log

    @staticmethod
    async def log_compliance_event(
        db: Session,
        regulation: str,
        requirement: str,
        risk_level: str = "low",
        audit_log_id: Optional[int] = None,
        data_classification: Optional[str] = None,
        encryption_used: Optional[str] = None,
        access_control: Optional[str] = None,
    ) -> ComplianceLog:
        """
        Log un événement spécifique à la conformité réglementaire.

        Args:
            db: Session de base de données
            regulation: Réglementation (gdpr, hipaa, sox, pci_dss)
            requirement: Exigence spécifique (article, section, etc.)
            risk_level: Niveau de risque (low, medium, high, critical)
            audit_log_id: ID du log d'audit associé (optionnel)
            data_classification: Classification des données
            encryption_used: Type de chiffrement utilisé
            access_control: Type de contrôle d'accès

        Returns:
            ComplianceLog: L'instance de log de conformité créée
        """
        compliance_log = ComplianceLog(
            audit_log_id=audit_log_id,
            regulation=regulation,
            requirement=requirement,
            risk_level=risk_level,
            data_classification=data_classification,
            encryption_used=encryption_used,
            access_control=access_control,
        )

        db.add(compliance_log)
        db.commit()
        db.refresh(compliance_log)

        return compliance_log

    @staticmethod
    async def log_security_alert(
        db: Session,
        event_type: str,
        severity: str,
        description: str,
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> SecurityEvent:
        """
        Log un événement de sécurité critique nécessitant attention.

        Args:
            db: Session de base de données
            event_type: Type d'événement (brute_force, ddos, suspicious_activity, etc.)
            severity: Sévérité (low, medium, high, critical)
            description: Description de l'événement
            ip_address: Adresse IP impliquée (optionnel)
            user_id: ID utilisateur impliqué (optionnel)
            username: Nom d'utilisateur impliqué (optionnel)
            details: Détails supplémentaires (optionnel)

        Returns:
            SecurityEvent: L'instance d'événement de sécurité créée
        """
        security_event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_id=user_id,
            username=username,
            details=details,
        )

        db.add(security_event)
        db.commit()
        db.refresh(security_event)

        return security_event

    @staticmethod
    def get_compliance_flags(action: str, resource: str, method: str) -> Dict[str, Any]:
        """
        Détermine les flags de conformité applicables selon l'action.

        Args:
            action: Action effectuée
            resource: Ressource concernée
            method: Méthode HTTP

        Returns:
            Dict: Flags de conformité
        """
        flags = {
            "gdpr": False,
            "ccpa": False,
            "hipaa": False,
            "sox": False,
            "pci_dss": False,
        }

        # Authentification - GDPR et SOX
        if resource == "auth" and action in ["login", "register", "password_change"]:
            flags["gdpr"] = True
            flags["sox"] = True

        # Données personnelles - GDPR
        if resource in ["user", "profile"] and method in ["PUT", "DELETE"]:
            flags["gdpr"] = True
            flags["ccpa"] = True

        # Données de santé - HIPAA
        if resource == "health" or "medical" in str(action).lower():
            flags["hipaa"] = True

        return flags


# Instance globale du service d'audit
audit_service = AuditService()
