"""
Modèles de base de données pour l'audit trail et la conformité enterprise.
"""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.models.base import Base


class AuditLog(Base):
    """
    Modèle pour les logs d'audit des opérations de sécurité.
    Conforme aux standards de conformité enterprise (GDPR, SOX, etc.).
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Informations sur l'utilisateur
    user_id = Column(String(100), nullable=True, index=True)
    username = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=False)  # Support IPv4 et IPv6

    # Informations sur l'opération
    action = Column(String(100), nullable=False)  # login, logout, password_change, etc.
    resource = Column(String(100), nullable=False)  # auth, user, audiobook, etc.
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE

    # Données détaillées
    status_code = Column(Integer, nullable=True)
    user_agent = Column(Text, nullable=True)
    request_data = Column(
        JSON, nullable=True
    )  # Données de la requête (chiffrées si sensibles)
    response_data = Column(
        JSON, nullable=True
    )  # Données de la réponse (chiffrées si sensibles)

    # Métadonnées
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    duration_ms = Column(
        Integer, nullable=True
    )  # Durée de l'opération en millisecondes

    # Contexte de sécurité
    session_id = Column(String(100), nullable=True)
    csrf_token_used = Column(String(100), nullable=True)
    rate_limit_hit = Column(Integer, nullable=True)  # Nombre de hits rate limit

    # Classification
    severity = Column(String(20), default="info")  # info, warning, error, critical
    compliance_flags = Column(
        JSON, nullable=True
    )  # Flags pour conformité: gdpr, hipaa, sox, etc.

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user={self.username}, action={self.action}, timestamp={self.timestamp})>"


class ComplianceLog(Base):
    """
    Logs spécifiques pour les exigences de conformité.
    Utile pour les audits réglementaires.
    """

    __tablename__ = "compliance_logs"

    id = Column(Integer, primary_key=True, index=True)
    audit_log_id = Column(Integer, ForeignKey("audit_logs.id"), nullable=True)

    # Références réglementaires
    regulation = Column(String(50), nullable=False)  # gdpr, hipaa, sox, pci_dss
    requirement = Column(String(100), nullable=False)  # Article GDPR, section SOX, etc.

    # Classification du risque
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    data_classification = Column(
        String(50), nullable=True
    )  # public, internal, confidential, restricted

    # Mesures de conformité
    encryption_used = Column(String(50), nullable=True)  # aes256, rsa, none
    access_control = Column(
        String(100), nullable=True
    )  # role_based, attribute_based, etc.

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relation
    audit_log = relationship("AuditLog")

    def __repr__(self):
        return f"<ComplianceLog(id={self.id}, regulation={self.regulation}, risk_level={self.risk_level})>"


class SecurityEvent(Base):
    """
    Événements de sécurité critiques nécessitant une attention immédiate.
    """

    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)

    event_type = Column(
        String(100), nullable=False
    )  # brute_force, ddos, suspicious_activity, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical

    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)

    # Informations de contexte
    ip_address = Column(String(45), nullable=True)
    user_id = Column(String(100), nullable=True)
    username = Column(String(100), nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, type={self.event_type}, severity={self.severity})>"
