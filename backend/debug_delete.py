#!/usr/bin/env python3
"""
Script pour déboguer la suppression d'immeubles
Affiche les erreurs détaillées
"""

import requests
import json

def debug_delete():
    """Déboguer la suppression d'immeubles"""
    print("🔍 DÉBOGAGE DE LA SUPPRESSION D'IMMEUBLES")
    print("=" * 50)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        # 1. Récupérer les immeubles
        print("1️⃣ Récupération des immeubles...")
        
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"   📊 {len(buildings)} immeubles trouvés")
            
            for building in buildings:
                building_id = building.get('id')
                print(f"   🏢 Immeuble {building_id}: {building.get('name', 'Sans nom')}")
        else:
            print(f"   ❌ Erreur récupération: {buildings_response.status_code}")
            return False
        
        # 2. Essayer de supprimer le premier immeuble
        print("\n2️⃣ Tentative de suppression...")
        
        if buildings:
            building_id = buildings[0].get('id')
            print(f"   🗑️ Suppression immeuble {building_id}...")
            
            delete_response = requests.delete(f"{base_url}/buildings/{building_id}")
            print(f"   📊 Status: {delete_response.status_code}")
            
            if delete_response.status_code != 200:
                print(f"   ❌ Erreur détaillée:")
                try:
                    error_data = delete_response.json()
                    print(f"      {json.dumps(error_data, indent=2)}")
                except:
                    print(f"      {delete_response.text}")
            else:
                print(f"   ✅ Suppression réussie")
        
        # 3. Vérification finale
        print("\n3️⃣ Vérification finale...")
        
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"   📊 Immeubles restants: {len(buildings)}")
        else:
            print(f"   ❌ Erreur vérification: {buildings_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur débogage: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔍 DÉBOGAGE DE LA SUPPRESSION D'IMMEUBLES")
    print("=" * 60)
    print("Ce script va déboguer pourquoi la suppression ne fonctionne pas.")
    print("=" * 60)
    
    success = debug_delete()
    
    if success:
        print("\n✅ Débogage terminé")
    else:
        print("\n❌ Erreur lors du débogage")

if __name__ == "__main__":
    main()
