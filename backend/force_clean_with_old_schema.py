#!/usr/bin/env python3
"""
Script pour nettoyer la base de données avec l'ancien schéma
Utilise des requêtes SQL directes pour contourner les modèles
"""

import requests
import json

def force_clean_with_old_schema():
    """Nettoyer la base avec l'ancien schéma"""
    print("🧹 NETTOYAGE FORCÉ AVEC ANCIEN SCHÉMA")
    print("=" * 50)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        print("1️⃣ Vérification de l'état actuel...")
        
        # Vérifier les immeubles
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"   📊 Immeubles: {len(buildings)}")
            
            for building in buildings:
                print(f"   🏢 Immeuble {building.get('id')}: {building.get('name', 'Sans nom')}")
        else:
            print(f"   ❌ Erreur immeubles: {buildings_response.status_code}")
        
        # Vérifier les unités
        units_response = requests.get(f"{base_url}/units")
        if units_response.status_code == 200:
            units_data = units_response.json()
            if isinstance(units_data, dict) and 'data' in units_data:
                units = units_data['data']
            else:
                units = units_data if isinstance(units_data, list) else []
            print(f"   📊 Unités: {len(units)}")
        else:
            print(f"   ❌ Erreur unités: {units_response.status_code}")
        
        print("\n2️⃣ Tentative de nettoyage direct...")
        
        # Essayer de supprimer les unités d'abord (car elles dépendent de l'immeuble)
        if 'units' in locals() and units:
            print("   🗑️ Suppression des unités...")
            for unit in units:
                if isinstance(unit, dict):
                    unit_id = unit.get('id')
                    if unit_id:
                        print(f"      Suppression unité {unit_id}...")
                        # Essayer plusieurs méthodes
                        methods = [
                            ("DELETE", f"{base_url}/units/{unit_id}"),
                            ("POST", f"{base_url}/units/{unit_id}/delete"),
                            ("PUT", f"{base_url}/units/{unit_id}", {"action": "delete"})
                        ]
                        
                        for method, url in methods:
                            try:
                                if method == "DELETE":
                                    response = requests.delete(url)
                                elif method == "POST":
                                    response = requests.post(url)
                                elif method == "PUT":
                                    response = requests.put(url, json={"action": "delete"})
                                
                                if response.status_code in [200, 204, 404]:
                                    print(f"         ✅ Unité {unit_id} supprimée avec {method}")
                                    break
                                else:
                                    print(f"         ⚠️ {method} échoué: {response.status_code}")
                            except Exception as e:
                                print(f"         ❌ Erreur {method}: {e}")
                                continue
        
        # Essayer de supprimer les immeubles
        if 'buildings' in locals() and buildings:
            print("\n   🗑️ Suppression des immeubles...")
            for building in buildings:
                if isinstance(building, dict):
                    building_id = building.get('id')
                    if building_id:
                        print(f"      Suppression immeuble {building_id}...")
                        # Essayer plusieurs méthodes
                        methods = [
                            ("DELETE", f"{base_url}/buildings/{building_id}"),
                            ("POST", f"{base_url}/buildings/{building_id}/delete"),
                            ("PUT", f"{base_url}/buildings/{building_id}", {"action": "delete"})
                        ]
                        
                        for method, url in methods:
                            try:
                                if method == "DELETE":
                                    response = requests.delete(url)
                                elif method == "POST":
                                    response = requests.post(url)
                                elif method == "PUT":
                                    response = requests.put(url, json={"action": "delete"})
                                
                                if response.status_code in [200, 204, 404]:
                                    print(f"         ✅ Immeuble {building_id} supprimé avec {method}")
                                    break
                                else:
                                    print(f"         ⚠️ {method} échoué: {response.status_code}")
                            except Exception as e:
                                print(f"         ❌ Erreur {method}: {e}")
                                continue
        
        print("\n3️⃣ Vérification finale...")
        
        # Vérifier l'état final
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"   📊 Immeubles restants: {len(buildings)}")
        else:
            print(f"   ❌ Erreur vérification immeubles: {buildings_response.status_code}")
        
        units_response = requests.get(f"{base_url}/units")
        if units_response.status_code == 200:
            units_data = units_response.json()
            if isinstance(units_data, dict) and 'data' in units_data:
                units = units_data['data']
            else:
                units = units_data if isinstance(units_data, list) else []
            print(f"   📊 Unités restantes: {len(units)}")
        else:
            print(f"   ❌ Erreur vérification unités: {units_response.status_code}")
        
        # Vérifier si tout est propre
        total_remaining = len(buildings) + len(units)
        if total_remaining == 0:
            print("\n   ✅ Nettoyage réussi !")
            return True
        else:
            print(f"\n   ⚠️ {total_remaining} éléments restants")
            return False
        
    except Exception as e:
        print(f"❌ Erreur nettoyage: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧹 NETTOYAGE FORCÉ AVEC ANCIEN SCHÉMA")
    print("=" * 60)
    print("Ce script utilise des méthodes directes pour nettoyer")
    print("la base de données même avec un schéma obsolète.")
    print("=" * 60)
    
    success = force_clean_with_old_schema()
    
    if success:
        print("\n🎉 NETTOYAGE RÉUSSI !")
        print("   Toutes les données ont été supprimées.")
        return True
    else:
        print("\n💥 NETTOYAGE PARTIEL !")
        print("   Certaines données persistent encore.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
