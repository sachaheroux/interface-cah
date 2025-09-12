#!/usr/bin/env python3
"""
Script simple pour supprimer toutes les données
Utilise la méthode qui fonctionnait avant
"""

import requests

def simple_delete_all():
    """Suppression simple de toutes les données"""
    print("🗑️ SUPPRESSION SIMPLE DE TOUTES LES DONNÉES")
    print("=" * 50)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        # 1. Supprimer tous les immeubles (cela supprimera aussi les unités)
        print("1️⃣ Suppression des immeubles...")
        
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"   📊 {len(buildings)} immeubles trouvés")
            
            for building in buildings:
                building_id = building.get('id')
                if building_id:
                    print(f"   🗑️ Suppression immeuble {building_id}...")
                    delete_response = requests.delete(f"{base_url}/buildings/{building_id}")
                    if delete_response.status_code == 200:
                        print(f"   ✅ Immeuble {building_id} supprimé")
                    else:
                        print(f"   ❌ Erreur suppression immeuble {building_id}: {delete_response.status_code}")
        else:
            print("   ℹ️ Aucun immeuble trouvé")
        
        # 2. Vérification finale
        print("\n2️⃣ Vérification finale...")
        
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"   📊 Immeubles restants: {len(buildings)}")
            
            if len(buildings) == 0:
                print("   ✅ Tous les immeubles supprimés !")
                return True
            else:
                print("   ⚠️ Des immeubles persistent encore")
                return False
        else:
            print("   ❌ Erreur vérification")
            return False
        
    except Exception as e:
        print(f"❌ Erreur suppression: {e}")
        return False

def main():
    """Fonction principale"""
    print("🗑️ SUPPRESSION SIMPLE DE TOUTES LES DONNÉES")
    print("=" * 60)
    print("Ce script utilise la méthode simple qui fonctionnait avant.")
    print("=" * 60)
    
    success = simple_delete_all()
    
    if success:
        print("\n🎉 SUPPRESSION RÉUSSIE !")
        print("   Toutes les données ont été supprimées.")
        return True
    else:
        print("\n💥 SUPPRESSION ÉCHOUÉE !")
        print("   Certaines données persistent encore.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
