#!/usr/bin/env python3
"""
Script pour créer une unité de test directement via l'API
"""

import requests
import json

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def create_test_unit():
    """Créer une unité de test"""
    try:
        print("🔄 Création d'une unité de test...")
        
        # Données de l'unité de test
        unit_data = {
            "id_immeuble": 1,  # L'ID de l'immeuble "Vachon" que nous avons créé
            "adresse_unite": "56 rue Vachon, Appartement 1",
            "type": "4 1/2",
            "nbr_chambre": 2,
            "nbr_salle_de_bain": 1
        }
        
        print(f"📤 Données à envoyer: {json.dumps(unit_data, indent=2)}")
        
        # Envoyer la requête
        response = requests.post(
            f"{RENDER_API_URL}/api/units",
            json=unit_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status code: {response.status_code}")
        print(f"📊 Response: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            unit = response.json()
            print(f"✅ Unité créée avec succès!")
            print(f"📋 ID: {unit.get('id_unite')}")
            print(f"📋 Adresse: {unit.get('adresse_unite')}")
            return True
        else:
            print(f"❌ Erreur lors de la création: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_units_after_creation():
    """Tester la récupération des unités après création"""
    try:
        print("\n🔄 Test de récupération des unités...")
        
        response = requests.get(f"{RENDER_API_URL}/api/units", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Données reçues: {json.dumps(data, indent=2)}")
            
            if isinstance(data, dict) and 'data' in data:
                units = data['data']
            else:
                units = data
                
            print(f"✅ {len(units)} unités trouvées")
            
            if units:
                print("\n📋 Détails des unités:")
                for i, unit in enumerate(units):
                    print(f"  Unité {i+1}:")
                    for key, value in unit.items():
                        print(f"    - {key}: {value}")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🚀 Création d'une unité de test")
    print("=" * 40)
    
    if create_test_unit():
        test_units_after_creation()
        print("\n✅ Test terminé - Vous pouvez maintenant tester la page des unités")
    else:
        print("\n❌ Échec de la création")

if __name__ == "__main__":
    main()
