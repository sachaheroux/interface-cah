#!/usr/bin/env python3
"""
Script pour tester la connexion avec Sacha
"""

import requests
import json

def test_login():
    url = "http://localhost:8000/api/auth/login"
    
    payload = {
        "email": "sacha.heroux87@gmail.com",
        "mot_de_passe": "Champion2024!"
    }
    
    print("\n" + "="*60)
    print("🔐 TEST DE CONNEXION")
    print("="*60)
    print(f"\n📍 URL: {url}")
    print(f"📧 Email: {payload['email']}")
    print(f"🔑 Mot de passe: {payload['mot_de_passe']}")
    
    try:
        response = requests.post(url, json=payload)
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"\n📄 Réponse:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ CONNEXION RÉUSSIE!")
            print(f"🎟️  Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"👤 Utilisateur: {data.get('user', {})}")
        else:
            print(f"\n❌ ÉCHEC DE CONNEXION")
            print(f"Message: {response.json().get('detail', 'Erreur inconnue')}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Le serveur backend n'est pas démarré sur http://localhost:8000")
        print("💡 Lance le serveur avec: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_login()

