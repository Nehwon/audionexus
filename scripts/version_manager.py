#!/usr/bin/env python3
"""
Script de gestion des versions pour AudioNexus
Gère le versionnement multi-branches avec le format vM.m.f.type
"""

import os
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

def get_branch_type():
    """Détermine le type de branche actuelle"""
    branch = os.getenv('GITHUB_REF_NAME') or os.getenv('CI_BRANCH') or 'main'
    
    if branch == 'main':
        return 'main'
    elif branch == 'devel':
        return 'dev'
    elif branch == 'debug':
        return 'bug'
    elif branch == 'preprod':
        return 'pprod'
    else:
        return 'dev'  # par défaut

def generate_version_tag(base_version, branch_type):
    """Génère un tag de version complet"""
    return f"v{base_version}.{branch_type}"

def increment_version(version, part='fix'):
    """Incrémente une partie de la version (major, minor, ou fix)"""
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Format de version invalide: {version}")
    
    major, minor, fix = map(int, parts)
    
    if part == 'major':
        major += 1
        minor = 0
        fix = 0
    elif part == 'minor':
        minor += 1
        fix = 0
    elif part == 'fix':
        fix += 1
    else:
        raise ValueError(f"Partie de version invalide: {part}")
    
    return f"{major}.{minor}.{fix}"

def get_git_commit_short():
    """Récupère le hash court du commit git"""
    try:
        import subprocess
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except:
        return 'local'

def main():
    if len(sys.argv) < 2:
        print("Usage: version_manager.py <command> [options]")
        print("Commands:")
        print("  get-version          - Affiche la version actuelle")
        print("  get-tag              - Affiche le tag complet pour la branche actuelle")
        print("  bump-major           - Incrémente la version majeure")
        print("  bump-minor           - Incrémente la version mineure")
        print("  bump-fix             - Incrémente la version de fix (par défaut)")
        print("  set-version <ver>    - Définit une version spécifique")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == 'get-version':
            version = get_current_version()
            print(version)
        
        elif command == 'get-tag':
            version = get_current_version()
            branch_type = get_branch_type()
            tag = generate_version_tag(version, branch_type)
            print(tag)
        
        elif command in ['bump-major', 'bump-minor', 'bump-fix']:
            part = command.split('-')[1]
            current_version = get_current_version()
            new_version = increment_version(current_version, part)
            update_version_file(new_version)
            print(f"Version mise à jour: {current_version} → {new_version}")
        
        elif command == 'set-version':
            if len(sys.argv) < 3:
                print("Error: set-version requires a version number")
                sys.exit(1)
            new_version = sys.argv[2]
            if not re.match(r'^\d+\.\d+\.\d+$', new_version):
                print("Error: Invalid version format. Use M.m.f")
                sys.exit(1)
            update_version_file(new_version)
            print(f"Version définie: {new_version}")
        
        else:
            print(f"Error: Unknown command '{command}'")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
