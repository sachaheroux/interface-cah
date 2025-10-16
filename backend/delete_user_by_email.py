#!/usr/bin/env python3
"""
Script pour supprimer un utilisateur par email depuis Render
"""

import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"
EMAIL_TO_DELETE = "sacha.heroux@uqtr.ca"

def delete_user_by_email():
    """Supprimer un utilisateur par email"""
    try:
        print(f"🗑️ Suppression de l'utilisateur: {EMAIL_TO_DELETE}")
        
        # Appeler l'endpoint de suppression
        response = requests.post(
            f"{RENDER_URL}/api/auth/debug/delete-user-by-email",
            json={"email": EMAIL_TO_DELETE},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Succès: {result.get('message', 'Utilisateur supprimé')}")
        elif response.status_code == 404:
            print(f"⚠️ Utilisateur non trouvé: {EMAIL_TO_DELETE}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    delete_user_by_email()
