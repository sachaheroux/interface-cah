#!/usr/bin/env python3
"""
Test simple de création de locataire
"""

import requests
import json

# URL de l'API Render
API_BASE_URL = "https://interface-cah-backend.onrender.com"

def test_simple_tenant():
    """Test simple de création de locataire"""
    
    print("🧪 Test simple de création de locataire")
    print("=" * 50)
    
    # Test avec l'endpoint simple /api/tenants
    tenant_data = {
        "id_unite": 2,
        "nom": "Test",
        "prenom": "User",
        "email": "test@email.com",
        "telephone": "514-999-9999",
        "statut": "actif",
        "notes": "Test simple"
    }
    
    print(f"📤 Données envoyées à /api/tenants:")
    print(f"   - Nom: {tenant_data['nom']}")
    print(f"   - Prénom: {tenant_data['prenom']}")
    print(f"   - Email: {tenant_data['email']}")
    print(f"   - Téléphone: {tenant_data['telephone']}")
    print(f"   - ID Unité: {tenant_data['id_unite']}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/tenants",
            json=tenant_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Réponse reçue:")
        print(f"   - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Locataire créé avec succès!")
            print(f"   - Données: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Erreur:")
            print(f"   - Status: {response.status_code}")
            print(f"   - Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_simple_tenant()
