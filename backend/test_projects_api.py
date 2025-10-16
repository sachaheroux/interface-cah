#!/usr/bin/env python3
"""
Script pour tester l'API des projets
"""

import requests
import json

# Configuration
CONSTRUCTION_BASE = "https://interface-cah-backend.onrender.com/api/construction"

def test_projects_api():
    """Tester l'API des projets"""
    
    print("🔍 TEST DE L'API PROJETS")
    print("=" * 50)
    
    try:
        response = requests.get(f"{CONSTRUCTION_BASE}/projets", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            projets = data.get('data', [])
            print(f"\n📊 {len(projets)} projet(s) trouvé(s)")
            
            for projet in projets:
                print(f"   🏗️ ID: {projet.get('id_projet', 'N/A')} - {projet.get('nom', 'N/A')}")
                if projet.get('date_debut'):
                    print(f"      Début: {projet['date_debut'][:10]}")
                if projet.get('date_fin_prevue'):
                    print(f"      Fin prévue: {projet['date_fin_prevue'][:10]}")
                print()
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_projects_api()
