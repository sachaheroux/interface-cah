#!/usr/bin/env python3
"""
Script pour analyser les données des immeubles et déboguer les adresses
"""
import requests
import json

API_BASE_URL = "https://interface-cah-backend.onrender.com"

def debug_buildings():
    """Analyser les données des immeubles"""
    print("🔍 Analyse des données des immeubles")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/buildings")
        buildings = response.json()
        
        print(f"📊 Nombre total d'immeubles: {len(buildings)}")
        print()
        
        for i, building in enumerate(buildings, 1):
            print(f"🏢 Immeuble {i}: {building['name']}")
            print(f"   ID: {building['id']}")
            
            # Analyser l'adresse
            address = building.get('address', {})
            print(f"   📍 Adresse:")
            if isinstance(address, dict):
                print(f"      Rue: {address.get('street', 'N/A')}")
                print(f"      Ville: {address.get('city', 'N/A')}")
                print(f"      Province: {address.get('province', 'N/A')}")
                print(f"      Code postal: {address.get('postalCode', 'N/A')}")
                print(f"      Pays: {address.get('country', 'N/A')}")
                
                # Construire l'adresse complète
                parts = []
                if address.get('street'): parts.append(address['street'])
                if address.get('city'): parts.append(address['city'])
                if address.get('province'): parts.append(address['province'])
                if address.get('country'): parts.append(address['country'])
                full_address = ', '.join(parts)
                print(f"      Adresse complète: {full_address}")
            else:
                print(f"      Format string: {address}")
            
            # Autres infos
            print(f"   🏠 Unités: {building.get('units', 'N/A')}")
            print(f"   💰 Valeur: {building.get('financials', {}).get('currentValue', 'N/A')}")
            print()
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    debug_buildings() 