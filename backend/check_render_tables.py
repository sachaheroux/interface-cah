#!/usr/bin/env python3
"""
Vérifier les tables sur Render
"""

import requests
import json

# URL de l'API Render
API_BASE_URL = "https://interface-cah-backend.onrender.com"

def check_render_tables():
    """Vérifier quelles tables existent sur Render"""
    
    print("🔍 Vérification des tables sur Render")
    print("=" * 50)
    
    # Tester différents endpoints pour voir quelles tables existent
    endpoints_to_test = [
        ("/api/buildings", "immeubles"),
        ("/api/units", "unites"), 
        ("/api/tenants", "locataires"),
        ("/api/invoices", "factures")
    ]
    
    for endpoint, table_name in endpoints_to_test:
        try:
            print(f"\n📋 Test de l'endpoint {endpoint} (table {table_name})...")
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    count = len(data['data'])
                    print(f"✅ {table_name}: {count} enregistrements")
                else:
                    print(f"✅ {table_name}: Réponse reçue")
            else:
                print(f"❌ {table_name}: Erreur {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ {table_name}: Exception - {e}")
    
    # Tester spécifiquement la création d'un locataire simple
    print(f"\n🧪 Test de création de locataire simple...")
    try:
        simple_tenant = {
            "nom": "Test",
            "prenom": "Simple", 
            "email": "test@simple.com",
            "telephone": "514-555-0000",
            "statut": "actif",
            "notes": "Test simple"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/tenants",
            json=simple_tenant,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Réponse création simple: {response.status_code}")
        if response.status_code != 200:
            print(f"   Erreur: {response.text}")
        else:
            print(f"   Succès: {response.json()}")
            
    except Exception as e:
        print(f"❌ Erreur test simple: {e}")

if __name__ == "__main__":
    check_render_tables()
