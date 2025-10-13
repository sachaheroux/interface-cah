#!/usr/bin/env python3
"""
Script pour supprimer les fichiers DB SQLite du repo Git
"""

import subprocess
import os

def run_git_command(command):
    """Exécuter une commande Git"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),  # Racine du projet
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def cleanup_db_files():
    print("\n" + "="*60)
    print("🧹 NETTOYAGE DES FICHIERS DB DU REPO GIT")
    print("="*60)
    
    # Fichiers à supprimer du repo
    files_to_remove = [
        "backend/data/cah_database.db-shm",
        "backend/data/cah_database.db-wal"
    ]
    
    # Supprimer du cache Git (mais garder localement)
    for file in files_to_remove:
        print(f"\n📝 Suppression de {file} du cache Git...")
        run_git_command(f'git rm --cached "{file}"')
    
    # Ajouter .gitignore
    print("\n📝 Ajout de .gitignore...")
    run_git_command("git add .gitignore")
    
    # Commit
    print("\n📝 Création du commit...")
    if run_git_command('git commit -m "chore: ignorer fichiers SQLite temporaires"'):
        print("✅ Commit créé avec succès")
        
        # Push
        print("\n📝 Push vers GitHub...")
        if run_git_command("git push"):
            print("✅ Modifications poussées vers GitHub")
        else:
            print("❌ Erreur lors du push")
    else:
        print("ℹ️ Rien à commiter (peut-être déjà fait)")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    cleanup_db_files()

