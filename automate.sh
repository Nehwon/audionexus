#!/bin/bash

# Usage: automate.sh "Auteur" "Série" Tome "Titre" [--threads N|all]

if [ "$#" -lt 4 ]; then
  echo "Usage: $0 \"Auteur\" \"Série\" Tome \"Titre\" [--threads N|all]"
  exit 1
fi

AUTEUR="$1"
SERIE="$2"
TOME="$3"
TITRE="$4"
shift 4

# Valeur par défaut pour les threads
THREADS=1

# Fonction de base
m4b-tool() {
  docker run -it --rm -u $(id -u):$(id -g) -v "$(pwd)":/mnt sandreas/m4b-tool:latest "$@"
}

# Gestion des options supplémentaires
while [[ $# -gt 0 ]]; do
  case "$1" in
    --threads)
      shift
      if [ "$1" == "all" ]; then
        THREADS=$(nproc)
      else
        THREADS="$1"
      fi
      ;;
    *)
      echo "Option inconnue : $1"
      exit 2
      ;;
  esac
  shift
done

# Construction du nom du dossier et du fichier de sortie
DOSSIER="${AUTEUR} - ${SERIE} ${TOME} - ${TITRE}"
FICHIER_SORTIE="${DOSSIER}.m4b"

# Création du dossier de log
mkdir -p ~/.log

# Commande m4b-tool
m4b-tool merge "${DOSSIER}" \
  --output-file="${FICHIER_SORTIE}" \
  --artist="${AUTEUR}" \
  --album="${TITRE}" \
  --writer="${AUTEUR}" \
  --audio-bitrate 64k \
  --series-part="${TOME}" \
  --jobs="${THREADS}" \
  --force \
  -vv

# Fin du script