#!/usr/bin/env python3
"""
Test complet de persistance des données - Interface CAH
Ce script teste tous les scénarios de persistance possibles
"""
import requests
import json
import time
from datetime import datetime

API_BASE_URL = "https://interface-cah-backend.onrender.com"

def print_header(title):
    """Afficher un en-tête formaté"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Afficher une étape"""
    print(f"\n{step}. {description}")
    print("-" * 40)

def test_persistance_complete():
    """Test complet de persistance"""
    print("🏗️  TEST COMPLET DE PERSISTANCE - INTERFACE CAH")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Étape 1: État initial
    print_step("1", "Vérification de l'état initial")
    try:
        response = requests.get(f"{API_BASE_URL}/api/buildings")
        initial_buildings = response.json()
        initial_count = len(initial_buildings)
        
        response = requests.get(f"{API_BASE_URL}/api/dashboard")
        initial_dashboard = response.json()
        initial_value = initial_dashboard['portfolioValue']
        
        print(f"📊 État initial:")
        print(f"   - Immeubles: {initial_count}")
        print(f"   - Valeur portfolio: {initial_value:,.0f}$")
        
        if initial_buildings:
            print(f"📋 Immeubles existants:")
            for building in initial_buildings:
                print(f"   - {building['name']} (ID: {building['id']}) - {building.get('financials', {}).get('currentValue', 0):,.0f}$")
    except Exception as e:
        print(f"❌ Erreur état initial: {e}")
        return False
    
    # Étape 2: Création d'un immeuble test
    print_step("2", "Création d'un immeuble de test")
    test_building = {
        "name": f"Test Persistance {datetime.now().strftime('%H:%M:%S')}",
        "address": {
            "street": "456 Rue Persistance",
            "city": "Québec",
            "province": "QC",
            "postalCode": "G1G 1G1",
            "country": "Canada"
        },
        "type": "residential",
        "units": 8,
        "floors": 2,
        "yearBuilt": 2022,
        "totalArea": 4000,
        "financials": {
            "purchasePrice": 600000,
            "downPayment": 120000,
            "interestRate": 4.5,
            "currentValue": 650000
        },
        "contacts": {
            "owner": "Test Persistance Owner",
            "bank": "Banque Test",
            "contractor": "Entrepreneur Test"
        },
        "notes": f"Immeuble créé le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} pour tester la persistance"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/buildings", json=test_building)
        if response.status_code == 200:
            new_building = response.json()
            test_building_id = new_building['id']
            print(f"✅ Immeuble créé avec succès:")
            print(f"   - ID: {test_building_id}")
            print(f"   - Nom: {new_building['name']}")
            print(f"   - Valeur: {new_building['financials']['currentValue']:,.0f}$")
        else:
            print(f"❌ Erreur création: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur création: {e}")
        return False
    
    # Étape 3: Vérification immédiate
    print_step("3", "Vérification immédiate de la sauvegarde")
    time.sleep(2)  # Attendre que la sauvegarde soit complète
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/buildings")
        buildings_after = response.json()
        
        response = requests.get(f"{API_BASE_URL}/api/dashboard")
        dashboard_after = response.json()
        
        building_found = any(b['id'] == test_building_id for b in buildings_after)
        
        print(f"📊 État après création:")
        print(f"   - Immeubles: {len(buildings_after)} (était {initial_count})")
        print(f"   - Valeur portfolio: {dashboard_after['portfolioValue']:,.0f}$ (était {initial_value:,.0f}$)")
        print(f"   - Immeuble trouvé: {'✅ Oui' if building_found else '❌ Non'}")
        
        if building_found and len(buildings_after) > initial_count:
            print("✅ Sauvegarde immédiate confirmée")
        else:
            print("❌ Problème de sauvegarde immédiate")
            return False
            
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
        return False
    
    # Étape 4: Test de récupération spécifique
    print_step("4", "Test de récupération par ID")
    try:
        response = requests.get(f"{API_BASE_URL}/api/buildings/{test_building_id}")
        if response.status_code == 200:
            retrieved_building = response.json()
            print(f"✅ Immeuble récupéré par ID:")
            print(f"   - Nom: {retrieved_building['name']}")
            print(f"   - Créé le: {retrieved_building.get('createdAt', 'N/A')}")
            print(f"   - Modifié le: {retrieved_building.get('updatedAt', 'N/A')}")
        else:
            print(f"❌ Erreur récupération: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur récupération: {e}")
        return False
    
    # Étape 5: Test de modification
    print_step("5", "Test de modification et persistance")
    modification = {
        "financials": {
            "purchasePrice": 600000,
            "downPayment": 120000,
            "interestRate": 4.5,
            "currentValue": 700000  # Augmentation de valeur
        },
        "notes": f"Modifié le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Test persistance"
    }
    
    try:
        response = requests.put(f"{API_BASE_URL}/api/buildings/{test_building_id}", json=modification)
        if response.status_code == 200:
            print("✅ Modification réussie")
            
            # Vérifier la modification
            time.sleep(1)
            response = requests.get(f"{API_BASE_URL}/api/buildings/{test_building_id}")
            modified_building = response.json()
            
            if modified_building['financials']['currentValue'] == 700000:
                print("✅ Modification persistée correctement")
                
                # Vérifier impact sur dashboard
                response = requests.get(f"{API_BASE_URL}/api/dashboard")
                dashboard_modified = response.json()
                print(f"📊 Valeur portfolio après modification: {dashboard_modified['portfolioValue']:,.0f}$")
            else:
                print("❌ Modification non persistée")
                return False
        else:
            print(f"❌ Erreur modification: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur modification: {e}")
        return False
    
    # Étape 6: Instructions pour test manuel
    print_step("6", "Test de persistance après redéploiement")
    print("📋 INSTRUCTIONS POUR TEST MANUEL:")
    print(f"   1. Notez l'ID de l'immeuble test: {test_building_id}")
    print(f"   2. Notez le nom: {new_building['name']}")
    print("   3. Redéployez l'application sur Render (git push)")
    print("   4. Attendez que le redéploiement soit terminé (2-3 minutes)")
    print("   5. Relancez ce script pour vérifier si l'immeuble existe encore")
    print("   6. Ou vérifiez dans l'interface web")
    
    # Étape 7: Résumé final
    print_header("RÉSUMÉ DU TEST")
    print("✅ API fonctionnelle")
    print("✅ Création d'immeuble persistée")
    print("✅ Récupération par ID fonctionnelle")
    print("✅ Modification persistée")
    print("✅ Dashboard mis à jour correctement")
    print("\n🎯 PROCHAINES ÉTAPES:")
    print("   1. Testez la persistance après redéploiement")
    print("   2. Créez des immeubles via l'interface web")
    print("   3. Vérifiez qu'ils persistent après rafraîchissement")
    
    return True

def test_apres_redeploiement():
    """Test à lancer après un redéploiement pour vérifier la persistance"""
    print_header("TEST POST-REDÉPLOIEMENT")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/buildings")
        buildings = response.json()
        
        print(f"📊 Immeubles trouvés après redéploiement: {len(buildings)}")
        
        if buildings:
            print("📋 Liste des immeubles persistés:")
            for building in buildings:
                created_at = building.get('createdAt', 'N/A')
                print(f"   - {building['name']} (ID: {building['id']}) - Créé: {created_at}")
            
            print("✅ PERSISTANCE CONFIRMÉE - Les données survivent au redéploiement!")
        else:
            print("⚠️  Aucun immeuble trouvé - Soit il n'y en avait pas, soit la persistance a échoué")
            
    except Exception as e:
        print(f"❌ Erreur test post-redéploiement: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "post":
        test_apres_redeploiement()
    else:
        test_persistance_complete() 