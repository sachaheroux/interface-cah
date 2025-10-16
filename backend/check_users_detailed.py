#!/usr/bin/env python3
"""
Script pour vérifier tous les utilisateurs sur Render
"""

import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"

def check_all_users():
    """Vérifier tous les utilisateurs"""
    try:
        print("🔍 Vérification de tous les utilisateurs...")
        
        # Appeler l'endpoint de debug
        response = requests.get(
            f"{RENDER_URL}/api/auth/debug/users",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            users = result.get('users', [])
            
            print(f"📊 Nombre total d'utilisateurs: {len(users)}")
            print("\n" + "="*80)
            
            for user in users:
                print(f"👤 Email: {user.get('email', 'N/A')}")
                print(f"   Nom: {user.get('nom', 'N/A')} {user.get('prenom', 'N/A')}")
                print(f"   Rôle: {user.get('role', 'N/A')}")
                print(f"   Statut: {user.get('statut', 'N/A')}")
                print(f"   Email vérifié: {user.get('email_verifie', 'N/A')}")
                print(f"   ID Compagnie: {user.get('id_compagnie', 'N/A')}")
                print("-" * 40)
                
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    check_all_users()