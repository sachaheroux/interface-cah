#!/usr/bin/env python3
"""
Script de suppression forcée des données cloud
Utilise des méthodes plus agressives pour supprimer les données
"""

import requests
import json

def force_delete_cloud():
    """Suppression forcée des données cloud"""
    print("🔥 SUPPRESSION FORCÉE DES DONNÉES CLOUD")
    print("=" * 50)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        # 1. Supprimer les unités d'abord (car elles dépendent de l'immeuble)
        print("1️⃣ Suppression forcée des unités...")
        
        units_response = requests.get(f"{base_url}/units")
        if units_response.status_code == 200:
            units_data = units_response.json()
            if isinstance(units_data, dict) and 'data' in units_data:
                units = units_data['data']
            else:
                units = units_data if isinstance(units_data, list) else []
            
            print(f"   📊 {len(units)} unités trouvées")
            
            for unit in units:
                if isinstance(unit, dict):
                    unit_id = unit.get('id')
                    if unit_id:
                        print(f"   🗑️ Suppression forcée unité {unit_id}...")
                        
                        # Essayer plusieurs méthodes de suppression
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
                                    print(f"      ✅ Unité {unit_id} supprimée avec {method}")
                                    break
                                else:
                                    print(f"      ⚠️ {method} échoué: {response.status_code}")
                            except Exception as e:
                                print(f"      ❌ Erreur {method}: {e}")
                                continue
        else:
            print("   ℹ️ Aucune unité trouvée")
        
        # 2. Supprimer l'immeuble
        print("\n2️⃣ Suppression forcée de l'immeuble...")
        
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"   📊 {len(buildings)} immeubles trouvés")
            
            for building in buildings:
                if isinstance(building, dict):
                    building_id = building.get('id')
                    if building_id:
                        print(f"   🗑️ Suppression forcée immeuble {building_id}...")
                        
                        # Essayer plusieurs méthodes de suppression
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
                                    print(f"      ✅ Immeuble {building_id} supprimé avec {method}")
                                    break
                                else:
                                    print(f"      ⚠️ {method} échoué: {response.status_code}")
                            except Exception as e:
                                print(f"      ❌ Erreur {method}: {e}")
                                continue
        else:
            print("   ℹ️ Aucun immeuble trouvé")
        
        # 3. Vérification finale
        print("\n3️⃣ Vérification finale...")
        
        endpoints = [
            ("buildings", "Immeubles"),
            ("units", "Unités"),
            ("tenants", "Locataires"),
            ("assignments", "Assignations"),
            ("building-reports", "Rapports d'immeubles"),
            ("invoices", "Factures")
        ]
        
        all_clean = True
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{base_url}/{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and 'data' in data:
                        count = len(data['data'])
                    else:
                        count = len(data) if isinstance(data, list) else 0
                    
                    if count == 0:
                        print(f"   ✅ {name}: 0 (propre)")
                    else:
                        print(f"   ⚠️ {name}: {count} (données restantes)")
                        all_clean = False
                else:
                    print(f"   ❌ {name}: Erreur {response.status_code}")
                    all_clean = False
            except Exception as e:
                print(f"   ❌ {name}: Erreur - {e}")
                all_clean = False
        
        return all_clean
        
    except Exception as e:
        print(f"❌ Erreur suppression forcée: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔥 SUPPRESSION FORCÉE DES DONNÉES CLOUD")
    print("=" * 60)
    print("Ce script utilise des méthodes agressives pour supprimer")
    print("toutes les données du cloud qui résistent à la suppression normale.")
    print("=" * 60)
    
    success = force_delete_cloud()
    
    if success:
        print("\n🎉 SUPPRESSION FORCÉE RÉUSSIE !")
        print("   Toutes les données du cloud ont été supprimées.")
        return True
    else:
        print("\n💥 SUPPRESSION FORCÉE PARTIELLE !")
        print("   Certaines données ont pu être supprimées.")
        print("   Vérifiez manuellement si nécessaire.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
