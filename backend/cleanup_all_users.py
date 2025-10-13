#!/usr/bin/env python3
"""
Script pour nettoyer complètement la base de données d'authentification
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def cleanup_all_users():
    print("\n" + "="*60)
    print("🧹 NETTOYAGE COMPLET DE LA BASE D'AUTHENTIFICATION")
    print("="*60)
    
    # Test 1: Lister tous les utilisateurs avant nettoyage
    print("\n📝 Test 1: Utilisateurs avant nettoyage")
    try:
        response = requests.get(f"{RENDER_URL}/api/auth/debug/users", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"Nombre d'utilisateurs: {len(users)}")
            for i, user in enumerate(users):
                print(f"  {i+1}. {user.get('email', 'N/A')} | Statut: {user.get('statut', 'N/A')}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 2: Supprimer TOUS les utilisateurs (sauf Sacha)
    print("\n📝 Test 2: Suppression de tous les utilisateurs")
    try:
        response = requests.post(f"{RENDER_URL}/api/auth/debug/cleanup-all-users", 
                               timeout=30)
        print(f"Status: {response.status_code}")
        print("Réponse:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 3: Vérifier après nettoyage
    print("\n📝 Test 3: Utilisateurs après nettoyage")
    try:
        response = requests.get(f"{RENDER_URL}/api/auth/debug/users", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"Nombre d'utilisateurs: {len(users)}")
            for i, user in enumerate(users):
                print(f"  {i+1}. {user.get('email', 'N/A')} | Statut: {user.get('statut', 'N/A')}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    cleanup_all_users()
