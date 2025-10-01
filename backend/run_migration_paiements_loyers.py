#!/usr/bin/env python3
"""
Script pour exécuter la migration des paiements de loyers
"""

import requests
import os

def run_migration():
    """Exécuter la migration des paiements de loyers"""
    try:
        # URL de l'API Render
        api_url = "https://interface-cah-backend.onrender.com"
        
        print("🔄 Exécution de la migration des paiements de loyers...")
        
        # Appeler l'endpoint de migration
        response = requests.post(f"{api_url}/api/migrate/paiements-loyers")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            return True
        else:
            print(f"❌ Erreur lors de la migration: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de la migration: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n🎉 Migration terminée avec succès!")
    else:
        print("\n💥 Migration échouée!")
