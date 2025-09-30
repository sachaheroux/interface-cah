#!/usr/bin/env python3
"""
Script pour tester l'endpoint de debug
"""

import requests
import json

# URL de l'API Render
API_BASE_URL = "https://interface-cah-backend.onrender.com"

def test_debug_endpoint():
    """Tester l'endpoint de debug"""
    try:
        print("🔍 Test de l'endpoint de debug")
        
        # Données de test
        test_data = {
            "dette_restante": 300000
        }
        
        print(f"📤 Envoi des données: {json.dumps(test_data, indent=2)}")
        
        # Appeler l'endpoint de debug
        response = requests.post(f"{API_BASE_URL}/api/debug/update-building?building_id=1", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Debug terminé!")
            print(f"📥 Réponse: {json.dumps(result, indent=2, default=str)}")
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    test_debug_endpoint()
