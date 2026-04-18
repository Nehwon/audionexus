#!/bin/bash

# Script de démarrage pour AudioNexus
# Utilisation: ./start.sh [dev|prod|stop]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Fonction d'aide
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev        Démarrer en mode développement"
    echo "  prod       Démarrer en mode production"
    echo "  stop       Arrêter tous les services"
    echo "  restart    Redémarrer tous les services"
    echo "  logs       Afficher les logs de tous les services"
    echo "  status     Afficher l'état des services"
    echo "  help       Afficher cette aide"
    echo ""
    echo "Examples:"
    echo "  $0 dev          # Démarre le mode développement"
    echo "  $0 prod         # Démarre le mode production"
    echo "  $0 logs backend # Affiche les logs du backend"
}

# Vérifier si Docker est installé
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "Erreur: Docker n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo "Erreur: Docker Compose n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
}

# Démarrer en mode développement
start_dev() {
    echo "🚀 Démarrage d'AudioNexus en mode développement..."

    # Créer les répertoires nécessaires
    mkdir -p data/database
    mkdir -p data/audiobookshelf/{config,metadata,podcasts,audiobooks}
    mkdir -p logs

    # Démarrer les services
    docker-compose -f docker-compose.dev.yml up -d

    echo "✅ Services de développement démarrés !"
    echo ""
    echo "🌐 Services disponibles :"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Adminer (Base de données): http://localhost:8080"
    echo "  - Redis: localhost:6379"
    echo "  - Redis Cache: localhost:6380"
    echo "  - Audiobookshelf: http://localhost:13378"
    echo ""
    echo "📜 Pour voir les logs: $0 logs"
    echo "🛑 Pour arrêter: $0 stop"
}

# Démarrer en mode production
start_prod() {
    echo "🏭 Démarrage d'AudioNexus en mode production..."

    # Vérifier la présence du fichier .env
    if [ ! -f ".env" ]; then
        echo "⚠️  ATTENTION: Fichier .env non trouvé."
        echo "Veuillez copier .env.example vers .env et configurer les valeurs appropriées."
        echo "cp .env.example .env"
        exit 1
    fi

    # Créer les répertoires nécessaires
    mkdir -p data/database
    mkdir -p data/audiobookshelf/{config,metadata,podcasts,audiobooks}
    mkdir -p data/certbot/{conf,www}
    mkdir -p logs

    # Démarrer les services
    docker-compose up -d

    echo "✅ Services de production démarrés !"
    echo ""
    echo "🌐 Service disponible :"
    echo "  - Application: http://localhost"
    echo ""
    echo "📜 Pour voir les logs: $0 logs"
    echo "🛑 Pour arrêter: $0 stop"
}

# Arrêter les services
stop_services() {
    echo "🛑 Arrêt de tous les services..."

    # Arrêter les services de développement
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true

    # Arrêter les services de production
    docker-compose down 2>/dev/null || true

    echo "✅ Tous les services arrêtés."
}

# Afficher les logs
show_logs() {
    if [ $# -eq 1 ]; then
        echo "📜 Logs du service: $1"
        docker-compose -f docker-compose.dev.yml logs -f "$1" 2>/dev/null || \
        docker-compose logs -f "$1" 2>/dev/null || \
        echo "Service '$1' non trouvé ou non démarré."
    else
        echo "📜 Logs de tous les services:"
        docker-compose -f docker-compose.dev.yml logs -f 2>/dev/null || \
        docker-compose logs -f 2>/dev/null || \
        echo "Aucun service en cours d'exécution."
    fi
}

# Afficher l'état des services
show_status() {
    echo "📊 État des services:"
    echo ""

    # Vérifier les services de développement
    if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
        echo "🔧 Mode développement:"
        docker-compose -f docker-compose.dev.yml ps
    elif docker-compose ps | grep -q "Up"; then
        echo "🏭 Mode production:"
        docker-compose ps
    else
        echo "❌ Aucun service en cours d'exécution."
        echo "Utilisez '$0 dev' ou '$0 prod' pour démarrer."
    fi
}

# Redémarrer les services
restart_services() {
    echo "🔄 Redémarrage des services..."

    stop_services

    # Déterminer le mode actif
    if [ -f "docker-compose.dev.yml" ] && docker-compose -f docker-compose.dev.yml ps | grep -q "Up" 2>/dev/null; then
        start_dev
    elif [ -f "docker-compose.yml" ] && docker-compose ps | grep -q "Up" 2>/dev/null; then
        start_prod
    else
        echo "❓ Mode non déterminé. Démarrage en développement par défaut..."
        start_dev
    fi
}

# Point d'entrée principal
main() {
    check_docker

    case "${1:-help}" in
        dev)
            start_dev
            ;;
        prod)
            start_prod
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs "$2"
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "❌ Commande inconnue: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"