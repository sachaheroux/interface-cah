#!/usr/bin/env python3
"""
Script pour nettoyer les anciennes demandes d'accès
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def cleanup_old_requests():
    print("\n" + "="*60)
    print("🧹 NETTOYAGE DES ANCIENNES DEMANDES D'ACCÈS")
    print("="*60)
    
    # Test 1: Lister tous les utilisateurs
    print("\n📝 Test 1: Lister tous les utilisateurs")
    try:
        response = requests.get(f"{RENDER_URL}/api/auth/debug/users", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"Nombre d'utilisateurs: {len(users)}")
            for user in users:
                print(f"  - {user['email']} | Statut: {user['statut']} | Compagnie: {user.get('id_compagnie', 'N/A')}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 2: Supprimer les utilisateurs en attente (sauf Sacha)
    print("\n📝 Test 2: Supprimer les utilisateurs en attente")
    try:
        response = requests.post(f"{RENDER_URL}/api/auth/debug/cleanup-pending-users", 
                               timeout=30)
        print(f"Status: {response.status_code}")
        print("Réponse:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    cleanup_old_requests()
