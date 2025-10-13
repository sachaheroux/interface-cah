#!/usr/bin/env python3
"""
Script pour tester l'envoi d'email sur Render
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def test_email():
    print("\n" + "="*60)
    print("📧 TEST ENVOI EMAIL SUR RENDER")
    print("="*60)
    
    # Test 1: Vérifier les variables d'environnement
    print("\n📝 Test 1: Variables d'environnement")
    try:
        response = requests.get(f"{RENDER_URL}/api/auth/debug/env-check", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Variables SMTP:")
            print(f"  SMTP_SERVER: {data.get('SMTP_SERVER', 'NON DÉFINIE')}")
            print(f"  SMTP_PORT: {data.get('SMTP_PORT', 'NON DÉFINIE')}")
            print(f"  SMTP_USERNAME: {data.get('SMTP_USERNAME', 'NON DÉFINIE')}")
            print(f"  SMTP_PASSWORD: {'***' if data.get('SMTP_PASSWORD') else 'NON DÉFINIE'}")
            print(f"  FROM_EMAIL: {data.get('FROM_EMAIL', 'NON DÉFINIE')}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 2: Envoyer un email de test
    print("\n📝 Test 2: Envoi email de test")
    try:
        response = requests.post(f"{RENDER_URL}/api/auth/debug/send-test-email", 
                               json={"email": "sacha.heroux87@gmail.com"}, 
                               timeout=30)
        print(f"Status: {response.status_code}")
        print("Réponse:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_email()

