#!/usr/bin/env python3
"""
Diagnostic complet du problème de persistance
Analyse tous les angles possibles
"""

import requests
import json
import time
from datetime import datetime

def complete_diagnosis():
    """Diagnostic complet du problème"""
    print("🔍 DIAGNOSTIC COMPLET DU PROBLÈME")
    print("=" * 60)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        print("1️⃣ VÉRIFICATION DE L'ÉTAT ACTUEL")
        print("-" * 40)
        
        # Vérifier les immeubles
        buildings_response = requests.get(f"{base_url}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"   📊 Immeubles: {len(buildings)}")
            for building in buildings:
                print(f"   🏢 ID: {building.get('id')}, Nom: {building.get('name')}, Créé: {building.get('created_at', 'N/A')}")
        else:
            print(f"   ❌ Erreur immeubles: {buildings_response.status_code}")
            return False
        
        # Vérifier les unités
        units_response = requests.get(f"{base_url}/units")
        if units_response.status_code == 200:
            units_data = units_response.json()
            if isinstance(units_data, dict) and 'data' in units_data:
                units = units_data['data']
            else:
                units = units_data if isinstance(units_data, list) else []
            print(f"   📊 Unités: {len(units)}")
            for unit in units[:3]:  # Afficher seulement les 3 premières
                print(f"   🏠 ID: {unit.get('id')}, Building: {unit.get('buildingId')}, Numéro: {unit.get('unitNumber')}")
        else:
            print(f"   ❌ Erreur unités: {units_response.status_code}")
            return False
        
        print("\n2️⃣ TEST DE SUPPRESSION DÉTAILLÉ")
        print("-" * 40)
        
        # Tester la suppression d'un immeuble spécifique
        if buildings:
            building_id = buildings[0].get('id')
            print(f"   🗑️ Test suppression immeuble {building_id}...")
            
            # Méthode 1: DELETE standard
            try:
                delete_response = requests.delete(f"{base_url}/buildings/{building_id}")
                print(f"      DELETE: Status {delete_response.status_code}")
                if delete_response.status_code != 200:
                    try:
                        error = delete_response.json()
                        print(f"      Erreur: {error}")
                    except:
                        print(f"      Erreur: {delete_response.text}")
            except Exception as e:
                print(f"      Erreur DELETE: {e}")
            
            # Attendre un peu
            time.sleep(2)
            
            # Vérifier si l'immeuble a été supprimé
            check_response = requests.get(f"{base_url}/buildings")
            if check_response.status_code == 200:
                buildings_after = check_response.json()
                if len(buildings_after) < len(buildings):
                    print(f"      ✅ Immeuble supprimé (avant: {len(buildings)}, après: {len(buildings_after)})")
                else:
                    print(f"      ❌ Immeuble non supprimé (avant: {len(buildings)}, après: {len(buildings_after)})")
            else:
                print(f"      ❌ Erreur vérification: {check_response.status_code}")
        
        print("\n3️⃣ VÉRIFICATION DES ENDPOINTS")
        print("-" * 40)
        
        # Tester tous les endpoints disponibles
        endpoints_to_test = [
            "/api/buildings",
            "/api/units", 
            "/api/tenants",
            "/api/assignments",
            "/api/building-reports",
            "/api/invoices",
            "/api/migrate-schema",
            "/api/reset-database",
            "/api/init-database",
            "/api/health",
            "/api/logs"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                print(f"   {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"   {endpoint}: Erreur - {e}")
        
        print("\n4️⃣ VÉRIFICATION DES MÉTADONNÉES")
        print("-" * 40)
        
        # Vérifier les headers de réponse
        try:
            response = requests.get(f"{base_url}/buildings")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Server: {response.headers.get('Server', 'N/A')}")
            print(f"   Date: {response.headers.get('Date', 'N/A')}")
        except Exception as e:
            print(f"   Erreur headers: {e}")
        
        print("\n5️⃣ TEST DE PERSISTANCE TEMPORELLE")
        print("-" * 40)
        
        # Faire plusieurs vérifications dans le temps
        for i in range(3):
            print(f"   Vérification {i+1}/3...")
            time.sleep(3)
            
            buildings_response = requests.get(f"{base_url}/buildings")
            if buildings_response.status_code == 200:
                buildings = buildings_response.json()
                print(f"      Immeubles: {len(buildings)}")
            else:
                print(f"      Erreur: {buildings_response.status_code}")
        
        print("\n6️⃣ ANALYSE DES DONNÉES")
        print("-" * 40)
        
        # Analyser les données en détail
        if buildings:
            building = buildings[0]
            print(f"   Structure immeuble: {list(building.keys())}")
            print(f"   Données complètes: {json.dumps(building, indent=2)}")
        
        print("\n7️⃣ VÉRIFICATION DE L'APPLICATION RENDER")
        print("-" * 40)
        
        # Vérifier l'état de l'application Render
        try:
            # Essayer d'accéder à la racine
            root_response = requests.get("https://interface-cah-backend.onrender.com/", timeout=10)
            print(f"   Root endpoint: {root_response.status_code}")
        except Exception as e:
            print(f"   Erreur root: {e}")
        
        # Vérifier les logs Render
        try:
            logs_response = requests.get("https://interface-cah-backend.onrender.com/logs", timeout=10)
            print(f"   Logs endpoint: {logs_response.status_code}")
        except Exception as e:
            print(f"   Erreur logs: {e}")
        
        print("\n8️⃣ CONCLUSION DU DIAGNOSTIC")
        print("-" * 40)
        
        # Analyser les résultats
        if len(buildings) > 0:
            print("   ❌ PROBLÈME IDENTIFIÉ: Données persistantes")
            print("   💡 CAUSE POSSIBLE: Schéma obsolète ou cache")
            print("   🔧 SOLUTION: Réinitialisation complète nécessaire")
        else:
            print("   ✅ Aucun problème détecté")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur diagnostic: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔍 DIAGNOSTIC COMPLET DU PROBLÈME")
    print("=" * 60)
    print("Ce script analyse tous les angles du problème de persistance.")
    print("=" * 60)
    
    success = complete_diagnosis()
    
    if success:
        print("\n✅ Diagnostic terminé")
    else:
        print("\n❌ Erreur lors du diagnostic")

if __name__ == "__main__":
    main()
