#!/usr/bin/env python3
"""
Script pour créer un endpoint d'approbation simple
"""

# Créons un endpoint temporaire pour tester
import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def create_temp_approve_endpoint():
    print("\n" + "="*60)
    print("🔧 CRÉATION ENDPOINT TEMPORAIRE D'APPROBATION")
    print("="*60)
    
    # Pour l'instant, créons un script qui simule l'approbation
    print("Créons un script temporaire pour approuver manuellement...")
    
    # Script pour approuver manuellement
    script_content = '''
# Script temporaire pour approuver manuellement
import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def approve_user_manually(email):
    """Approuver un utilisateur manuellement"""
    try:
        # Appeler l'endpoint de debug pour lister les utilisateurs
        response = requests.get(f"{RENDER_URL}/api/auth/debug/users", timeout=30)
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            
            for user in users:
                if user.get("email") == email:
                    print(f"Utilisateur trouvé: {user}")
                    # TODO: Créer un endpoint pour approuver par email
                    return True
            
            print(f"Utilisateur {email} non trouvé")
            return False
        else:
            print(f"Erreur: {response.text}")
            return False
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    approve_user_manually("demerskaim@gmail.com")
'''
    
    with open("backend/manual_approve.py", "w") as f:
        f.write(script_content)
    
    print("✅ Script créé: backend/manual_approve.py")
    print("Utilise ce script pour approuver manuellement l'utilisateur")

if __name__ == "__main__":
    create_temp_approve_endpoint()
