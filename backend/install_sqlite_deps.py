#!/usr/bin/env python3
"""
Script pour installer les dépendances SQLite
Usage: python install_sqlite_deps.py
"""

import subprocess
import sys
import os

def install_package(package):
    """Installer un package Python"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation de {package}: {e}")
        return False

def main():
    """Installer toutes les dépendances nécessaires"""
    print("📦 INSTALLATION DES DÉPENDANCES SQLITE")
    print("=" * 50)
    
    # Dépendances nécessaires
    packages = [
        "sqlite3",  # Déjà inclus avec Python
        "sqlalchemy",  # ORM pour Python
        "alembic",  # Migrations de base de données
    ]
    
    print("🔍 Vérification des dépendances...")
    
    # Vérifier si sqlite3 est disponible
    try:
        import sqlite3
        print("✅ sqlite3 disponible (inclus avec Python)")
    except ImportError:
        print("❌ sqlite3 non disponible")
        return False
    
    # Installer les packages manquants
    success = True
    for package in packages:
        if package == "sqlite3":
            continue  # Déjà vérifié
            
        try:
            __import__(package)
            print(f"✅ {package} déjà installé")
        except ImportError:
            print(f"📦 Installation de {package}...")
            if not install_package(package):
                success = False
    
    if success:
        print("\n🎉 TOUTES LES DÉPENDANCES SONT PRÊTES !")
        print("✅ Vous pouvez maintenant exécuter la migration")
        return True
    else:
        print("\n❌ Certaines dépendances n'ont pas pu être installées")
        return False

if __name__ == "__main__":
    main()
