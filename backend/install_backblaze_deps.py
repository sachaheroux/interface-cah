#!/usr/bin/env python3
"""
Script d'installation des dépendances Backblaze B2
"""

import subprocess
import sys

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
    """Installer les dépendances nécessaires"""
    print("📦 Installation des dépendances Backblaze B2...")
    
    packages = [
        "boto3",           # Client AWS S3 compatible pour Backblaze B2
        "python-dotenv"    # Chargement des variables d'environnement
    ]
    
    success = True
    for package in packages:
        if not install_package(package):
            success = False
    
    if success:
        print("\n🎉 Toutes les dépendances sont installées !")
        print("✅ Vous pouvez maintenant configurer Backblaze B2")
    else:
        print("\n❌ Certaines dépendances n'ont pas pu être installées")
        print("🔧 Essayez d'installer manuellement:")
        print("   pip install boto3 python-dotenv")
    
    return success

if __name__ == "__main__":
    main()
