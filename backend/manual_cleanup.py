#!/usr/bin/env python3
"""
Script pour voir et supprimer manuellement les utilisateurs
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def manual_cleanup():
    print("\n" + "="*60)
    print("🔧 NETTOYAGE MANUEL DES UTILISATEURS")
    print("="*60)
    
    # Test 1: Lister tous les utilisateurs avec détails
    print("\n📝 Test 1: Liste détaillée des utilisateurs")
    try:
        response = requests.get(f"{RENDER_URL}/api/auth/debug/users", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            print(f"Nombre d'utilisateurs: {data.get('total_users', 0)}")
            print("\nDétails des utilisateurs:")
            for i, user in enumerate(users):
                print(f"\n--- Utilisateur {i+1} ---")
                for key, value in user.items():
                    print(f"  {key}: {value}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 2: Supprimer spécifiquement demerskaim@gmail.com
    print("\n📝 Test 2: Suppression spécifique de demerskaim@gmail.com")
    try:
        response = requests.post(f"{RENDER_URL}/api/auth/debug/delete-user-by-email", 
                               json={"email": "demerskaim@gmail.com"}, 
                               timeout=30)
        print(f"Status: {response.status_code}")
        print("Réponse:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    manual_cleanup()
