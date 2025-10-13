#!/usr/bin/env python3
"""
Script pour tester l'endpoint setup-company et voir l'erreur exacte
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def test_setup_company():
    print("\n" + "="*60)
    print("🔍 TEST ENDPOINT SETUP-COMPANY")
    print("="*60)
    
    # Test avec des données fictives
    test_data = {
        "action": "join",
        "code_acces": "YRX-6HF",
        "role": "employe"
    }
    
    # Headers avec un token fictif
    headers = {
        "Authorization": "Bearer fake_token_for_test",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{RENDER_URL}/api/auth/setup-company", 
                               json=test_data, 
                               headers=headers,
                               timeout=30)
        print(f"Status: {response.status_code}")
        print("Réponse:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_setup_company()
