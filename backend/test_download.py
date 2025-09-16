#!/usr/bin/env python3
"""
Script de test pour vérifier la connectivité et les données
"""

import requests
import json
from datetime import datetime

# Configuration
RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def test_api_connectivity():
    """Tester la connectivité à l'API Render"""
    print("🔄 Test de connectivité à l'API Render...")
    
    try:
        # Test de base
        response = requests.get(f"{RENDER_API_URL}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        
        # Test des endpoints principaux
        endpoints = [
            "/api/buildings",
            "/api/units", 
            "/api/tenants",
            "/api/invoices"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{RENDER_API_URL}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint}: {len(data)} enregistrements")
                else:
                    print(f"⚠️  {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connectivité: {e}")
        return False

def test_database_structure():
    """Tester la structure de la base de données"""
    print("\n🔄 Test de la structure de la base de données...")
    
    try:
        # Tester l'endpoint buildings
        response = requests.get(f"{RENDER_API_URL}/api/buildings", timeout=10)
        
        if response.status_code == 200:
            buildings = response.json()
            
            if buildings:
                building = buildings[0]
                print("✅ Structure d'un immeuble:")
                for key, value in building.items():
                    print(f"  - {key}: {type(value).__name__} = {value}")
            else:
                print("⚠️  Aucun immeuble trouvé")
        else:
            print(f"❌ Erreur API buildings: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test de structure: {e}")

def main():
    """Fonction principale"""
    print("🧪 Test de connectivité et structure de données")
    print("=" * 50)
    
    # Test de connectivité
    if test_api_connectivity():
        # Test de structure
        test_database_structure()
        
        print("\n✅ Tests terminés - Vous pouvez utiliser download_render_db.py")
    else:
        print("\n❌ Tests échoués - Vérifiez la connectivité")

if __name__ == "__main__":
    main()
