#!/usr/bin/env python3
"""
Script pour exécuter la migration de la colonne dette_restante via l'API
"""

import requests
import json

# URL de l'API Render
API_BASE_URL = "https://interface-cah-backend.onrender.com"

def run_migration():
    """Exécuter la migration via l'API"""
    try:
        print("🚀 Début de la migration: Ajout de la colonne dette_restante")
        print(f"📡 Appel de l'API: {API_BASE_URL}/api/migrate/dette-restante")
        
        response = requests.post(f"{API_BASE_URL}/api/migrate/dette-restante")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            print("🎉 Migration terminée avec succès!")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    
    if not success:
        print("💥 Migration échouée!")
        exit(1)
