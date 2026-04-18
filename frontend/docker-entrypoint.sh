#!/bin/sh

# Script d'entrée pour corriger les permissions des volumes Docker
# Ce script s'assure que l'utilisateur appuser peut accéder aux fichiers montés

set -e

echo "🔧 Correction des permissions Docker pour AudioNexus Frontend..."

# Fonction pour corriger les permissions d'un répertoire
fix_permissions() {
    local dir="$1"
    if [ -d "$dir" ]; then
        echo "📁 Correction des permissions pour: $dir"
        chown -R appuser:appuser "$dir" 2>/dev/null || true

        # Pour les répertoires cache, on donne accès en écriture
        if echo "$dir" | grep -qE '\.vite|node_modules/\.cache|.*cache.*'; then
            chmod -R 755 "$dir" 2>/dev/null || true
        fi
    fi
}

# Corriger les permissions des répertoires critiques
fix_permissions "/app"
fix_permissions "/app/node_modules"
fix_permissions "/app/.vite"
fix_permissions "/app/dist"
fix_permissions "/tmp"

# Nettoyer les anciens fichiers de cache Vite problématiques
echo "🧹 Nettoyage du cache Vite..."
find /app -name "vite.config.ts.timestamp-*.mjs" -type f -delete 2>/dev/null || true
find /app -name "*.timestamp-*.mjs" -type f -delete 2>/dev/null || true

# Créer les répertoires nécessaires s'ils n'existent pas
mkdir -p /app/.vite 2>/dev/null || true
mkdir -p /app/node_modules/.cache 2>/dev/null || true
mkdir -p /tmp 2>/dev/null || true

# S'assurer que appuser peut écrire dans ces répertoires
chown -R appuser:appuser /app/.vite /app/node_modules/.cache /tmp 2>/dev/null || true
chmod -R 755 /app/.vite /app/node_modules/.cache /tmp 2>/dev/null || true

echo "✅ Permissions corrigées. Démarrage de Vite..."

# Démarrer Vite avec l'utilisateur appuser
exec su-exec appuser "$@"