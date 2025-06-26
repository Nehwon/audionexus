#!/bin/bash

# Nettoyer les variables d'environnement problématiques
echo "Nettoyage des variables d'environnement problématiques..."
unset ACCESS_TOKEN_EXPIRE_MINUTES

# Exporter les variables nécessaires pour les tests
export TESTING="1"
export DATABASE_URI="sqlite+aiosqlite:///:memory:"

# Exécuter les tests avec pytest
echo "Lancement des tests..."
python -m pytest -xvs app/tests/

# Code de sortie
TEST_EXIT_CODE=$?
echo "Tests terminés avec le code de sortie: $TEST_EXIT_CODE"
exit $TEST_EXIT_CODE
