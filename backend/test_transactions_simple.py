#!/usr/bin/env python3
"""
Script simple pour tester les transactions sur Render
"""

import requests
import json

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def test_constants():
    """Tester l'endpoint des constantes"""
    print("🧪 Test des constantes...")
    try:
        response = requests.get(f"{RENDER_API_URL}/api/transactions-constants")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Constantes: {data}")
            return True
        else:
            print(f"❌ Erreur: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_transactions():
    """Tester l'endpoint des transactions"""
    print("\n🧪 Test des transactions...")
    try:
        response = requests.get(f"{RENDER_API_URL}/api/transactions")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Transactions: {len(data.get('data', []))} trouvées")
            return True
        else:
            print(f"❌ Erreur: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_buildings():
    """Tester l'endpoint des immeubles"""
    print("\n🧪 Test des immeubles...")
    try:
        response = requests.get(f"{RENDER_API_URL}/api/buildings")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            buildings = data.get('data', []) if isinstance(data, dict) else data
            print(f"✅ Immeubles: {len(buildings)} trouvés")
            if buildings:
                print(f"   Premier immeuble: {buildings[0]}")
                return buildings[0].get('id_immeuble') if isinstance(buildings[0], dict) else buildings[0].id_immeuble
            return None
        else:
            print(f"❌ Erreur: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_create_transaction(building_id):
    """Tester la création d'une transaction"""
    print(f"\n🧪 Test de création de transaction (immeuble {building_id})...")
    try:
        transaction_data = {
            "id_immeuble": building_id,
            "categorie": "revenu",
            "montant": 100.50,
            "date_de_transaction": "2025-01-17",
            "methode_de_paiement": "virement",
            "reference": "TEST-001",
            "source": "Test automatique",
            "pdf_transaction": "",
            "notes": "Transaction de test"
        }
        
        response = requests.post(f"{RENDER_API_URL}/api/transactions", json=transaction_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Transaction créée: {data}")
            return data.get('data', {}).get('id_transaction')
        else:
            print(f"❌ Erreur: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Fonction principale"""
    print("🚀 Test simple des transactions sur Render")
    print("=" * 50)
    
    # Test des constantes
    if not test_constants():
        print("\n❌ Problème avec les constantes")
        return False
    
    # Test des immeubles
    building_id = test_buildings()
    if not building_id:
        print("\n❌ Aucun immeuble trouvé")
        return False
    
    # Test des transactions
    if not test_transactions():
        print("\n❌ Problème avec les transactions")
        return False
    
    # Test de création
    transaction_id = test_create_transaction(building_id)
    if transaction_id:
        print(f"\n✅ Transaction créée avec succès (ID: {transaction_id})")
        
        # Supprimer la transaction de test
        try:
            delete_response = requests.delete(f"{RENDER_API_URL}/api/transactions/{transaction_id}")
            if delete_response.status_code == 200:
                print("✅ Transaction de test supprimée")
        except:
            print("⚠️ Transaction créée mais non supprimée")
    
    print("\n🎉 Tous les tests sont passés!")
    return True

if __name__ == "__main__":
    main()
