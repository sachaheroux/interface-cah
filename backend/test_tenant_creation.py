#!/usr/bin/env python3
"""
Script de test pour créer un locataire via l'API
"""

import requests
import json

# URL de l'API Render
API_URL = "https://interface-cah-backend.onrender.com"

def test_create_tenant():
    """Tester la création d'un locataire"""
    
    # Données de test
    test_data = {
        "name": "Test Locataire",
        "email": "test@example.com",
        "phone": "819-123-4567",
        "notes": "Test de création",
        "unitId": 1,
        "lease": {
            "startDate": "2025-01-01",
            "endDate": "2025-12-31",
            "monthlyRent": 1000,
            "paymentMethod": "Virement bancaire"
        },
        "moveInDate": "2025-01-01",
        "moveOutDate": "2025-12-31",
        "rentAmount": 1000,
        "leaseStartDate": "2025-01-01",
        "leaseEndDate": "2025-12-31",
        "rentDueDay": 1
    }
    
    print("🧪 Test de création de locataire...")
    print(f"📤 Données envoyées: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/tenants/create-with-assignment",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès!")
            print(f"📋 Réponse: {json.dumps(result, indent=2)}")
        else:
            print("❌ Erreur!")
            print(f"📋 Erreur: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    test_create_tenant()
