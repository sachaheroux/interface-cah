#!/usr/bin/env python3
"""
Script pour tester directement l'API et voir l'erreur exacte
"""

import requests
import json

# Configuration
RENDER_API_BASE = "https://interface-cah-backend.onrender.com"

def test_api_direct():
    """Tester l'API directement"""
    print("🔍 Test direct de l'API Render...")
    
    # Test 1: Constantes
    print("\n1. Test des constantes...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/transactions-constants")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Types: {data.get('types', [])}")
            print(f"   ✅ Catégories: {data.get('categories', [])}")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Récupération des transactions (avec détails de l'erreur)
    print("\n2. Test de récupération des transactions...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/transactions")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Transactions: {len(data.get('data', []))} trouvées")
        else:
            print(f"   ❌ Erreur détaillée:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Text: {response.text}")
            
            # Essayer de parser le JSON de l'erreur
            try:
                error_data = response.json()
                print(f"   Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Response n'est pas du JSON valide")
                
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Test des autres endpoints
    print("\n3. Test des autres endpoints...")
    
    endpoints = [
        ("/api/buildings", "Immeubles"),
        ("/api/units", "Unités"),
        ("/api/tenants", "Locataires"),
        ("/api/leases", "Baux")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{RENDER_API_BASE}{endpoint}")
            print(f"   {name}: {response.status_code}")
            if response.status_code != 200:
                print(f"      Erreur: {response.text[:200]}...")
        except Exception as e:
            print(f"   {name}: Exception - {e}")

if __name__ == "__main__":
    test_api_direct()
