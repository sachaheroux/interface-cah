#!/usr/bin/env python3
"""
Script de test simple pour vérifier les routes API des immeubles
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_buildings():
    """Test GET /api/buildings"""
    print("🏢 Test GET /api/buildings...")
    response = requests.get(f"{BASE_URL}/api/buildings")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        buildings = response.json()
        print(f"Nombre d'immeubles: {len(buildings)}")
        for building in buildings:
            print(f"  - {building['name']} (ID: {building['id']})")
        return buildings
    else:
        print(f"Erreur: {response.text}")
        return []

def test_create_building():
    """Test POST /api/buildings"""
    print("\n🏗️ Test POST /api/buildings...")
    
    new_building = {
        "name": "Test Immeuble API",
        "address": {
            "street": "123 Rue Test",
            "city": "Ville Test",
            "province": "QC",
            "postalCode": "H1H 1H1",
            "country": "Canada"
        },
        "type": "residential",
        "units": 5,
        "floors": 2,
        "yearBuilt": 2023,
        "totalArea": 3000,
        "characteristics": {
            "parking": 5,
            "elevator": False,
            "balconies": 3,
            "storage": True,
            "laundry": True,
            "airConditioning": False,
            "heating": "electric",
            "internet": True,
            "security": False
        },
        "financials": {
            "purchasePrice": 500000,
            "downPayment": 100000,
            "interestRate": 4.5,
            "currentValue": 520000
        },
        "contacts": {
            "owner": "Test Owner - 514-555-TEST",
            "bank": "Test Bank - Prêt #TEST-2023",
            "contractor": "Test Contractor - 514-555-BUILD"
        },
        "notes": "Immeuble de test créé via API"
    }
    
    response = requests.post(f"{BASE_URL}/api/buildings", json=new_building)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        created_building = response.json()
        print(f"Immeuble créé: {created_building['name']} (ID: {created_building['id']})")
        return created_building
    else:
        print(f"Erreur: {response.text}")
        return None

def test_get_building(building_id):
    """Test GET /api/buildings/{id}"""
    print(f"\n🔍 Test GET /api/buildings/{building_id}...")
    response = requests.get(f"{BASE_URL}/api/buildings/{building_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        building = response.json()
        print(f"Immeuble trouvé: {building['name']}")
        return building
    else:
        print(f"Erreur: {response.text}")
        return None

def test_update_building(building_id):
    """Test PUT /api/buildings/{id}"""
    print(f"\n✏️ Test PUT /api/buildings/{building_id}...")
    
    update_data = {
        "name": "Test Immeuble API - Modifié",
        "notes": "Immeuble de test modifié via API"
    }
    
    response = requests.put(f"{BASE_URL}/api/buildings/{building_id}", json=update_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        updated_building = response.json()
        print(f"Immeuble modifié: {updated_building['name']}")
        return updated_building
    else:
        print(f"Erreur: {response.text}")
        return None

def test_delete_building(building_id):
    """Test DELETE /api/buildings/{id}"""
    print(f"\n🗑️ Test DELETE /api/buildings/{building_id}...")
    response = requests.delete(f"{BASE_URL}/api/buildings/{building_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Résultat: {result['message']}")
        return True
    else:
        print(f"Erreur: {response.text}")
        return False

def main():
    print("🚀 Test des routes API des immeubles")
    print("=" * 50)
    
    # Test 1: Récupérer tous les immeubles
    buildings = test_get_buildings()
    
    # Test 2: Créer un nouvel immeuble
    new_building = test_create_building()
    if not new_building:
        print("❌ Échec de la création, arrêt des tests")
        return
    
    building_id = new_building['id']
    
    # Test 3: Récupérer l'immeuble créé
    test_get_building(building_id)
    
    # Test 4: Modifier l'immeuble
    test_update_building(building_id)
    
    # Test 5: Vérifier la modification
    test_get_building(building_id)
    
    # Test 6: Supprimer l'immeuble
    test_delete_building(building_id)
    
    # Test 7: Vérifier la suppression
    print("\n🔍 Vérification après suppression...")
    test_get_buildings()
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au serveur.")
        print("Assurez-vous que le serveur FastAPI est démarré sur http://localhost:8000")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}") 