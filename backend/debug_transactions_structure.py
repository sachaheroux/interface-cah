#!/usr/bin/env python3
"""
Script pour diagnostiquer la structure de la table transactions sur Render
"""

import requests
import json

# Configuration
RENDER_API_BASE = "https://interface-cah-backend.onrender.com"

def test_endpoints():
    """Tester les endpoints de transactions"""
    print("🔍 Diagnostic des endpoints de transactions sur Render...")
    
    # Test 1: Constantes
    print("\n1. Test des constantes...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/transactions-constants")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Types: {data.get('types', [])}")
            print(f"   Catégories: {data.get('categories', [])}")
        else:
            print(f"   Erreur: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Récupération des transactions
    print("\n2. Test de récupération des transactions...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/transactions")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Nombre de transactions: {len(data.get('data', []))}")
        else:
            print(f"   Erreur: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Récupération des immeubles
    print("\n3. Test de récupération des immeubles...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/buildings")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Nombre d'immeubles: {len(data.get('data', []))}")
            if data.get('data'):
                print(f"   Premier immeuble: {data['data'][0].get('nom_immeuble', 'N/A')}")
        else:
            print(f"   Erreur: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

def test_transaction_creation():
    """Tester la création d'une transaction"""
    print("\n4. Test de création d'une transaction...")
    
    # D'abord récupérer un immeuble
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/buildings")
        if response.status_code == 200:
            data = response.json()
            buildings = data.get('data', [])
            if buildings:
                building_id = buildings[0]['id_immeuble']
                print(f"   Utilisation de l'immeuble ID: {building_id}")
                
                # Test avec l'ancien format
                print("\n   Test avec l'ancien format...")
                old_transaction = {
                    "id_immeuble": building_id,
                    "type_transaction": "depense",
                    "montant": -200.0,
                    "date_transaction": "2025-01-17",
                    "description": "Test ancien format",
                    "statut": "paye",
                    "methode_de_paiement": "virement",
                    "reference": "TEST-OLD-001",
                    "source": "Test Company",
                    "pdf_document": "",
                    "notes": "Test avec ancien format"
                }
                
                response = requests.post(f"{RENDER_API_BASE}/api/transactions", json=old_transaction)
                print(f"   Status (ancien): {response.status_code}")
                if response.status_code != 200:
                    print(f"   Erreur (ancien): {response.text}")
                
                # Test avec le nouveau format
                print("\n   Test avec le nouveau format...")
                new_transaction = {
                    "id_immeuble": building_id,
                    "type": "depense",
                    "categorie": "taxes_scolaires",
                    "montant": -200.0,
                    "date_de_transaction": "2025-01-17",
                    "methode_de_paiement": "virement",
                    "reference": "TEST-NEW-001",
                    "source": "Test Company",
                    "pdf_transaction": "",
                    "notes": "Test avec nouveau format"
                }
                
                response = requests.post(f"{RENDER_API_BASE}/api/transactions", json=new_transaction)
                print(f"   Status (nouveau): {response.status_code}")
                if response.status_code != 200:
                    print(f"   Erreur (nouveau): {response.text}")
                else:
                    print(f"   Succès! Transaction créée: {response.json()}")
                    
            else:
                print("   Aucun immeuble trouvé")
        else:
            print(f"   Erreur lors de la récupération des immeubles: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_endpoints()
    test_transaction_creation()
