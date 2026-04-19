#!/usr/bin/env python3
"""
Script d'auto-bump de version pour AudioNexus.
Ce script analyse les commits et incrémente la version automatiquement.
"""

import re
import sys
from pathlib import Path

def get_current_version():
    """Récupère la version actuelle depuis le fichier VERSION"""
    version_file = Path("VERSION")
    if not version_file.exists():
        raise FileNotFoundError("Fichier VERSION non trouvé")
    
    with open(version_file, 'r') as f:
        for line in f:
            if line.startswith('CURRENT_VERSION='):
                return line.split('=')[1].strip()
    
    raise ValueError("CURRENT_VERSION non trouvé dans le fichier VERSION")

def update_version_file(version):
    """Met à jour le fichier VERSION avec la nouvelle version"""
    version_file = Path("VERSION")
    content = version_file.read_text()
    
    # Mettre à jour la ligne CURRENT_VERSION
    updated_content = re.sub(
        r'^CURRENT_VERSION=.*$',
        f'CURRENT_VERSION={version}',
        content,
        flags=re.MULTILINE
    )
    
    version_file.write_text(updated_content)

def increment_version(current_version, bump_type):
    """Incrémente la version selon le type"""
    parts = current_version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Format de version invalide: {current_version}")
    
    major, minor, fix = map(int, parts)
    
    if bump_type == 'major':
        major += 1
        minor = 0
        fix = 0
    elif bump_type == 'minor':
        minor += 1
        fix = 0
    elif bump_type == 'fix':
        fix += 1
    else:
        raise ValueError(f"Type d'incrément invalide: {bump_type}")
    
    return f"{major}.{minor}.{fix}"

def get_commit_type(commit_message):
    """Détermine le type de commit pour le bump de version"""
    commit_message = commit_message.lower()
    
    if commit_message.startswith('major:'):
        return 'major'
    elif commit_message.startswith('feat:') or commit_message.startswith('rc:'):
        return 'minor'
    else:
        return 'fix'

def main():
    if len(sys.argv) < 2:
        print("Usage: auto_bump_version.py <commit_message>")
        sys.exit(1)
    
    commit_message = sys.argv[1]
    
    try:
        # Récupérer la version actuelle
        current_version = get_current_version()
        print(f"Version actuelle: {current_version}")
        
        # Déterminer le type de bump
        bump_type = get_commit_type(commit_message)
        print(f"Type de bump: {bump_type}")
        
        # Incrémenter la version
        new_version = increment_version(current_version, bump_type)
        print(f"Nouvelle version: {new_version}")
        
        # Mettre à jour le fichier
        update_version_file(new_version)
        print(f"Version mise à jour dans VERSION")
        
        # Retourner la nouvelle version pour utilisation dans les scripts
        print(f"::set-output name=version::{new_version}")
        
    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
