#!/usr/bin/env python3
"""
Analyse des commits pour déterminer la version logique.
"""

import re

def is_feat(commit_msg):
    """Détermine si un commit est une feature"""
    commit_msg = commit_msg.lower()
    
    # Mots-clés pour les features
    feat_keywords = [
        'feat:', 'feature', 'ajout', 'implémentation', 'implémentation',
        'ajout', 'création', 'nouveau', 'add', 'create', 'new'
    ]
    
    # Mots-clés pour les corrections
    fix_keywords = [
        'fix:', 'correction', 'corrig', 'bug', 'error', 'issue',
        'problème', 'résolution', 'patch', 'hotfix'
    ]
    
    # Vérifier les mots-clés
    for keyword in feat_keywords:
        if keyword in commit_msg:
            return True
    
    for keyword in fix_keywords:
        if keyword in commit_msg:
            return False
    
    # Par défaut, considérer comme fix (conservateur)
    return False

def analyze_commits():
    """Analyse tous les commits et détermine la version"""
    major = 0
    minor = 0
    fix = 0
    
    with open('commits.txt', 'r') as f:
        for line in f:
            # Extraire le message (après le hash)
            parts = line.split(' ', 1)
            if len(parts) < 2:
                continue
            commit_msg = parts[1].strip()
            
            if is_feat(commit_msg):
                minor += 1
                fix = 0  # Réinitialiser les fixes
                print(f"FEAT: {commit_msg} → v{major}.{minor}.{fix}")
            else:
                fix += 1
                print(f"FIX:  {commit_msg} → v{major}.{minor}.{fix}")
    
    return major, minor, fix

if __name__ == '__main__':
    major, minor, fix = analyze_commits()
    print(f"\n=== VERSION FINALE: v{major}.{minor}.{fix} ===")
