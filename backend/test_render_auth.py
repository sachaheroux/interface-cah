#!/usr/bin/env python3
"""
Script pour tester l'authentification sur Render
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def test_render_auth():
    print("\n" + "="*60)
    print("🔐 TEST AUTHENTIFICATION RENDER")
    print("="*60)
    
    # Test 1: Connexion Sacha
    print("\n📝 Test 1: Connexion avec Sacha")
    print(f"URL: {RENDER_URL}/api/auth/login")
    
    payload = {
        "email": "sacha.heroux87@gmail.com",
        "mot_de_passe": "Champion2024!"
    }
    
    try:
        response = requests.post(f"{RENDER_URL}/api/auth/login", json=payload, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ CONNEXION RÉUSSIE sur Render!")
            print(f"Token: {data.get('token', 'N/A')[:50]}...")
            print(f"Utilisateur: {data.get('user', {}).get('email')}")
            print(f"Compagnie: {data.get('user', {}).get('compagnie', {}).get('nom_compagnie')}")
        else:
            print(f"❌ ÉCHEC: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ TIMEOUT: Le serveur Render met trop de temps à répondre (peut-être en train de démarrer)")
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR: Impossible de se connecter à Render")
    except Exception as e:
        print(f"❌ ERREUR: {e}")
    
    # Test 2: Liste des compagnies
    print("\n📝 Test 2: Liste des compagnies disponibles")
    print(f"URL: {RENDER_URL}/api/auth/companies")
    
    try:
        response = requests.get(f"{RENDER_URL}/api/auth/companies", timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            companies = data.get('companies', [])
            print(f"✅ {len(companies)} compagnie(s) trouvée(s):")
            for company in companies:
                print(f"  - {company.get('nom_compagnie')} (ID: {company.get('id_compagnie')})")
        else:
            print(f"❌ ÉCHEC: {response.text}")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_render_auth()

