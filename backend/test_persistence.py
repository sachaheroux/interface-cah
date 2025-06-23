#!/usr/bin/env python3
"""
Script de test pour vérifier la persistance des données
"""
import requests
import json
import time

API_BASE_URL = "https://interface-cah-backend.onrender.com"

def test_api():
    """Tester l'API et la persistance des données"""
    print("🧪 Test de l'API Interface CAH")
    print("=" * 50)
    
    # Test 1: Vérifier que l'API fonctionne
    print("\n1. Test de santé de l'API...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API fonctionnelle")
        else:
            print(f"❌ API non fonctionnelle (status: {response.status_code})")
            return
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    # Test 2: Vérifier les données actuelles
    print("\n2. Vérification des données actuelles...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/buildings")
        buildings = response.json()
        print(f"📊 Nombre d'immeubles actuels: {len(buildings)}")
        
        # Afficher les immeubles existants
        for building in buildings:
            print(f"   - {building['name']} (ID: {building['id']}, Valeur: {building.get('financials', {}).get('currentValue', 0)}$)")
    except Exception as e:
        print(f"❌ Erreur récupération immeubles: {e}")
        return
    
    # Test 3: Vérifier le dashboard
    print("\n3. Test du dashboard...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/dashboard")
        dashboard = response.json()
        print(f"📈 Statistiques dashboard:")
        print(f"   - Total immeubles: {dashboard['totalBuildings']}")
        print(f"   - Total unités: {dashboard['totalUnits']}")
        print(f"   - Valeur portfolio: {dashboard['portfolioValue']:,.0f}$")
        print(f"   - Taux d'occupation: {dashboard['occupancyRate']}%")
    except Exception as e:
        print(f"❌ Erreur dashboard: {e}")
        return
    
    # Test 4: Créer un immeuble de test
    print("\n4. Test de création d'immeuble...")
    test_building = {
        "name": "Test Immeuble Persistance",
        "address": {
            "street": "123 Rue Test",
            "city": "Montréal",
            "province": "QC",
            "postalCode": "H1H 1H1",
            "country": "Canada"
        },
        "type": "residential",
        "units": 10,
        "floors": 3,
        "yearBuilt": 2020,
        "totalArea": 5000,
        "financials": {
            "purchasePrice": 800000,
            "downPayment": 160000,
            "interestRate": 5.5,
            "currentValue": 900000
        },
        "contacts": {
            "owner": "Test Owner",
            "bank": "Test Bank",
            "contractor": "Test Contractor"
        },
        "notes": "Immeuble créé pour tester la persistance"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/buildings", json=test_building)
        if response.status_code == 200:
            new_building = response.json()
            print(f"✅ Immeuble créé avec succès (ID: {new_building['id']})")
            
            # Vérifier que les données sont bien sauvegardées
            time.sleep(2)  # Attendre un peu
            
            response = requests.get(f"{API_BASE_URL}/api/dashboard")
            dashboard_after = response.json()
            print(f"📈 Nouvelles statistiques:")
            print(f"   - Total immeubles: {dashboard_after['totalBuildings']}")
            print(f"   - Valeur portfolio: {dashboard_after['portfolioValue']:,.0f}$")
            
            if dashboard_after['portfolioValue'] > dashboard['portfolioValue']:
                print("✅ Persistance fonctionne - valeur portfolio mise à jour!")
            else:
                print("⚠️  Valeur portfolio non mise à jour")
                
        else:
            print(f"❌ Erreur création immeuble (status: {response.status_code})")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Erreur création immeuble: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test terminé")

if __name__ == "__main__":
    test_api() 