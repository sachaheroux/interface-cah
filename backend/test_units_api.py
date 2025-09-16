#!/usr/bin/env python3
"""
Script pour tester l'API des unités et voir le format des données
"""

import requests
import json

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def test_units_api():
    """Tester l'API des unités"""
    try:
        print("🔄 Test de l'API des unités...")
        
        response = requests.get(f"{RENDER_API_URL}/api/units", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Données brutes: {data}")
            
            # Vérifier si c'est un tableau direct ou dans un objet data
            if isinstance(data, list):
                units = data
            elif isinstance(data, dict) and 'data' in data:
                units = data['data']
            else:
                units = []
            
            print(f"✅ {len(units)} unités trouvées")
            
            if units:
                print("\n📊 Structure d'une unité:")
                unit = units[0]
                for key, value in unit.items():
                    print(f"  - {key}: {type(value).__name__} = {value}")
            else:
                print("⚠️  Aucune unité trouvée")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_units_api()
