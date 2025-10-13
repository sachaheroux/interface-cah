#!/usr/bin/env python3
"""
Script pour approuver manuellement un utilisateur
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def approve_user_manually():
    print("\n" + "="*60)
    print("🔧 APPROBATION MANUELLE D'UTILISATEUR")
    print("="*60)
    
    email = "demerskaim@gmail.com"
    
    try:
        response = requests.post(f"{RENDER_URL}/api/auth/debug/approve-user-by-email", 
                               json={"email": email}, 
                               timeout=30)
        print(f"Status: {response.status_code}")
        print("Réponse:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"\n✅ Utilisateur {email} approuvé avec succès !")
                print(f"📧 Email envoyé: {data.get('email_sent', False)}")
            else:
                print(f"❌ Erreur: {data.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    approve_user_manually()
