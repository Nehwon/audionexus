#!/bin/bash

set -euo pipefail

# Script de tests Docker AudioNexus
# Lance les tests d'intégration avec Docker Compose

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
ENVIRONMENT="test"
COVERAGE=false
PARALLEL_TESTS=false
SKIP_BUILD=false
NO_CLEANUP=false
TEST_TYPE="all"
CONTAINER_NAME="audionexus-test-${RANDOM}"

# Logging
log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

log_success() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [SUCCESS] $1"
}

# Fonction d'aide
show_help() {
    cat << EOF
Script de tests Docker AudioNexus

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -e, --environment ENV      Environnement de test (test, development) [default: test]
    -t, --type TYPE            Type de tests (unit, integration, all) [default: all]
    --coverage                 Générer le rapport de couverture
    --parallel                 Exécuter les tests en parallèle
    --skip-build              Ne pas reconstruire les images
    --no-cleanup              Ne pas nettoyer les ressources après les tests
    -v, --verbose             Mode verbose
    -h, --help                Afficher cette aide

EXEMPLES:
    # Tests d'intégration complets
    $0 -t integration --coverage

    # Tests unitaires seulement
    $0 -t unit

    # Tests avec environnement développement
    $0 -e development --parallel
EOF
}

# Vérifier les prérequis
check_prerequisites() {
    cd "$PROJECT_ROOT"

    local required_tools=("docker" "docker-compose")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Outil requis manquant: $tool"
            exit 1
        fi
    done

    log_info "Prérequis vérifiés"
}

# Créer un fichier docker-compose pour les tests
create_test_compose() {
    local test_compose="$PROJECT_ROOT/docker-compose.test.yml"

    cat > "$test_compose" << EOF
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: $CONTAINER_NAME
    env_file:
      - .env.test
    environment:
      - FLASK_ENV=test
      - TESTING=true
      - COVERAGE=${COVERAGE}
    volumes:
      - .:/app:cached
    depends_on:
      - test-db
      - redis
    networks:
      - test-network

  test-db:
    image: mysql:8.0
    container_name: audionexus-test-db
    env_file:
      - .env.test
    environment:
      MYSQL_ROOT_PASSWORD: test_password
      MYSQL_DATABASE: audiobookshelf_test
      MYSQL_USER: test_user
      MYSQL_PASSWORD: test_password
      MYSQL_ROOT_HOST: '%'
      MYSQL_LOG_CONSOLE: 'true'
    command:
      - --default-authentication-plugin=mysql_native_password
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
    volumes:
      - mysql_test_data:/var/lib/mysql
    ports:
      - "3307:3306"
    networks:
      - test-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u\${MYSQL_USER}", "-p\${MYSQL_PASSWORD}"]
      interval: 5s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    container_name: audionexus-test-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_test_data:/data
    networks:
      - test-network

networks:
  test-network:
    driver: bridge

volumes:
  mysql_test_data:
    name: audionexus_mysql_test_data
  redis_test_data:
    name: audionexus_redis_test_data
EOF

    log_info "Fichier de tests Docker Compose créé: $test_compose"
}

# Construire l'image de test si nécessaire
build_test_image() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        log_info "Construction ignorée (--skip-build)"
        return 0
    fi

    local test_compose="$PROJECT_ROOT/docker-compose.test.yml"

    log_info "Construction de l'image de test..."
    docker-compose -f "$test_compose" build backend
    log_info "Image de test construite"
}

# Attendre que la base de données soit prête
wait_for_db() {
    local test_compose="$PROJECT_ROOT/docker-compose.test.yml"

    log_info "Attente de la disponibilité de la base de données..."

    local max_attempts=30
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f "$test_compose" exec -T test-db mysqladmin ping -h localhost -u test_user -ptest_password &>/dev/null; then
            log_success "Base de données prête"
            return 0
        fi

        log_info "Tentative $attempt/$max_attempts - Base de données pas encore prête..."
        sleep 2
        ((attempt++))
    done

    log_error "Timeout dépassé - Base de données non disponible"
    return 1
}

# Exécuter les tests
run_tests() {
    local test_compose="$PROJECT_ROOT/docker-compose.test.yml"
    local test_command=""

    log_info "Lancement des tests ($TEST_TYPE)..."

    # Démarrer les services de test
    docker-compose -f "$test_compose" up -d test-db redis

    # Attendre que la base soit prête
    wait_for_db

    # Démarrer le service backend
    docker-compose -f "$test_compose" up -d backend

    # Attendre que le backend soit prêt
    sleep 10

    # Préparer la commande de test
    case "$TEST_TYPE" in
        unit)
            test_command="python -m pytest app/tests/ -v --tb=short"
            ;;
        integration)
            test_command="python -m pytest tests/integration/ -v --tb=short"
            ;;
        all|*)
            test_command="python -m pytest app/tests/ tests/integration/ -v --tb=short"
            ;;
    esac

    # Ajouter la couverture si demandé
    if [[ "$COVERAGE" == "true" ]]; then
        test_command="$test_command --cov=app --cov-report=html --cov-report=term"
    fi

    # Ajouter le parallélisme si demandé
    if [[ "$PARALLEL_TESTS" == "true" ]]; then
        test_command="$test_command -n auto"
    fi

    log_info "Commande de test: $test_command"

    # Exécuter les tests dans le container
    local test_result
    if docker-compose -f "$test_compose" exec -T backend bash -c "$test_command"; then
        test_result=0
        log_success "Tests passés avec succès"
    else
        test_result=$?
        log_error "Tests échoués"
    fi

    return $test_result
}

# Fonction de nettoyage
cleanup() {
    if [[ "$NO_CLEANUP" == "true" ]]; then
        log_info "Nettoyage ignoré (--no-cleanup)"
        return 0
    fi

    local test_compose="$PROJECT_ROOT/docker-compose.test.yml"

    log_info "Nettoyage des ressources de test..."

    # Arrêter et supprimer les containers
    docker-compose -f "$test_compose" down -v

    # Supprimer l'image de test
    docker rmi "$CONTAINER_NAME" 2>/dev/null || true

    # Supprimer le fichier compose temporaire
    rm -f "$test_compose"

    log_info "Nettoyage terminé"
}

# Fonction de génération du rapport de couverture
generate_coverage_report() {
    if [[ "$COVERAGE" != "true" ]]; then
        return 0
    fi

    local test_compose="$PROJECT_ROOT/docker-compose.test.yml"
    local coverage_dir="$PROJECT_ROOT/htmlcov"

    log_info "Génération du rapport de couverture..."

    # Copier le rapport depuis le container si nécessaire
    if [[ -d "$coverage_dir" ]]; then
        log_info "Rapport de couverture généré: $coverage_dir/index.html"
        echo "Rapport disponible: file://$coverage_dir/index.html"
    else
        log_warn "Rapport de couverture non trouvé"
    fi
}

# Gestion des signaux pour le nettoyage
trap cleanup EXIT

# Parser les arguments
while [[ $# -gt 0 ]]; do
case $1 in
    -e|--environment)
        ENVIRONMENT="$2"
        shift 2
        ;;
    -t|--type)
        TEST_TYPE="$2"
        shift 2
        ;;
    --coverage)
        COVERAGE=true
        shift
        ;;
    --parallel)
        PARALLEL_TESTS=true
        shift
        ;;
    --skip-build)
        SKIP_BUILD=true
        shift
        ;;
    --no-cleanup)
        NO_CLEANUP=true
        shift
        ;;
    -v|--verbose)
        set -x
        shift
        ;;
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        log_error "Argument inconnu: $1"
        show_help
        exit 1
        ;;
    esac
done

# Fonction principale
main() {
    log_info "=== Tests Docker AudioNexus ==="
    log_info "Environnement: $ENVIRONMENT"
    log_info "Type de tests: $TEST_TYPE"
    log_info "Couverture: $COVERAGE"
    log_info "Parallèle: $PARALLEL_TESTS"

    log_info "Début: $(date)"

    check_prerequisites
    create_test_compose
    build_test_image

    # Exécuter les tests et capturer le résultat
    local test_result
    if run_tests; then
        test_result=0
        log_success "=== Tests réussis ==="
    else
        test_result=$?
        log_error "=== Tests échoués ==="
    fi

    # Générer le rapport de couverture
    generate_coverage_report

    log_info "Fin: $(date)"

    return $test_result
}

# Exécuter la fonction principale et propager le code de sortie
main "$@"