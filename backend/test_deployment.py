#!/usr/bin/env python3
"""
Test de compatibilité pour le déploiement
"""

import sys
import importlib

def test_imports():
    """Tester tous les imports critiques"""
    print("🧪 TEST DE COMPATIBILITÉ POUR DÉPLOIEMENT")
    print("=" * 50)
    
    print(f"🐍 Version Python: {sys.version}")
    
    # Test des imports critiques
    imports_to_test = [
        ("sqlalchemy", "SQLAlchemy"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("psutil", "PSUtil"),
        ("schedule", "Schedule"),
        ("database", "Database module"),
        ("database_service", "Database service"),
        ("validation_service", "Validation service"),
        ("monitoring_service", "Monitoring service"),
        ("backup_service", "Backup service")
    ]
    
    success_count = 0
    
    for module_name, description in imports_to_test:
        try:
            print(f"\n🔍 Test import: {description}")
            importlib.import_module(module_name)
            print(f"✅ {description}: RÉUSSI")
            success_count += 1
        except Exception as e:
            print(f"❌ {description}: ÉCHOUÉ - {e}")
    
    print(f"\n📊 RÉSULTATS: {success_count}/{len(imports_to_test)} imports réussis")
    
    if success_count == len(imports_to_test):
        print("🎉 TOUS LES IMPORTS RÉUSSIS !")
        return True
    else:
        print("⚠️ Certains imports ont échoué")
        return False

def test_database_connection():
    """Tester la connexion à la base de données"""
    print("\n🗄️ TEST DE CONNEXION BASE DE DONNÉES")
    print("=" * 50)
    
    try:
        from database import db_manager, init_database
        
        print("1️⃣ Test d'initialisation...")
        if init_database():
            print("✅ Initialisation réussie")
        else:
            print("❌ Échec d'initialisation")
            return False
        
        print("\n2️⃣ Test de connexion...")
        if db_manager.connect():
            print("✅ Connexion réussie")
            
            # Test simple
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM buildings")
            count = cursor.fetchone()[0]
            print(f"✅ Test requête: {count} immeubles")
            
            db_manager.disconnect()
            print("✅ Déconnexion réussie")
        else:
            print("❌ Échec de connexion")
            return False
        
        print("\n🎉 TEST BASE DE DONNÉES RÉUSSI !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test base de données: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_startup():
    """Tester le démarrage de l'API"""
    print("\n🚀 TEST DE DÉMARRAGE API")
    print("=" * 50)
    
    try:
        # Test d'import de l'API
        print("1️⃣ Test import API...")
        from main import app
        print("✅ Import API réussi")
        
        # Test des endpoints principaux
        print("\n2️⃣ Test des endpoints...")
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test endpoint de santé
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Endpoint /health: RÉUSSI")
        else:
            print(f"❌ Endpoint /health: ÉCHOUÉ ({response.status_code})")
            return False
        
        # Test endpoint buildings
        response = client.get("/api/buildings")
        if response.status_code == 200:
            print("✅ Endpoint /api/buildings: RÉUSSI")
        else:
            print(f"❌ Endpoint /api/buildings: ÉCHOUÉ ({response.status_code})")
            return False
        
        print("\n🎉 TEST API RÉUSSI !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST COMPLET DE COMPATIBILITÉ DÉPLOIEMENT")
    print("=" * 60)
    
    # Test 1: Imports
    success1 = test_imports()
    
    # Test 2: Base de données
    success2 = test_database_connection()
    
    # Test 3: API
    success3 = test_api_startup()
    
    # Résumé
    print("\n📊 RÉSUMÉ DES TESTS")
    print("=" * 30)
    print(f"Imports: {'✅ RÉUSSI' if success1 else '❌ ÉCHOUÉ'}")
    print(f"Base de données: {'✅ RÉUSSI' if success2 else '❌ ÉCHOUÉ'}")
    print(f"API: {'✅ RÉUSSI' if success3 else '❌ ÉCHOUÉ'}")
    
    if success1 and success2 and success3:
        print("\n🎉 SYSTÈME PRÊT POUR DÉPLOIEMENT !")
        print("✅ Tous les composants fonctionnent")
        print("✅ Compatibilité vérifiée")
        print("✅ Prêt pour Render")
    else:
        print("\n⚠️ Problèmes détectés - Vérifiez les erreurs ci-dessus")

if __name__ == "__main__":
    main()
