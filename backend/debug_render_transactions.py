#!/usr/bin/env python3
"""
Script pour déboguer l'erreur 500 sur les transactions Render
"""

import requests
import json

# Configuration Render
RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def debug_transactions():
    """Déboguer l'erreur des transactions"""
    
    try:
        print("🔍 Débogage des transactions Render...")
        print("=" * 50)
        
        # 1. Tester l'endpoint des constantes (qui fonctionne)
        print("✅ Test des constantes...")
        response = requests.get(f"{RENDER_API_URL}/api/transactions/constants", timeout=30)
        if response.status_code == 200:
            constants = response.json()
            print(f"   Constantes OK: {len(constants)} types")
        else:
            print(f"   Erreur constantes: {response.status_code}")
        
        # 2. Tester l'endpoint des transactions (qui échoue)
        print("\n❌ Test des transactions...")
        response = requests.get(f"{RENDER_API_URL}/api/transactions", timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            try:
                error_detail = response.json()
                print(f"   Erreur détail: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Erreur texte: {response.text}")
        
        # 3. Tester la création d'une transaction
        print("\n🧪 Test de création de transaction...")
        test_transaction = {
            "id_immeuble": 1,
            "type_transaction": "test",
            "montant": 100.0,
            "description": "Test transaction",
            "date_transaction": "2025-01-17",
            "methode_paiement": "virement",
            "statut": "en_attente",
            "reference": "TEST001"
        }
        
        response = requests.post(f"{RENDER_API_URL}/api/transactions", 
                               json=test_transaction, timeout=30)
        print(f"   Status création: {response.status_code}")
        
        if response.status_code != 200:
            try:
                error_detail = response.json()
                print(f"   Erreur création: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Erreur création texte: {response.text}")
        
        # 4. Vérifier les autres endpoints qui fonctionnent
        print("\n✅ Vérification des autres endpoints...")
        working_endpoints = [
            "/api/buildings",
            "/api/units", 
            "/api/tenants",
            "/api/leases"
        ]
        
        for endpoint in working_endpoints:
            try:
                response = requests.get(f"{RENDER_API_URL}{endpoint}", timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    count = len(data.get('data', [])) if isinstance(data, dict) else len(data)
                    print(f"   ✅ {endpoint}: {count} enregistrements")
                else:
                    print(f"   ❌ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ {endpoint}: {e}")
        
        print("\n🔍 Diagnostic terminé!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Diagnostic des transactions Render")
    print("=" * 50)
    
    success = debug_transactions()
    
    if success:
        print("\n🎉 Diagnostic terminé!")
    else:
        print("\n💥 Diagnostic échoué!")
