# Documentation de l'ancien script `automate.sh`

## 📝 Description
Ce script était utilisé pour automatiser la conversion de fichiers audio en livres audio au format M4B (AAC) en utilisant `m4b-tool` dans un conteneur Docker.

## 🛠️ Fonctionnalités
- Conversion de dossiers de fichiers audio en un seul fichier M4B
- Gestion des métadonnées (auteur, série, tome, titre)
- Support du multithreading
- Gestion des logs

## 📋 Utilisation
```bash
./automate.sh "Auteur" "Série" Tome "Titre" [--threads N|all]
```

### Paramètres
- `Auteur` : Nom de l'auteur du livre audio
- `Série` : Nom de la série (si applicable)
- `Tome` : Numéro du tome
- `Titre` : Titre du livre audio
- `--threads` : Optionnel, nombre de threads à utiliser (ou "all" pour utiliser tous les cœurs disponibles)

## 🔍 Détails techniques
- Utilise `sandreas/m4b-tool` via Docker
- Crée un fichier de sortie au format : `Auteur - Série Tome - Titre.m4b`
- Les logs sont enregistrés dans `~/.log/`
- Options de conversion :
  - Débit audio : 64k
  - Forçage de l'écrasement des fichiers existants
  - Niveau de verbosité élevé (-vv)

## ⚠️ Statut
Ce script a été remplacé par la solution AudioNexus et n'est plus maintenu. Il est conservé à titre d'archive dans la documentation.
