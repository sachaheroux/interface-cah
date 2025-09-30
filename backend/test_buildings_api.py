#!/usr/bin/env python3
"""
Script pour tester l'API des immeubles et vérifier la colonne dette_restante
"""

import requests
import json

def test_buildings_api():
    """Tester l'API des immeubles"""
    
    # URL de l'API Render
    base_url = "https://interface-cah-backend.onrender.com"
    url = f"{base_url}/api/buildings"
    
    print(f"🚀 Test de l'API des immeubles")
    print(f"🔍 URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            buildings = response.json()
            print(f"✅ Succès! {len(buildings)} immeubles récupérés")
            
            # Vérifier le premier immeuble
            if buildings:
                first_building = buildings[0]
                print(f"📋 Premier immeuble:")
                print(f"  - ID: {first_building.get('id_immeuble')}")
                print(f"  - Nom: {first_building.get('nom_immeuble')}")
                print(f"  - Valeur actuelle: {first_building.get('valeur_actuel')}")
                print(f"  - Dette restante: {first_building.get('dette_restante')}")
                
                # Vérifier si toutes les clés attendues sont présentes
                expected_keys = [
                    'id_immeuble', 'nom_immeuble', 'adresse', 'ville', 'province',
                    'code_postal', 'pays', 'nbr_unite', 'annee_construction',
                    'prix_achete', 'mise_de_fond', 'taux_interet', 'valeur_actuel',
                    'dette_restante', 'proprietaire', 'banque', 'contracteur',
                    'notes', 'date_creation', 'date_modification'
                ]
                
                missing_keys = []
                for key in expected_keys:
                    if key not in first_building:
                        missing_keys.append(key)
                
                if missing_keys:
                    print(f"❌ Clés manquantes: {missing_keys}")
                else:
                    print(f"✅ Toutes les clés attendues sont présentes")
                    
                # Vérifier tous les immeubles pour dette_restante
                buildings_without_dette = []
                for building in buildings:
                    if 'dette_restante' not in building:
                        buildings_without_dette.append(building.get('nom_immeuble', 'Unknown'))
                
                if buildings_without_dette:
                    print(f"❌ Immeubles sans dette_restante: {buildings_without_dette}")
                else:
                    print(f"✅ Tous les immeubles ont la colonne dette_restante")
                    
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"📋 Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_buildings_api()
