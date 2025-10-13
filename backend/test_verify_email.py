#!/usr/bin/env python3
"""
Script pour tester l'endpoint verify-email et voir le format du token
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def test_verify_email():
    print("\n" + "="*60)
    print("🔍 TEST ENDPOINT VERIFY-EMAIL")
    print("="*60)
    
    # Test avec un email fictif et un code fictif
    test_data = {
        "email": "test@example.com",
        "code": "TEST123"
    }
    
    try:
        response = requests.post(f"{RENDER_URL}/api/auth/verify-email", 
                               json=test_data, 
                               timeout=30)
        print(f"Status: {response.status_code}")
        print("Réponse:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_verify_email()
