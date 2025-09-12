#!/usr/bin/env python3
"""
Script pour vérifier la persistance des données
Vérifie si les données reviennent après suppression
"""

import requests
import time

def check_persistence():
    """Vérifier la persistance des données"""
    print("🔍 VÉRIFICATION DE LA PERSISTANCE")
    print("=" * 50)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        print("1️⃣ Vérification initiale...")
        
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
        
        print("\n2️⃣ Attente de 5 secondes...")
        time.sleep(5)
        
        print("3️⃣ Vérification après attente...")
        
        # Vérifier à nouveau les immeubles
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings_after = buildings_response.json()
            print(f"   📊 Immeubles après attente: {len(buildings_after)}")
            
            if len(buildings_after) != len(buildings):
                print("   ⚠️ Le nombre d'immeubles a changé !")
                for building in buildings_after:
                    print(f"   🏢 Immeuble {building.get('id')}: {building.get('name', 'Sans nom')}")
            else:
                print("   ✅ Le nombre d'immeubles est stable")
        else:
            print(f"   ❌ Erreur immeubles après attente: {buildings_response.status_code}")
        
        # Vérifier à nouveau les unités
        units_response = requests.get(f"{base_url}/units")
        if units_response.status_code == 200:
            units_data = units_response.json()
            if isinstance(units_data, dict) and 'data' in units_data:
                units_after = units_data['data']
            else:
                units_after = units_data if isinstance(units_data, list) else []
            print(f"   📊 Unités après attente: {len(units_after)}")
            
            if len(units_after) != len(units):
                print("   ⚠️ Le nombre d'unités a changé !")
            else:
                print("   ✅ Le nombre d'unités est stable")
        else:
            print(f"   ❌ Erreur unités après attente: {units_response.status_code}")
        
        print("\n4️⃣ Vérification des logs de l'application...")
        
        # Essayer de récupérer les logs
        try:
            logs_response = requests.get(f"{base_url}/api/logs")
            if logs_response.status_code == 200:
                logs = logs_response.json()
                print(f"   📊 Logs récupérés: {len(logs) if isinstance(logs, list) else 'N/A'}")
            else:
                print(f"   ℹ️ Pas de logs disponibles: {logs_response.status_code}")
        except:
            print("   ℹ️ Pas de logs disponibles")
        
        print("\n5️⃣ Vérification de l'état de l'application...")
        
        # Vérifier l'état de l'application
        try:
            health_response = requests.get(f"{base_url}/health")
            if health_response.status_code == 200:
                health = health_response.json()
                print(f"   📊 Santé de l'application: {health}")
            else:
                print(f"   ℹ️ Pas d'endpoint de santé: {health_response.status_code}")
        except:
            print("   ℹ️ Pas d'endpoint de santé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔍 VÉRIFICATION DE LA PERSISTANCE")
    print("=" * 60)
    print("Ce script vérifie si les données reviennent après suppression.")
    print("=" * 60)
    
    success = check_persistence()
    
    if success:
        print("\n✅ Vérification terminée")
    else:
        print("\n❌ Erreur lors de la vérification")

if __name__ == "__main__":
    main()
