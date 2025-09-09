#!/usr/bin/env python3
"""
Script de test pour l'API SQLite
Usage: python test_api_sqlite.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_server_startup():
    """Tester si le serveur démarre correctement"""
    print("🚀 Test de démarrage du serveur...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur démarré avec succès")
            return True
        else:
            print(f"❌ Serveur répond mais avec erreur: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("💡 Assurez-vous que le serveur est démarré avec: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test du serveur: {e}")
        return False

def test_buildings_endpoints():
    """Tester les endpoints des immeubles"""
    print("\n🏢 Test des endpoints des immeubles...")
    
    try:
        # Test GET /api/buildings
        print("  Test GET /api/buildings...")
        response = requests.get(f"{API_BASE_URL}/api/buildings")
        if response.status_code == 200:
            buildings = response.json()
            print(f"  ✅ Récupéré {len(buildings)} immeubles")
        else:
            print(f"  ❌ Erreur GET buildings: {response.status_code}")
            return False
        
        # Test POST /api/buildings (créer un immeuble de test)
        print("  Test POST /api/buildings...")
        test_building = {
            "name": "Immeuble Test SQLite",
            "address": {
                "street": "123 Rue Test",
                "city": "Montréal",
                "province": "QC",
                "postalCode": "H1A 1A1",
                "country": "Canada"
            },
            "type": "Résidentiel",
            "units": 5,
            "floors": 3,
            "yearBuilt": 2020,
            "totalArea": 1000,
            "notes": "Immeuble de test pour SQLite"
        }
        
        response = requests.post(f"{API_BASE_URL}/api/buildings", json=test_building)
        if response.status_code == 200:
            created_building = response.json()
            building_id = created_building["id"]
            print(f"  ✅ Immeuble créé avec ID: {building_id}")
            
            # Test GET /api/buildings/{id}
            print("  Test GET /api/buildings/{id}...")
            response = requests.get(f"{API_BASE_URL}/api/buildings/{building_id}")
            if response.status_code == 200:
                print("  ✅ Immeuble récupéré par ID")
            else:
                print(f"  ❌ Erreur GET building by ID: {response.status_code}")
                return False
            
            # Test PUT /api/buildings/{id}
            print("  Test PUT /api/buildings/{id}...")
            update_data = {"name": "Immeuble Test SQLite Modifié"}
            response = requests.put(f"{API_BASE_URL}/api/buildings/{building_id}", json=update_data)
            if response.status_code == 200:
                print("  ✅ Immeuble mis à jour")
            else:
                print(f"  ❌ Erreur PUT building: {response.status_code}")
                return False
            
            # Test DELETE /api/buildings/{id}
            print("  Test DELETE /api/buildings/{id}...")
            response = requests.delete(f"{API_BASE_URL}/api/buildings/{building_id}")
            if response.status_code == 200:
                print("  ✅ Immeuble supprimé")
            else:
                print(f"  ❌ Erreur DELETE building: {response.status_code}")
                return False
            
        else:
            print(f"  ❌ Erreur POST building: {response.status_code}")
            print(f"  Détails: {response.text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test des immeubles: {e}")
        return False

def test_invoices_endpoints():
    """Tester les endpoints des factures"""
    print("\n💰 Test des endpoints des factures...")
    
    try:
        # Test GET /api/invoices/constants
        print("  Test GET /api/invoices/constants...")
        response = requests.get(f"{API_BASE_URL}/api/invoices/constants")
        if response.status_code == 200:
            constants = response.json()
            print(f"  ✅ Constantes récupérées: {len(constants.get('categories', {}))} catégories")
        else:
            print(f"  ❌ Erreur GET constants: {response.status_code}")
            return False
        
        # Test GET /api/invoices
        print("  Test GET /api/invoices...")
        response = requests.get(f"{API_BASE_URL}/api/invoices")
        if response.status_code == 200:
            invoices = response.json()
            print(f"  ✅ Récupéré {len(invoices.get('data', []))} factures")
        else:
            print(f"  ❌ Erreur GET invoices: {response.status_code}")
            return False
        
        # Test POST /api/invoices (créer une facture de test)
        print("  Test POST /api/invoices...")
        test_invoice = {
            "invoiceNumber": f"TEST-{int(time.time())}",
            "category": "municipal_taxes",
            "source": "Ville de Montréal",
            "date": datetime.now().isoformat(),
            "amount": 1500.50,
            "currency": "CAD",
            "paymentType": "bank_transfer",
            "buildingId": 1,
            "notes": "Facture de test pour SQLite"
        }
        
        response = requests.post(f"{API_BASE_URL}/api/invoices", json=test_invoice)
        if response.status_code == 200:
            created_invoice = response.json()
            invoice_id = created_invoice["data"]["id"]
            print(f"  ✅ Facture créée avec ID: {invoice_id}")
            
            # Test GET /api/invoices/{id}
            print("  Test GET /api/invoices/{id}...")
            response = requests.get(f"{API_BASE_URL}/api/invoices/{invoice_id}")
            if response.status_code == 200:
                print("  ✅ Facture récupérée par ID")
            else:
                print(f"  ❌ Erreur GET invoice by ID: {response.status_code}")
                return False
            
        else:
            print(f"  ❌ Erreur POST invoice: {response.status_code}")
            print(f"  Détails: {response.text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test des factures: {e}")
        return False

def test_database_integrity():
    """Tester l'intégrité de la base de données"""
    print("\n🔍 Test d'intégrité de la base de données...")
    
    try:
        from database import db_manager
        
        if not db_manager.connect():
            print("  ❌ Impossible de se connecter à la base de données")
            return False
        
        cursor = db_manager.connection.cursor()
        
        # Test des contraintes de clés étrangères
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        
        if fk_errors:
            print(f"  ❌ {len(fk_errors)} erreurs de clés étrangères trouvées")
            return False
        else:
            print("  ✅ Aucune erreur de clés étrangères")
        
        # Test du nombre d'enregistrements
        tables = ["buildings", "tenants", "assignments", "building_reports", "unit_reports", "invoices"]
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  📊 Table {table}: {count} enregistrements")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test d'intégrité: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST DE L'API SQLITE")
    print("=" * 50)
    
    tests = [
        ("Démarrage du serveur", test_server_startup),
        ("Endpoints des immeubles", test_buildings_endpoints),
        ("Endpoints des factures", test_invoices_endpoints),
        ("Intégrité de la base de données", test_database_integrity)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Test: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: RÉUSSI")
        else:
            print(f"❌ {test_name}: ÉCHOUÉ")
    
    print(f"\n📊 RÉSULTATS: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ Votre API SQLite fonctionne parfaitement")
        return True
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")
        return False

if __name__ == "__main__":
    main()
