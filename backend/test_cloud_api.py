#!/usr/bin/env python3
"""
Test simple de l'API cloud
"""

import requests

def test_cloud_api():
    print("🌐 TEST API CLOUD:")
    
    # Test des immeubles
    print("\n🏢 IMMEUBLES:")
    response = requests.get('https://interface-cah-backend.onrender.com/api/buildings')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        buildings = response.json()
        print(f"Immeubles trouvés: {len(buildings)}")
        for building in buildings:
            print(f"  - {building['name']} (ID: {building['id']})")
    else:
        print(f"Erreur: {response.text}")
    
    # Test des unités
    print("\n🏠 UNITÉS:")
    response = requests.get('https://interface-cah-backend.onrender.com/api/units')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        units_data = response.json()
        print(f"Type des données: {type(units_data)}")
        print(f"Clés disponibles: {list(units_data.keys()) if isinstance(units_data, dict) else 'N/A'}")
        
        # Vérifier si c'est un dict avec une clé 'data'
        if isinstance(units_data, dict) and 'data' in units_data:
            units = units_data['data']
            print(f"Unités trouvées: {len(units)}")
            for i, unit in enumerate(units):
                print(f"  - Unité {i}: {unit}")
        else:
            print(f"Structure inattendue: {units_data}")
    else:
        print(f"Erreur: {response.text}")

if __name__ == "__main__":
    test_cloud_api()
