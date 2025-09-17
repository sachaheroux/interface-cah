#!/usr/bin/env python3
"""
Script pour tester la suppression d'unités
"""

import requests
import json

# Configuration
API_BASE_URL = "https://interface-cah-backend.onrender.com"

def test_delete_unit():
    """Tester la suppression d'une unité"""
    print("🧪 Test de suppression d'unité")
    print("=" * 50)
    
    # 1. Récupérer les unités existantes
    print("1️⃣ Récupération des unités existantes...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/units")
        if response.status_code == 200:
            data = response.json()
            units = data.get('data', [])
            print(f"✅ {len(units)} unités trouvées")
            
            if units:
                unit_to_delete = units[0]
                print(f"📋 Unité à supprimer: {unit_to_delete['adresse_unite']} (ID: {unit_to_delete['id_unite']})")
                
                # 2. Supprimer l'unité
                print(f"\n2️⃣ Suppression de l'unité {unit_to_delete['id_unite']}...")
                delete_response = requests.delete(f"{API_BASE_URL}/api/units/{unit_to_delete['id_unite']}")
                
                if delete_response.status_code == 200:
                    result = delete_response.json()
                    print(f"✅ Suppression réussie: {result.get('message', 'Unité supprimée')}")
                    
                    # 3. Vérifier que l'unité a été supprimée
                    print(f"\n3️⃣ Vérification de la suppression...")
                    verify_response = requests.get(f"{API_BASE_URL}/api/units")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        remaining_units = verify_data.get('data', [])
                        print(f"✅ {len(remaining_units)} unités restantes")
                        
                        # Vérifier que l'unité supprimée n'est plus dans la liste
                        deleted_unit_exists = any(u['id_unite'] == unit_to_delete['id_unite'] for u in remaining_units)
                        if not deleted_unit_exists:
                            print("✅ L'unité a bien été supprimée de la base de données")
                        else:
                            print("❌ L'unité est toujours présente dans la base de données")
                    else:
                        print(f"❌ Erreur lors de la vérification: {verify_response.status_code}")
                else:
                    print(f"❌ Erreur lors de la suppression: {delete_response.status_code}")
                    print(f"   Réponse: {delete_response.text}")
            else:
                print("⚠️ Aucune unité trouvée pour tester la suppression")
        else:
            print(f"❌ Erreur lors de la récupération des unités: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_delete_unit()
