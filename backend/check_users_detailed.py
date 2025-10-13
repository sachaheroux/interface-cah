#!/usr/bin/env python3
"""
Script pour voir exactement qui est dans la base de données
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def check_users():
    print("\n" + "="*60)
    print("👥 VÉRIFICATION DÉTAILLÉE DES UTILISATEURS")
    print("="*60)
    
    try:
        response = requests.get(f"{RENDER_URL}/api/auth/debug/users", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"Nombre d'utilisateurs: {len(users)}")
            print("\nDétails des utilisateurs:")
            for i, user in enumerate(users):
                print(f"\n--- Utilisateur {i+1} ---")
                for key, value in user.items():
                    print(f"  {key}: {value}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    check_users()
