#!/usr/bin/env python3
"""
Script pour ajouter un deuxième immeuble de test
"""
import requests

# Configuration
API_URL = "https://interface-cah-backend.onrender.com"

# Deuxième immeuble avec une valeur plus élevée
second_building = {
    "name": "Complexe Maple Heights",
    "address": {
        "street": "789 Boulevard Maple",
        "city": "Laval",
        "province": "QC",
        "postalCode": "H7H 7H7",
        "country": "Canada"
    },
    "type": "Résidentiel",
    "units": 24,
    "floors": 6,
    "yearBuilt": 2019,
    "financials": {
        "purchasePrice": 1200000,
        "currentValue": 1450000,
        "downPayment": 240000,
        "interestRate": 2.8
    },
    "characteristics": {
        "parking": 30,
        "elevator": True,
        "balconies": 24,
        "storage": True,
        "laundry": True,
        "airConditioning": True,
        "heating": "central",
        "internet": True,
        "security": True
    },
    "contacts": {
        "owner": "CAH Construction Inc.",
        "bank": "Banque TD",
        "contractor": "Groupe Construction Elite"
    },
    "notes": "Complexe résidentiel haut de gamme avec vue sur rivière"
}

def main():
    try:
        print("🏗️ Création du deuxième immeuble...")
        response = requests.post(
            f"{API_URL}/api/buildings",
            headers={"Content-Type": "application/json"},
            json=second_building
        )
        
        if response.status_code == 200:
            building_data = response.json()
            print(f"✅ Immeuble créé - ID: {building_data.get('id')}")
            print(f"   Nom: {building_data.get('name')}")
            print(f"   Valeur: {building_data.get('financials', {}).get('currentValue', 0):,}$")
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            return
        
        # Vérifier le nouveau total
        print("📊 Nouveau total du portfolio...")
        dashboard_response = requests.get(f"{API_URL}/api/dashboard")
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print(f"✅ Portfolio mis à jour:")
            print(f"   Total immeubles: {dashboard_data.get('totalBuildings', 0)}")
            print(f"   Total unités: {dashboard_data.get('totalUnits', 0)}")
            print(f"   Valeur portfolio: {dashboard_data.get('portfolioValue', 0):,}$")
            print(f"   Revenus mensuels estimés: {dashboard_data.get('monthlyRevenue', 0):,.0f}$")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main() 