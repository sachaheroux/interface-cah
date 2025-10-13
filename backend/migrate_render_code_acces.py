#!/usr/bin/env python3
"""
Script pour migrer le code d'accès sur Render
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def migrate_render():
    print("\n" + "="*60)
    print("🔧 MIGRATION RENDER: Ajout code d'accès")
    print("="*60)
    
    try:
        response = requests.post(f"{RENDER_URL}/api/auth/debug/migrate-code-acces", timeout=30)
        
        print(f"Status: {response.status_code}\n")
        
        data = response.json()
        print("Réponse:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get("success"):
            print(f"\n✅ MIGRATION RÉUSSIE!")
            print(f"🎟️ Code d'accès CAH Immobilier: {data.get('code_acces')}")
            print(f"\n📋 Instructions:")
            print(f"1. Note ce code: {data.get('code_acces')}")
            print(f"2. On va l'ajouter dans le formulaire d'inscription")
            print(f"3. Les nouveaux utilisateurs pourront rejoindre avec ce code")
        else:
            print(f"\n❌ ÉCHEC: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    migrate_render()

