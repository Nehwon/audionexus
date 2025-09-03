#!/bin/bash

set -euo pipefail

# Script de déploiement Docker AudioNexus avec rollback
# Gère le déploiement zero-downtime et les rollbacks automatiques

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
ROLLBACK_TAG=""
DEPLOY_TAG=""
ENVIRONMENT="prod"
SKIP_HEALTH_CHECK=false
SKIP_BUILD=false
ROLLBACK_ON_FAILURE=true
TIMEOUT=300
REPLICAS=1

# Logging
log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

log_warn() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [WARN] $1"
}

# Fonction d'aide
show_help() {
    cat << EOF
Script de déploiement Docker AudioNexus

USAGE:
    $0 [OPTIONS] [COMMAND]

COMMANDES:
    deploy      Déployer l'application
    rollback    Rollback vers le tag précédent
    status      Afficher le statut du déploiement
    logs        Afficher les logs du déploiement

OPTIONS:
    -e, --environment ENV      Environnement (prod, dev) [default: prod]
    -t, --tag TAG              Tag du déploiement
    --skip-health-check        Ne pas attendre les health checks
    --skip-build              Ne pas construire les images
    --no-rollback             Ne pas faire de rollback automatique en cas d'échec
    --timeout SECONDS         Timeout pour les déploiements [default: 300]
    --replicas N              Nombre de réplicas [default: 1]
    -v, --verbose             Mode verbose
    -h, --help                Afficher cette aide

EXEMPLES:
    # Déploiement production
    $0 deploy -e prod -t v1.2.3

    # Déploiement développement sans health check
    $0 deploy -e dev --skip-health-check

    # Rollback d'urgence
    $0 rollback

    # Statut du déploiement
    $0 status
EOF
}

# Fonction de vérification des prérequis
check_prerequisites() {
    cd "$PROJECT_ROOT"

    # Vérifier la présence des fichiers nécessaires
    local required_files=("docker-compose.${ENVIRONMENT}.yml" ".env.${ENVIRONMENT}")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Fichier requis manquant: $file"
            exit 1
        fi
    done

    log_info "Prérequis vérifiés"
}

# Créer un tag de déploiement unique
create_deploy_tag() {
    if [[ -z "$DEPLOY_TAG" ]]; then
        DEPLOY_TAG="deploy-$(date +%Y%m%d-%H%M%S)"
    fi

    log_info "Tag de déploiement: $DEPLOY_TAG"
    echo "$DEPLOY_TAG"
}

# Fonction de sauvegarde de la configuration actuelle
backup_current_state() {
    local backup_dir="$PROJECT_ROOT/backups/$(date +%Y%m%d-%H%M%S)-$ENVIRONMENT"
    local compose_file="docker-compose.${ENVIRONMENT}.yml"

    log_info "Création de la sauvegarde dans: $backup_dir"

    mkdir -p "$backup_dir"

    # Sauvegarder la configuration Docker
    docker-compose -f "$compose_file" config > "$backup_dir/docker-compose-config.yml"

    # Sauvegarder les volumes (optionnel, coûteux)
    # docker run --rm -v audionexus_mysql_data:/source -v $backup_dir:/backup alpine tar czf /backup/mysql-data.tar.gz -C /source .

    # Sauvegarder les logs actuels
    docker-compose -f "$compose_file" logs > "$backup_dir/current-logs.log" 2>&1 || true

    # Sauvegarder les variables d'environnement
    cp ".env.${ENVIRONMENT}" "$backup_dir/.env.backup"

    log_info "Sauvegarde créée: $backup_dir"
    echo "$backup_dir"
}

# Fonction de construction des images
build_images() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        log_info "Construction des images ignorée (--skip-build)"
        return 0
    fi

    local compose_file="docker-compose.${ENVIRONMENT}.yml"

    log_info "Construction des images..."

    # Utiliser le script de construction optimisé
    if [[ -x "$SCRIPT_DIR/docker-build.sh" ]]; then
        bash "$SCRIPT_DIR/docker-build.sh" -f "$ENVIRONMENT" --no-cache
    else
        # Fallback vers docker-compose
        docker-compose -f "$compose_file" build --no-cache
    fi

    log_info "Construction terminée"
}

# Fonction de déploiement
deploy_services() {
    local compose_file="docker-compose.${ENVIRONMENT}.yml"

    log_info "Déploiement des services..."

    # Démarrer les services
    docker-compose -f "$compose_file" up -d --scale backend="$REPLICAS"

    # Attendre le démarrage
    if [[ "$SKIP_HEALTH_CHECK" != "true" ]]; then
        wait_for_healthy
    fi

    log_info "Services déployés et sains"
}

# Fonction d'attente des health checks
wait_for_healthy() {
    local compose_file="docker-compose.${ENVIRONMENT}.yml"
    local start_time
    start_time=$(date +%s)

    log_info "Attente des health checks (timeout: ${TIMEOUT}s)..."

    while true; do
        local current_time
        current_time=$(date +%s)
        local elapsed=$((current_time - start_time))

        if [[ $elapsed -gt $TIMEOUT ]]; then
            log_error "Timeout dépassé lors des health checks"
            return 1
        fi

        # Vérifier l'état des containers
        if docker-compose -f "$compose_file" ps | grep -q "unhealthy\|Exit"; then
            log_error "Service défaillant détecté"
            if [[ "$ROLLBACK_ON_FAILURE" == "true" ]]; then
                log_error "Déclenchement du rollback automatique..."
                rollback_deployment
            fi
            return 1
        fi

        # Vérifier si tous les services sont healthy
        local unhealthy_count
        unhealthy_count=$(docker-compose -f "$compose_file" ps | grep -c "healthy" || echo "0")

        if [[ $unhealthy_count -eq 0 ]]; then
            # Attendre un peu plus pour s'assurer de la stabilité
            sleep 5
            unhealthy_count=$(docker-compose -f "$compose_file" ps | grep -c "healthy" || echo "0")
            if [[ $unhealthy_count -eq 0 ]]; then
                log_info "Tous les services sont sains"
                return 0
            fi
        fi

        sleep 10
    done
}

# Fonction de rollback
rollback_deployment() {
    local compose_file="docker-compose.${ENVIRONMENT}.yml"

    log_info "Début du rollback..."

    # Arrêt des services actuels
    docker-compose -f "$compose_file" down

    # Restaurer l'ancienne image si elle existe
    if [[ -n "$ROLLBACK_TAG" ]]; then
        log_info "Restaurer le tag: $ROLLBACK_TAG"
        docker tag "$ROLLBACK_TAG" "$(docker-compose -f "$compose_file" config | grep 'image:' | awk '{print $2}')"
    fi

    # Redémarrer avec l'ancienne version
    docker-compose -f "$compose_file" up -d

    # Attendre la stabilité
    if [[ "$SKIP_HEALTH_CHECK" != "true" ]]; then
        wait_for_healthy
    fi

    log_info "Rollback terminé"
}

# Fonction de nettoyage post-déploiement
cleanup_old_images() {
    log_info "Nettoyage des anciennes images..."

    # Garder seulement les 3 dernières images
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}" | \
        grep "audionexus" | \
        sort -r | \
        tail -n +4 | \
        awk '{print $3}' | \
        xargs -r docker rmi || true

    log_info "Nettoyage terminé"
}

# Fonction d'affichage du statut
show_status() {
    local compose_file="docker-compose.${ENVIRONMENT}.yml"

    echo "=== Statut du déploiement AudioNexus ($ENVIRONMENT) ==="
    echo ""

    docker-compose -f "$compose_file" ps

    echo ""
    echo "=== Utilisation des ressources ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--tag)
            DEPLOY_TAG="$2"
            shift 2
            ;;
        --skip-health-check)
            SKIP_HEALTH_CHECK=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --no-rollback)
            ROLLBACK_ON_FAILURE=false
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --replicas)
            REPLICAS="$2"
            shift 2
            ;;
        -v|--verbose)
            set -x
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        deploy|rollback|status|logs)
            COMMAND="$1"
            shift
            ;;
        *)
            log_error "Argument inconnu: $1"
            show_help
            exit 1
            ;;
    esac
done

# Valeurs par défaut
if [[ -z "${COMMAND:-}" ]]; then
    COMMAND="deploy"
fi

# Fonctions par commande
case "$COMMAND" in
    deploy)
        log_info "=== Déploiement AudioNexus ==="

        check_prerequisites
        ROLLBACK_TAG=$(backup_current_state)
        DEPLOY_TAG=$(create_deploy_tag)
        build_images
        deploy_services
        cleanup_old_images

        log_info "=== Déploiement terminé avec succès ==="
        log_info "Tag déployé: $DEPLOY_TAG"
        ;;
    rollback)
        log_info "=== Rollback AudioNexus ==="

        check_prerequisites
        rollback_deployment

        log_info "=== Rollback terminé ==="
        ;;
    status)
        show_status
        ;;
    logs)
        local compose_file="docker-compose.${ENVIRONMENT}.yml"
        docker-compose -f "$compose_file" logs -f
        ;;
    *)
        log_error "Commande inconnue: $COMMAND"
        show_help
        exit 1
        ;;
esac