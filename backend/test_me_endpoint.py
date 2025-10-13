#!/usr/bin/env python3
"""
Script pour tester l'endpoint /api/auth/me
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def test_me_endpoint():
    print("\n" + "="*60)
    print("🔍 TEST ENDPOINT /api/auth/me")
    print("="*60)
    
    # Test avec un token fictif
    headers = {
        "Authorization": "Bearer fake_token_for_test",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{RENDER_URL}/api/auth/me", 
                               headers=headers,
                               timeout=30)
        print(f"Status: {response.status_code}")
        print("Headers:", dict(response.headers))
        print("Réponse:")
        print(response.text[:500])  # Premiers 500 caractères
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_me_endpoint()
