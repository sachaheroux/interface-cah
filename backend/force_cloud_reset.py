#!/usr/bin/env python3
"""
Script pour forcer la réinitialisation complète du cloud
Supprime toutes les données et recrée le schéma
"""

import requests
import json

def force_cloud_reset():
    """Forcer la réinitialisation complète du cloud"""
    print("🔥 RÉINITIALISATION FORCÉE DU CLOUD")
    print("=" * 50)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        print("1️⃣ Vérification de l'état actuel...")
        
        # Vérifier les immeubles
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"   📊 Immeubles: {len(buildings)}")
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
        
        print("\n2️⃣ Tentative de réinitialisation...")
        
        # Essayer plusieurs endpoints de réinitialisation
        reset_endpoints = [
            "/api/reset-database",
            "/api/init-database",
            "/api/recreate-tables",
            "/api/force-reset",
            "/api/migrate-schema"
        ]
        
        for endpoint in reset_endpoints:
            try:
                print(f"   🔄 Essai {endpoint}...")
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
                print(f"      Status: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    print(f"      ✅ Réinitialisation réussie avec {endpoint}")
                    try:
                        result = response.json()
                        print(f"      📊 Résultat: {result}")
                    except:
                        print(f"      📊 Résultat: {response.text}")
                    break
                else:
                    print(f"      ⚠️ {endpoint} échoué: {response.status_code}")
                    try:
                        error = response.json()
                        print(f"      📊 Erreur: {error}")
                    except:
                        print(f"      📊 Erreur: {response.text}")
            except Exception as e:
                print(f"      ❌ Erreur {endpoint}: {e}")
                continue
        
        print("\n3️⃣ Vérification après réinitialisation...")
        
        # Vérifier l'état après réinitialisation
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings_after = buildings_response.json()
            print(f"   📊 Immeubles après réinitialisation: {len(buildings_after)}")
        else:
            print(f"   ❌ Erreur vérification immeubles: {buildings_response.status_code}")
        
        units_response = requests.get(f"{base_url}/units")
        if units_response.status_code == 200:
            units_data = units_response.json()
            if isinstance(units_data, dict) and 'data' in units_data:
                units_after = units_data['data']
            else:
                units_after = units_data if isinstance(units_data, list) else []
            print(f"   📊 Unités après réinitialisation: {len(units_after)}")
        else:
            print(f"   ❌ Erreur vérification unités: {units_response.status_code}")
        
        # Vérifier si la réinitialisation a fonctionné
        total_after = len(buildings_after) + len(units_after)
        if total_after == 0:
            print("\n   ✅ Réinitialisation réussie !")
            return True
        else:
            print(f"\n   ⚠️ {total_after} éléments persistent encore")
            return False
        
    except Exception as e:
        print(f"❌ Erreur réinitialisation: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔥 RÉINITIALISATION FORCÉE DU CLOUD")
    print("=" * 60)
    print("Ce script force la réinitialisation complète du cloud.")
    print("=" * 60)
    
    success = force_cloud_reset()
    
    if success:
        print("\n🎉 RÉINITIALISATION RÉUSSIE !")
        print("   Le cloud a été complètement réinitialisé.")
        return True
    else:
        print("\n💥 RÉINITIALISATION ÉCHOUÉE !")
        print("   Le cloud n'a pas pu être réinitialisé.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
