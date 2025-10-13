#!/usr/bin/env python3
"""
Script pour créer l'utilisateur Sacha sur Render
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def create_sacha():
    print("\n" + "="*60)
    print("👤 CRÉATION DE L'UTILISATEUR SACHA SUR RENDER")
    print("="*60)
    
    # Appeler l'endpoint de création
    print(f"\n📝 Appel: {RENDER_URL}/api/auth/debug/create-sacha")
    
    try:
        response = requests.post(f"{RENDER_URL}/api/auth/debug/create-sacha", timeout=30)
        
        print(f"Status: {response.status_code}\n")
        
        data = response.json()
        print("Réponse:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get("success"):
            print("\n✅ UTILISATEUR SACHA CRÉÉ AVEC SUCCÈS!")
            
            # Tester la connexion
            print("\n" + "-"*60)
            print("🔐 TEST DE CONNEXION")
            print("-"*60)
            
            login_response = requests.post(
                f"{RENDER_URL}/api/auth/login",
                json={
                    "email": "sacha.heroux87@gmail.com",
                    "mot_de_passe": "Champion2024!"
                },
                timeout=30
            )
            
            print(f"Status: {login_response.status_code}\n")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print("✅ CONNEXION RÉUSSIE!")
                print(f"Token: {login_data.get('token', 'N/A')[:50]}...")
                print(f"Utilisateur: {login_data.get('user', {}).get('email')}")
            else:
                print(f"❌ Échec connexion: {login_response.text}")
        else:
            print(f"\n⚠️ {data.get('message', data.get('error', 'Erreur inconnue'))}")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    create_sacha()

