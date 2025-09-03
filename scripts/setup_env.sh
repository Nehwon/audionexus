#!/bin/bash

# Script de gestion des environnements AudioNexus
# Permet de basculer facilement entre les environnements de développement, test et production

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Fonction pour vérifier si un fichier existe
file_exists() {
    [[ -f "$1" ]]
}

# Fonction pour copier un environnement
switch_env() {
    local env=$1

    if file_exists ".env.${env}"; then
        cp ".env.${env}" ".env"
        log_success "Configuration basculée vers l'environnement: ${env}"
        log_info "Fichier actif: .env (copié depuis .env.${env})"
    else
        log_error "Fichier .env.${env} introuvable"
        log_info "Environnements disponibles:"
        ls -1 .env.* 2>/dev/null | sed 's/\.env\./  - /' || log_warning "Aucun fichier d'environnement trouvé"
        exit 1
    fi
}

# Fonction pour afficher la configuration actuelle
show_current_config() {
    if file_exists ".env"; then
        log_info "Configuration actuelle (.env):"
        echo "----------------------------------------"
        grep -E "^(ENVIRONMENT|DB_TYPE|DB_HOST|DB_NAME|DEBUG)=" .env 2>/dev/null || log_warning "Variables principales non trouvées"
        echo "----------------------------------------"
    else
        log_warning "Aucun fichier .env actif trouvé"
    fi
}

# Fonction pour afficher l'aide
show_help() {
    echo "Script de gestion des environnements AudioNexus"
    echo ""
    echo "USAGE:"
    echo "  $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "COMMANDS:"
    echo "  dev         Basculer vers l'environnement de développement (SQLite)"
    echo "  prod        Basculer vers l'environnement de production (MySQL)"
    echo "  test        Basculer vers l'environnement de test (SQLite en mémoire)"
    echo "  status      Afficher la configuration actuelle"
    echo "  list        Lister tous les environnements disponibles"
    echo "  help        Afficher cette aide"
    echo ""
    echo "OPTIONS:"
    echo "  --dry-run   Afficher les actions sans les exécuter"
    echo ""
    echo "EXEMPLES:"
    echo "  $0 dev      # Bascule en développement"
    echo "  $0 prod     # Bascule en production"
    echo "  $0 status   # Vérifie la config actuelle"
}

# Fonction pour lister les environnements
list_envs() {
    log_info "Environnements disponibles:"
    for env_file in .env.*; do
        if [[ -f "$env_file" ]]; then
            env_name=$(basename "$env_file" | sed 's/\.env\.//')
            env_type="SQLite"
            if grep -q "DB_TYPE=mysql" "$env_file" 2>/dev/null; then
                env_type="MySQL"
            fi
            echo "  - ${env_name} (${env_type})"
        fi
    done
}

# Vérifier l'argument
case "${1:-help}" in
    "dev")
        log_info "Basculement vers l'environnement de développement..."
        switch_env "development"
        log_info "Base de données: SQLite (.env.development)"
        ;;
    "prod")
        log_warning "ATTENTION: Basculement vers la PRODUCTION"
        log_warning "Assurez-vous que les mots de passe et clés secrètes sont configurés correctement"
        switch_env "production"
        log_info "Base de données: MySQL (.env.production)"
        ;;
    "test")
        switch_env "test"
        log_info "Base de données: SQLite en mémoire (.env.test)"
        ;;
    "status")
        show_current_config
        ;;
    "list")
        list_envs
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        log_error "Commande inconnue: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

# Afficher la configuration finale si ce n'est pas une commande informative
if [[ "$1" != "help" && "$1" != "status" && "$1" != "list" && "$1" != "" ]]; then
    echo ""
    show_current_config
    log_success "Configuration appliquée avec succès!"
fi