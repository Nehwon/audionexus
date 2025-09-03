#!/bin/bash

set -euo pipefail

# Script de construction Docker optimisé pour AudioNexus
# Utilise les bonnes pratiques Docker pour maximiser le cache et la performance

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE=""
TARGET="production"
BUILD_ARGS=""
PUSH_IMAGE=false
NO_CACHE=false

# Fonction d'aide
show_help() {
    cat << EOF
Script de construction Docker AudioNexus

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -f, --compose-file FILE     Fichier docker-compose à utiliser (prod, dev)
    -t, --target TARGET         Target Docker (production, development) [default: production]
    --build-arg KEY=VALUE      Arguments de construction
    --push                      Pousser l'image après construction
    --no-cache                  Forcer reconstruction sans cache
    -v, --verbose               Mode verbose
    -h, --help                  Afficher cette aide

EXEMPLES:
    # Construction production standard
    $0 -f prod

    # Construction développement
    $0 -f dev -t development

    # Construction avec arguments personnalisés
    $0 -f prod --build-arg BUILDKIT_INLINE_CACHE=1 --push

    # Reconstruction complète sans cache
    $0 -f prod --no-cache --verbose
EOF
}

# Logging
log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

log_warn() {
    echo "[WARN] $1"
}

# Fonction pour vérifier les prérequis
check_prerequisites() {
    local prerequisites=("docker" "docker-compose")

    for cmd in "${prerequisites[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "$cmd n'est pas installé ou n'est pas dans le PATH"
            exit 1
        fi
    done

    log_info "Prérequis vérifiés avec succès"
}

# Fonction pour nettoyer les images non utilisées
cleanup() {
    log_info "Nettoyage des ressources Docker non utilisées..."

    # Supprimer les conteneurs arrêtés
    docker container prune -f

    # Supprimer les images dangling
    docker image prune -f

    # Supprimer les volumes non utilisés
    docker volume prune -f

    # Supprimer les réseaux non utilisés
    docker network prune -f

    log_info "Nettoyage terminé"
}

# Fonction de construction optimisée
build_image() {
    local compose_file="$1"
    local target="$2"
    local build_args="$3"
    local no_cache="$4"
    local push_image="$5"

    cd "$PROJECT_ROOT"

    log_info "Construction de l'image Docker..."
    log_info "Fichier compose: $compose_file"
    log_info "Target: $target"
    log_info "Arguments build: $build_args"

    # Variables d'environnement pour optimiser la construction
    export DOCKER_BUILDKIT=1
    export BUILDKIT_PROGRESS=plain

    # Arguments de construction par défaut pour optimiser
    local default_args="--rm \
        --target $target \
        --platform linux/amd64 \
        --build-arg BUILDKIT_INLINE_CACHE=1"

    # Ajouter --no-cache si demandé
    if [[ "$no_cache" == "true" ]]; then
        default_args="$default_args --no-cache"
        log_info "Reconstruction sans cache activée"
    fi

    # Combiner les arguments
    local final_args="$default_args $build_args"

    log_info "Arguments finaux: $final_args"

    # Construction avec docker-compose
    if ! docker-compose -f "$compose_file" build $final_args; then
        log_error "Échec de la construction Docker"
        exit 1
    fi

    log_info "Construction terminée avec succès"

    # Pousser l'image si demandé
    if [[ "$push_image" == "true" ]]; then
        log_info "Poussée de l'image en cours..."
        if ! docker-compose -f "$compose_file" push; then
            log_error "Échec de la poussée de l'image"
            exit 1
        fi
        log_info "Poussée terminée"
    fi
}

# Fonction de validation post-construction
validate_build() {
    local compose_file="$1"
    local target="$2"

    cd "$PROJECT_ROOT"

    log_info "Validation de la construction..."

    # Vérifier que l'image existe
    local image_name
    image_name=$(docker-compose -f "$compose_file" config | grep "image:" | head -1 | awk '{print $2}' || echo "")

    if [[ -n "$image_name" ]]; then
        if docker image inspect "$image_name" &> /dev/null; then
            local size
            size=$(docker image inspect "$image_name" --format='{{.Size}}' | numfmt --to=iec-i)
            log_info "Image validée: $image_name (taille: $size)"
        else
            log_error "Image $image_name n'existe pas"
            exit 1
        fi
    fi

    log_info "Validation terminée"
}

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--compose-file)
            if [[ "$2" == "prod" ]]; then
                DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.prod.yml"
            elif [[ "$2" == "dev" ]]; then
                DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.dev.yml"
                TARGET="development"
            else
                DOCKER_COMPOSE_FILE="$PROJECT_ROOT/$2"
            fi
            shift 2
            ;;
        -t|--target)
            TARGET="$2"
            shift 2
            ;;
        --build-arg)
            BUILD_ARGS="$BUILD_ARGS --build-arg $2"
            shift 2
            ;;
        --push)
            PUSH_IMAGE=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
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

# Valeurs par défaut si non spécifiées
if [[ -z "$DOCKER_COMPOSE_FILE" ]]; then
    DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
fi

# Vérifications
if [[ ! -f "$DOCKER_COMPOSE_FILE" ]]; then
    log_error "Fichier docker-compose introuvable: $DOCKER_COMPOSE_FILE"
    exit 1
fi

# Exécution principale
main() {
    log_info "=== Construction Docker AudioNexus ==="
    log_info "Début: $(date)"

    check_prerequisites

    if [[ "$NO_CACHE" == "true" ]]; then
        cleanup
    fi

    build_image "$DOCKER_COMPOSE_FILE" "$TARGET" "$BUILD_ARGS" "$NO_CACHE" "$PUSH_IMAGE"

    validate_build "$DOCKER_COMPOSE_FILE" "$TARGET"

    log_info "=== Construction terminée avec succès ==="
    log_info "Fin: $(date)"
}

main "$@"