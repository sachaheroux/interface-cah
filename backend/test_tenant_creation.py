#!/usr/bin/env python3
"""
Test simple de création de locataire
"""

import requests
import json

def test_tenant_creation():
    """Tester la création d'un locataire"""
    print("👤 TEST DE CRÉATION DE LOCATAIRE")
    print("=" * 40)
    
    RENDER_URL = "https://interface-cah-backend.onrender.com"
    
    try:
        # Créer un locataire simple
        tenant_data = {
            "name": "Test Simple",
            "email": "test@example.com",
            "phone": "(514) 555-0123",
            "status": "active"
        }
        
        print("1️⃣ Création du locataire...")
        response = requests.post(f"{RENDER_URL}/api/tenants", 
                               json=tenant_data, 
                               headers={'Content-Type': 'application/json'}, 
                               timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Réponse JSON: {json.dumps(result, indent=2)}")
                
                # Vérifier la structure
                if 'data' in result:
                    tenant = result['data']
                    if 'id' in tenant:
                        print(f"   ✅ Locataire créé avec ID: {tenant['id']}")
                        return True
                    else:
                        print(f"   ❌ Pas d'ID dans la réponse: {tenant}")
                        return False
                else:
                    print(f"   ❌ Pas de 'data' dans la réponse: {result}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ Erreur JSON: {e}")
                print(f"   📝 Réponse brute: {response.text}")
                return False
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
            print(f"   📝 Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    success = test_tenant_creation()
    
    if success:
        print("\n✅ Test réussi !")
    else:
        print("\n❌ Test échoué")

if __name__ == "__main__":
    main()