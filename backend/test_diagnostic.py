#!/usr/bin/env python3
"""
Test de diagnostic détaillé pour identifier les problèmes d'endpoints
"""

import urllib.request
import urllib.parse
import json
import traceback

API_BASE_URL = "http://localhost:8000"

def test_endpoint_detailed(endpoint, method="GET", data=None):
    """Test détaillé d'un endpoint avec gestion d'erreurs complète"""
    print(f"\n🔍 Test détaillé: {method} {endpoint}")
    
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if data:
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data_bytes, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status
            response_data = response.read().decode('utf-8')
            
            print(f"  ✅ Status: {status}")
            print(f"  📄 Response length: {len(response_data)} caractères")
            
            try:
                json_data = json.loads(response_data)
                print(f"  📊 JSON valide: {type(json_data)}")
                if isinstance(json_data, dict):
                    print(f"  🔑 Clés: {list(json_data.keys())}")
                elif isinstance(json_data, list):
                    print(f"  📋 Éléments: {len(json_data)}")
            except json.JSONDecodeError:
                print(f"  ⚠️ Réponse non-JSON: {response_data[:200]}...")
            
            return True, status, response_data
            
    except urllib.error.HTTPError as e:
        print(f"  ❌ Erreur HTTP {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"  📄 Corps d'erreur: {error_body}")
        except:
            pass
        return False, e.code, str(e)
        
    except Exception as e:
        print(f"  ❌ Erreur: {type(e).__name__}: {e}")
        print(f"  📍 Traceback: {traceback.format_exc()}")
        return False, None, str(e)

def test_health_endpoints():
    """Tester les endpoints de santé"""
    print("\n🏥 Test des endpoints de santé")
    
    endpoints = [
        "/health",
        "/api/health",
        "/docs",
        "/openapi.json"
    ]
    
    for endpoint in endpoints:
        success, status, response = test_endpoint_detailed(endpoint)
        if not success:
            print(f"  ⚠️ {endpoint} non accessible")

def test_buildings_endpoints():
    """Tester les endpoints des immeubles"""
    print("\n🏢 Test des endpoints des immeubles")
    
    # Test GET /api/buildings
    success, status, response = test_endpoint_detailed("/api/buildings")
    
    if success and status == 200:
        print("  ✅ GET /api/buildings fonctionne")
        
        # Test POST /api/buildings
        test_building = {
            "name": "Test Building Diagnostic",
            "address": {
                "street": "123 Test Street",
                "city": "Montreal",
                "province": "QC",
                "postalCode": "H1A 1A1",
                "country": "Canada"
            },
            "type": "Residential",
            "units": 1,
            "floors": 1,
            "yearBuilt": 2023,
            "totalArea": 100,
            "notes": "Test building for diagnostic"
        }
        
        success, status, response = test_endpoint_detailed("/api/buildings", "POST", test_building)
        
        if success and status == 200:
            print("  ✅ POST /api/buildings fonctionne")
            try:
                building_data = json.loads(response)
                building_id = building_data.get("id")
                if building_id:
                    print(f"  🆔 Building ID: {building_id}")
                    
                    # Test GET /api/buildings/{id}
                    success, status, response = test_endpoint_detailed(f"/api/buildings/{building_id}")
                    if success and status == 200:
                        print("  ✅ GET /api/buildings/{id} fonctionne")
                    else:
                        print("  ❌ GET /api/buildings/{id} échoue")
            except Exception as e:
                print(f"  ❌ Erreur parsing POST response: {e}")
        else:
            print("  ❌ POST /api/buildings échoue")
    else:
        print("  ❌ GET /api/buildings échoue")

def test_invoices_endpoints():
    """Tester les endpoints des factures"""
    print("\n💰 Test des endpoints des factures")
    
    # Test GET /api/invoices/constants
    success, status, response = test_endpoint_detailed("/api/invoices/constants")
    
    if success and status == 200:
        print("  ✅ GET /api/invoices/constants fonctionne")
    else:
        print("  ❌ GET /api/invoices/constants échoue")
    
    # Test GET /api/invoices
    success, status, response = test_endpoint_detailed("/api/invoices")
    
    if success and status == 200:
        print("  ✅ GET /api/invoices fonctionne")
    else:
        print("  ❌ GET /api/invoices échoue")

def test_database_direct():
    """Test direct de la base de données"""
    print("\n🗄️ Test direct de la base de données")
    
    try:
        from database import db_manager
        
        if not db_manager.connect():
            print("  ❌ Impossible de se connecter à la base de données")
            return False
        
        cursor = db_manager.connection.cursor()
        
        # Test des tables
        tables = ["buildings", "tenants", "assignments", "building_reports", "unit_reports", "invoices"]
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  📊 Table {table}: {count} enregistrements")
            except Exception as e:
                print(f"  ❌ Erreur table {table}: {e}")
        
        # Test d'insertion simple
        try:
            cursor.execute("""
                INSERT INTO buildings (name, address_street, address_city, address_province, address_postal_code, address_country, type, units, floors, year_built, total_area, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, ("Test Direct DB", "123 Test Street", "Montreal", "QC", "H1A 1A1", "Canada", "Test", 1, 1, 2023, 100, "Test direct"))
            
            building_id = cursor.lastrowid
            print(f"  ✅ Insertion test réussie, ID: {building_id}")
            
            # Test de récupération
            cursor.execute("SELECT * FROM buildings WHERE id = ?", (building_id,))
            building = cursor.fetchone()
            if building:
                print(f"  ✅ Récupération test réussie: {building[1]}")
            
            # Nettoyage
            cursor.execute("DELETE FROM buildings WHERE id = ?", (building_id,))
            print("  🧹 Test nettoyé")
            
        except Exception as e:
            print(f"  ❌ Erreur test insertion: {e}")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur test base de données: {e}")
        return False

def main():
    """Fonction principale de diagnostic"""
    print("🔍 DIAGNOSTIC DÉTAILLÉ DE L'API SQLITE")
    print("=" * 50)
    
    tests = [
        ("Endpoints de santé", test_health_endpoints),
        ("Endpoints des immeubles", test_buildings_endpoints),
        ("Endpoints des factures", test_invoices_endpoints),
        ("Base de données directe", test_database_direct)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            print(f"📍 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
