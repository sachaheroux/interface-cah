#!/usr/bin/env python3
"""
Script pour ajouter un immeuble de test avec des données financières
"""
import requests
import json

# Configuration
API_URL = "https://interface-cah-backend.onrender.com"

# Données de l'immeuble de test
test_building = {
    "name": "Immeuble Portfolio Test",
    "address": {
        "street": "456 Rue Portfolio",
        "city": "Montreal",
        "province": "QC",
        "postalCode": "H2H 2H2",
        "country": "Canada"
    },
    "type": "Résidentiel",
    "units": 15,
    "floors": 4,
    "yearBuilt": 2021,
    "financials": {
        "purchasePrice": 800000,
        "currentValue": 950000,
        "downPayment": 160000,
        "interestRate": 3.2
    },
    "characteristics": {
        "parking": 20,
        "elevator": True,
        "balconies": 15,
        "storage": True,
        "laundry": True,
        "airConditioning": True,
        "heating": "central",
        "internet": True,
        "security": True
    },
    "contacts": {
        "owner": "CAH Construction Inc.",
        "bank": "Banque Nationale",
        "contractor": "Constructions Pro"
    },
    "notes": "Immeuble de test pour validation du calcul de portfolio"
}

def main():
    try:
        # Vérifier l'état de l'API
        print("🔍 Vérification de l'API...")
        health_response = requests.get(f"{API_URL}/health")
        if health_response.status_code == 200:
            print("✅ API disponible")
        else:
            print("❌ API non disponible")
            return
        
        # Créer l'immeuble
        print("🏗️ Création de l'immeuble de test...")
        response = requests.post(
            f"{API_URL}/api/buildings",
            headers={"Content-Type": "application/json"},
            json=test_building
        )
        
        if response.status_code == 200:
            building_data = response.json()
            print(f"✅ Immeuble créé avec succès - ID: {building_data.get('id')}")
            print(f"   Nom: {building_data.get('name')}")
            print(f"   Valeur: {building_data.get('financials', {}).get('currentValue', 0):,}$")
        else:
            print(f"❌ Erreur lors de la création: {response.status_code}")
            print(f"   Détails: {response.text}")
            return
        
        # Vérifier le tableau de bord
        print("📊 Vérification du tableau de bord...")
        dashboard_response = requests.get(f"{API_URL}/api/dashboard")
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print(f"✅ Tableau de bord mis à jour:")
            print(f"   Total immeubles: {dashboard_data.get('totalBuildings', 0)}")
            print(f"   Total unités: {dashboard_data.get('totalUnits', 0)}")
            print(f"   Valeur portfolio: {dashboard_data.get('portfolioValue', 0):,}$")
            print(f"   Revenus mensuels estimés: {dashboard_data.get('monthlyRevenue', 0):,.0f}$")
        else:
            print(f"❌ Erreur tableau de bord: {dashboard_response.status_code}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main() 