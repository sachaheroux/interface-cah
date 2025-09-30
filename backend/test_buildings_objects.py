#!/usr/bin/env python3
"""
Script pour tester la méthode get_buildings_by_ids_objects
"""

import requests
import json

def test_buildings_objects():
    """Tester la méthode get_buildings_by_ids_objects"""
    
    # URL de l'API Render
    base_url = "https://interface-cah-backend.onrender.com"
    url = f"{base_url}/api/buildings"
    
    print(f"🚀 Test de la méthode get_buildings_by_ids_objects")
    print(f"🔍 URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            buildings = response.json()
            print(f"✅ Succès! {len(buildings)} immeubles récupérés")
            
            # Prendre les 3 premiers immeubles
            if len(buildings) >= 3:
                building_ids = [buildings[0]['id_immeuble'], buildings[1]['id_immeuble'], buildings[2]['id_immeuble']]
                print(f"🔍 IDs des immeubles: {building_ids}")
                
                # Tester l'analyse de rentabilité avec ces IDs
                analysis_url = f"{base_url}/api/analysis/profitability"
                params = {
                    "building_ids": ",".join(map(str, building_ids)),
                    "start_year": 2025,
                    "start_month": 7,
                    "end_year": 2026,
                    "end_month": 6
                }
                
                print(f"🔍 Test de l'analyse de rentabilité...")
                print(f"🔍 URL: {analysis_url}")
                print(f"🔍 Paramètres: {params}")
                
                analysis_response = requests.get(analysis_url, params=params, timeout=30)
                print(f"📊 Status Code: {analysis_response.status_code}")
                
                if analysis_response.status_code == 200:
                    analysis_data = analysis_response.json()
                    print(f"✅ Analyse réussie!")
                    print(f"📋 Données reçues:")
                    print(f"  - Nombre d'immeubles: {len(analysis_data.get('buildings', []))}")
                    print(f"  - Nombre de mois: {len(analysis_data.get('monthlyTotals', []))}")
                    print(f"  - Résumé: {analysis_data.get('summary', {})}")
                else:
                    print(f"❌ Erreur {analysis_response.status_code}")
                    print(f"📋 Réponse: {analysis_response.text}")
            else:
                print(f"❌ Pas assez d'immeubles pour le test")
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"📋 Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_buildings_objects()
