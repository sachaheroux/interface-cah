#!/usr/bin/env python3
"""
Script pour vérifier si la colonne dette_restante existe dans la base de données Render
"""

import requests
import json

# URL de l'API Render
API_BASE_URL = "https://interface-cah-backend.onrender.com"

def check_column():
    """Vérifier si la colonne existe via l'API"""
    try:
        print("🔍 Vérification de la colonne dette_restante")
        
        # Essayer de récupérer un immeuble pour voir si la colonne existe
        response = requests.get(f"{API_BASE_URL}/api/buildings")
        
        if response.status_code == 200:
            buildings = response.json()
            if buildings and len(buildings) > 0:
                first_building = buildings[0]
                print("📋 Premier immeuble récupéré:")
                print(json.dumps(first_building, indent=2, default=str))
                
                if 'dette_restante' in first_building:
                    print("✅ La colonne 'dette_restante' existe dans l'API")
                    return True
                else:
                    print("❌ La colonne 'dette_restante' n'existe pas dans l'API")
                    return False
            else:
                print("⚠️ Aucun immeuble trouvé")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def test_migration_again():
    """Essayer la migration à nouveau"""
    try:
        print("\n🔄 Tentative de migration à nouveau...")
        response = requests.post(f"{API_BASE_URL}/api/migrate/dette-restante")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📝 Résultat: {result['message']}")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Vérification de la colonne dette_restante")
    
    # Vérifier si la colonne existe
    column_exists = check_column()
    
    if not column_exists:
        print("\n🔄 La colonne n'existe pas, tentative de migration...")
        migration_success = test_migration_again()
        
        if migration_success:
            print("\n🔍 Vérification après migration...")
            check_column()
    else:
        print("✅ La colonne existe déjà!")
