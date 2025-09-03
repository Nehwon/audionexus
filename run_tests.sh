#!/bin/bash

# Script de lancement automatique des tests AudioNexus
# Utilise maintenant le système de configuration unifié

set -e

# Couleurs pour les messages
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Configuration automatique pour les tests
log_info "Configuration automatique des tests avec SQLite en mémoire..."
export TESTING="true"
export ENVIRONMENT="testing"

# Configuration de la base de données de test
export DB_TYPE="sqlite"
export SQLITE_PATH=":memory:"
export SECRET_KEY="test-secret-key"
export JWT_SECRET="test-jwt-secret"

# Désactiver les avertissements de SQLAlchemy pendant les tests
export SQLALCHEMY_SILENCE_UBER_WARNING="1"

# Vérifier si nous sommes dans le bon répertoire
if [[ ! -f "pyproject.toml" ]]; then
    log_error "Erreur: pyproject.toml introuvable. Assurez-vous d'être à la racine du projet AudioNexus."
    exit 1
fi

# Créer les dossiers nécessaires s'ils n'existent pas
mkdir -p app/tests/__pycache__ 2>/dev/null || true

# Afficher la configuration
log_info "Configuration des tests:"
echo "  - Environnement: $ENVIRONMENT"
echo "  - Base de données: SQLite en mémoire"
echo "  - Tests actifs: $TESTING"
echo ""

# Lancer les tests avec couverture
log_info "Lancement des tests PyTest..."
pytest -xvs \
    --tb=short \
    --strict-markers \
    --disable-warnings \
    --color=yes \
    app/tests/

# Code de sortie
TEST_EXIT_CODE=$?
echo ""

if [[ $TEST_EXIT_CODE -eq 0 ]]; then
    log_success "Tous les tests ont réussi! ✅"
    echo "Base de données de test nettoyée automatiquement."
else
    log_error "Échec des tests avec code de sortie: $TEST_EXIT_CODE ❌"
    log_warning "Consultez les logs ci-dessus pour diagnostiquer les erreurs."
fi

exit $TEST_EXIT_CODE
