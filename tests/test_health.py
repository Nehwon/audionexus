"""
Tests pour l'endpoint de santé de l'API.
"""
import pytest
from flask import url_for


def test_health_endpoint(client):
    """Teste que l'endpoint de santé renvoie une réponse valide."""
    # Act
    response = client.get("/health")
    
    # Assert
    assert response.status_code == 200
    assert response.is_json
    assert "status" in response.json
    assert response.json["status"] == "ok"
    assert "version" in response.json
    assert "timestamp" in response.json


def test_health_endpoint_headers(client):
    """Teste les en-têtes de la réponse de l'endpoint de santé."""
    # Act
    response = client.get("/health")
    
    # Assert
    assert "Content-Type" in response.headers
    assert response.headers["Content-Type"] == "application/json"
    assert "Cache-Control" in response.headers
    assert "no-cache" in response.headers["Cache-Control"]


@pytest.mark.integration
def test_health_with_database(client, db_session):
    """Teste que l'endpoint de santé vérifie la connexion à la base de données."""
    # Act
    response = client.get("/health?check_db=true")
    
    # Assert
    assert response.status_code == 200
    assert response.is_json
    assert "database" in response.json
    assert response.json["database"] == "ok"
