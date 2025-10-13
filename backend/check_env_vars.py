#!/usr/bin/env python3
"""
Script pour vérifier les variables d'environnement sur Render
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def check_env_vars():
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION VARIABLES D'ENVIRONNEMENT")
    print("="*60)
    
    try:
        response = requests.get(f"{RENDER_URL}/api/auth/debug/env-check", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Variables d'environnement:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    check_env_vars()
