#!/usr/bin/env python3
"""
Script pour supprimer l'unité de test (ID 1)
"""

import requests
import json

API_BASE_URL = "https://interface-cah-backend.onrender.com"

def delete_test_unit():
    """Supprimer l'unité de test (ID 1)"""
    print("🗑️ Suppression de l'unité de test (ID 1)...")
    try:
        response = requests.delete(f"{API_BASE_URL}/api/units/1")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Suppression réussie: {result.get('message', 'Unité supprimée')}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def verify_units():
    """Vérifier les unités restantes"""
    print("\n🔄 Vérification des unités restantes...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/units")
        if response.status_code == 200:
            data = response.json()
            units = data.get('data', [])
            print(f"✅ {len(units)} unités restantes:")
            for unit in units:
                print(f"  - ID {unit['id_unite']}: {unit['adresse_unite']}")
            return units
        else:
            print(f"❌ Erreur lors de la vérification: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

if __name__ == "__main__":
    # Supprimer l'unité de test
    success = delete_test_unit()
    
    if success:
        # Vérifier les unités restantes
        remaining_units = verify_units()
        
        if len(remaining_units) == 4:
            print("\n✅ Parfait ! Vous avez maintenant exactement 4 unités.")
        else:
            print(f"\n⚠️  Vous avez {len(remaining_units)} unités au lieu de 4.")
    else:
        print("\n❌ Échec de la suppression de l'unité de test.")
