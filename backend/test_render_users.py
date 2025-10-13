#!/usr/bin/env python3
"""
Script pour voir les utilisateurs sur Render
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def test_users():
    print("\n" + "="*60)
    print("👥 UTILISATEURS SUR RENDER")
    print("="*60)
    
    try:
        response = requests.get(f"{RENDER_URL}/api/auth/debug/users", timeout=30)
        
        print(f"Status: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Total utilisateurs: {data.get('total_users', 0)}\n")
            
            users = data.get('users', [])
            if users:
                for user in users:
                    print(f"👤 Utilisateur #{user.get('id')}:")
                    print(f"   Email: {user.get('email')}")
                    print(f"   Nom: {user.get('prenom')} {user.get('nom')}")
                    print(f"   Rôle: {user.get('role')}")
                    print(f"   Statut: {user.get('statut')}")
                    print(f"   Email vérifié: {user.get('email_verifie')}")
                    print(f"   Admin principal: {user.get('est_admin_principal')}")
                    print(f"   Compagnie ID: {user.get('id_compagnie')}")
                    print()
            else:
                print("⚠️ AUCUN UTILISATEUR TROUVÉ!")
                print("   → L'utilisateur Sacha n'a pas été créé automatiquement")
        else:
            print(f"❌ Erreur {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    test_users()

