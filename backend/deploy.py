#!/usr/bin/env python3
"""
Script de déploiement pour Interface CAH
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Vérifier la version de Python"""
    print("🐍 Vérification de la version Python...")
    version = sys.version_info
    print(f"   Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 11:
        print("✅ Version Python compatible")
        return True
    else:
        print("❌ Version Python incompatible (requis: 3.11+)")
        return False

def install_dependencies():
    """Installer les dépendances"""
    print("\n📦 Installation des dépendances...")
    
    try:
        # Mise à jour de pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        print("✅ Pip mis à jour")
        
        # Installation des requirements
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dépendances installées")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation: {e}")
        return False

def test_imports():
    """Tester les imports critiques"""
    print("\n🔍 Test des imports...")
    
    critical_imports = [
        "sqlalchemy",
        "fastapi", 
        "uvicorn",
        "psutil",
        "schedule"
    ]
    
    for module in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    return True

def test_database():
    """Tester la base de données"""
    print("\n🗄️ Test de la base de données...")
    
    try:
        from database import init_database
        if init_database():
            print("✅ Base de données initialisée")
            return True
        else:
            print("❌ Échec initialisation base de données")
            return False
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        return False

def test_api():
    """Tester l'API"""
    print("\n🚀 Test de l'API...")
    
    try:
        from main import app
        print("✅ API importée")
        
        # Test simple des endpoints
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Endpoint /health fonctionne")
        else:
            print(f"❌ Endpoint /health: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False

def create_data_directory():
    """Créer le répertoire de données"""
    print("\n📁 Création du répertoire de données...")
    
    data_dir = os.environ.get("DATA_DIR", "./data")
    
    try:
        os.makedirs(data_dir, exist_ok=True)
        print(f"✅ Répertoire créé: {data_dir}")
        
        # Vérifier les permissions
        if os.access(data_dir, os.R_OK | os.W_OK):
            print("✅ Permissions OK")
        else:
            print("❌ Problème de permissions")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Erreur création répertoire: {e}")
        return False

def main():
    """Fonction principale de déploiement"""
    print("🚀 DÉPLOIEMENT INTERFACE CAH")
    print("=" * 50)
    
    # Vérifications
    checks = [
        ("Version Python", check_python_version),
        ("Installation dépendances", install_dependencies),
        ("Test imports", test_imports),
        ("Création répertoire données", create_data_directory),
        ("Test base de données", test_database),
        ("Test API", test_api)
    ]
    
    success_count = 0
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        if check_func():
            success_count += 1
        else:
            print(f"❌ Échec: {check_name}")
            break
    
    # Résumé
    print(f"\n📊 RÉSULTATS: {success_count}/{len(checks)} vérifications réussies")
    
    if success_count == len(checks):
        print("\n🎉 DÉPLOIEMENT RÉUSSI !")
        print("✅ Tous les composants fonctionnent")
        print("✅ Prêt pour la production")
        
        # Afficher les informations de démarrage
        print("\n🚀 POUR DÉMARRER LE SERVEUR:")
        print("   uvicorn main:app --host 0.0.0.0 --port 8000")
        
        return True
    else:
        print("\n⚠️ DÉPLOIEMENT ÉCHOUÉ")
        print("❌ Vérifiez les erreurs ci-dessus")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
