#!/usr/bin/env python3
"""
Script pour exécuter le setup d'authentification directement sur Render
via un endpoint API temporaire
"""

import requests
import json

RENDER_URL = "https://interface-cah-backend.onrender.com"

def check_health():
    """Vérifie que le backend Render est accessible"""
    try:
        response = requests.get(f"{RENDER_URL}/api/dashboard", timeout=10)
        if response.status_code == 200:
            print("✅ Backend Render accessible")
            return True
        else:
            print(f"❌ Backend répond avec status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def trigger_setup():
    """Déclenche le setup d'authentification sur Render"""
    print("\n" + "="*70)
    print("🚀 EXÉCUTION DU SETUP D'AUTHENTIFICATION SUR RENDER")
    print("="*70)
    
    if not check_health():
        print("\n❌ Le backend Render n'est pas accessible. Attends qu'il redémarre.")
        return
    
    print("\n📡 Appel de l'endpoint /api/setup-authentication...")
    
    try:
        response = requests.post(
            f"{RENDER_URL}/api/setup-authentication",
            timeout=60  # Le setup peut prendre du temps
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SETUP RÉUSSI !\n")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n❌ Erreur durant le setup:")
            print(response.text)
    
    except requests.exceptions.Timeout:
        print("\n⏱️ Timeout - Le setup prend plus de 60 secondes.")
        print("Vérifie les logs Render pour voir s'il continue à s'exécuter.")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    trigger_setup()

