#!/usr/bin/env python3
"""
Script pour tester l'endpoint approve-request-email
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def test_approve_endpoint():
    print("\n" + "="*60)
    print("🔍 TEST ENDPOINT APPROVE-REQUEST-EMAIL")
    print("="*60)
    
    # Test avec un ID de demande fictif
    try:
        response = requests.get(f"{RENDER_URL}/api/auth/approve-request-email?request_id=1", 
                               timeout=30)
        print(f"Status: {response.status_code}")
        print("Réponse:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_approve_endpoint()
