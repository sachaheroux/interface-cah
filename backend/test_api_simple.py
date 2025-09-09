#!/usr/bin/env python3
"""
Test simple de l'API SQLite sans dépendances externes
Usage: python test_api_simple.py
"""

import urllib.request
import urllib.parse
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

def make_request(url, method="GET", data=None):
    """Faire une requête HTTP simple"""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, response.read().decode('utf-8')
    except Exception as e:
        return None, str(e)

def test_server_startup():
    """Tester si le serveur démarre correctement"""
    print("🚀 Test de démarrage du serveur...")
    
    status, response = make_request(f"{API_BASE_URL}/health")
    if status == 200:
        print("✅ Serveur démarré avec succès")
        return True
    else:
        print(f"❌ Serveur non accessible: {response}")
        print("💡 Assurez-vous que le serveur est démarré avec: uvicorn main:app --reload")
        return False

def test_buildings_endpoints():
    """Tester les endpoints des immeubles"""
    print("\n🏢 Test des endpoints des immeubles...")
    
    try:
        # Test GET /api/buildings
        print("  Test GET /api/buildings...")
        status, response = make_request(f"{API_BASE_URL}/api/buildings")
        if status == 200:
            buildings = json.loads(response)
            print(f"  ✅ Récupéré {len(buildings)} immeubles")
        else:
            print(f"  ❌ Erreur GET buildings: {status}")
            return False
        
        # Test POST /api/buildings (créer un immeuble de test)
        print("  Test POST /api/buildings...")
        test_building = {
            "name": "Immeuble Test SQLite Simple",
            "address": {
                "street": "123 Rue Test Simple",
                "city": "Montréal",
                "province": "QC",
                "postalCode": "H1A 1A1",
                "country": "Canada"
            },
            "type": "Résidentiel",
            "units": 3,
            "floors": 2,
            "yearBuilt": 2023,
            "totalArea": 800,
            "notes": "Immeuble de test simple pour SQLite"
        }
        
        status, response = make_request(f"{API_BASE_URL}/api/buildings", "POST", test_building)
        if status == 200:
            created_building = json.loads(response)
            building_id = created_building["id"]
            print(f"  ✅ Immeuble créé avec ID: {building_id}")
            
            # Test GET /api/buildings/{id}
            print("  Test GET /api/buildings/{id}...")
            status, response = make_request(f"{API_BASE_URL}/api/buildings/{building_id}")
            if status == 200:
                print("  ✅ Immeuble récupéré par ID")
            else:
                print(f"  ❌ Erreur GET building by ID: {status}")
                return False
            
            # Test PUT /api/buildings/{id}
            print("  Test PUT /api/buildings/{id}...")
            update_data = {"name": "Immeuble Test SQLite Simple Modifié"}
            status, response = make_request(f"{API_BASE_URL}/api/buildings/{building_id}", "PUT", update_data)
            if status == 200:
                print("  ✅ Immeuble mis à jour")
            else:
                print(f"  ❌ Erreur PUT building: {status}")
                return False
            
            # Test DELETE /api/buildings/{id}
            print("  Test DELETE /api/buildings/{id}...")
            status, response = make_request(f"{API_BASE_URL}/api/buildings/{building_id}", "DELETE")
            if status == 200:
                print("  ✅ Immeuble supprimé")
            else:
                print(f"  ❌ Erreur DELETE building: {status}")
                return False
            
        else:
            print(f"  ❌ Erreur POST building: {status}")
            print(f"  Détails: {response}")
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
        status, response = make_request(f"{API_BASE_URL}/api/invoices/constants")
        if status == 200:
            constants = json.loads(response)
            print(f"  ✅ Constantes récupérées: {len(constants.get('categories', {}))} catégories")
        else:
            print(f"  ❌ Erreur GET constants: {status}")
            return False
        
        # Test GET /api/invoices
        print("  Test GET /api/invoices...")
        status, response = make_request(f"{API_BASE_URL}/api/invoices")
        if status == 200:
            invoices = json.loads(response)
            print(f"  ✅ Récupéré {len(invoices.get('data', []))} factures")
        else:
            print(f"  ❌ Erreur GET invoices: {status}")
            return False
        
        # Test POST /api/invoices (créer une facture de test)
        print("  Test POST /api/invoices...")
        test_invoice = {
            "invoiceNumber": f"SIMPLE-TEST-{int(time.time())}",
            "category": "municipal_taxes",
            "source": "Ville de Montréal",
            "date": datetime.now().isoformat(),
            "amount": 1200.75,
            "currency": "CAD",
            "paymentType": "bank_transfer",
            "buildingId": 1,
            "notes": "Facture de test simple pour SQLite"
        }
        
        status, response = make_request(f"{API_BASE_URL}/api/invoices", "POST", test_invoice)
        if status == 200:
            created_invoice = json.loads(response)
            invoice_id = created_invoice["data"]["id"]
            print(f"  ✅ Facture créée avec ID: {invoice_id}")
            
            # Test GET /api/invoices/{id}
            print("  Test GET /api/invoices/{id}...")
            status, response = make_request(f"{API_BASE_URL}/api/invoices/{invoice_id}")
            if status == 200:
                print("  ✅ Facture récupérée par ID")
            else:
                print(f"  ❌ Erreur GET invoice by ID: {status}")
                return False
            
        else:
            print(f"  ❌ Erreur POST invoice: {status}")
            print(f"  Détails: {response}")
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
    print("🧪 TEST SIMPLE DE L'API SQLITE")
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
