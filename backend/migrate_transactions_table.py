#!/usr/bin/env python3
"""
Script pour migrer la table transactions sur Render vers la nouvelle structure
"""

import requests
import time
import sys

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def create_test_transaction():
    """Créer une transaction de test pour forcer la création de la table"""
    try:
        print("🔄 Création d'une transaction de test...")
        
        # Récupérer un immeuble
        buildings_response = requests.get(f"{RENDER_API_URL}/api/buildings")
        if buildings_response.status_code != 200:
            print("❌ Impossible de récupérer les immeubles")
            return False
        
        buildings = buildings_response.json().get('data', [])
        if not buildings:
            print("❌ Aucun immeuble trouvé")
            return False
        
        building_id = buildings[0]['id_immeuble']
        print(f"   Utilisation de l'immeuble ID: {building_id}")
        
        # Créer une transaction de test
        test_transaction = {
            "id_immeuble": building_id,
            "categorie": "revenu",
            "montant": 0.01,
            "date_de_transaction": "2025-01-17",
            "methode_de_paiement": "test",
            "reference": "MIGRATION-TEST",
            "source": "Migration automatique",
            "pdf_transaction": "",
            "notes": "Transaction de test pour migration"
        }
        
        response = requests.post(f"{RENDER_API_URL}/api/transactions", json=test_transaction)
        
        if response.status_code == 201:
            print("✅ Transaction de test créée avec succès")
            transaction_id = response.json().get('data', {}).get('id_transaction')
            
            # Supprimer la transaction de test
            if transaction_id:
                delete_response = requests.delete(f"{RENDER_API_URL}/api/transactions/{transaction_id}")
                if delete_response.status_code == 200:
                    print("✅ Transaction de test supprimée")
            
            return True
        else:
            print(f"❌ Erreur création transaction: {response.status_code}")
            print(f"   Détail: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de test: {e}")
        return False

def test_endpoints():
    """Tester tous les endpoints"""
    try:
        print("🧪 Test des endpoints...")
        
        # Test des constantes
        constants_response = requests.get(f"{RENDER_API_URL}/api/transactions-constants")
        if constants_response.status_code == 200:
            print("✅ Constantes récupérées")
            constants = constants_response.json()
            print(f"   Catégories: {constants.get('categories', [])}")
        else:
            print(f"❌ Erreur constantes: {constants_response.status_code}")
            return False
        
        # Test de la liste des transactions
        transactions_response = requests.get(f"{RENDER_API_URL}/api/transactions")
        if transactions_response.status_code == 200:
            print("✅ Liste des transactions récupérée")
            transactions = transactions_response.json().get('data', [])
            print(f"   Nombre de transactions: {len(transactions)}")
        else:
            print(f"❌ Erreur liste transactions: {transactions_response.status_code}")
            print(f"   Détail: {transactions_response.text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Migration de la table transactions sur Render")
    print("=" * 50)
    
    # Attendre un peu
    print("⏳ Attente de la stabilisation...")
    time.sleep(5)
    
    # Créer une transaction de test pour forcer la migration
    if create_test_transaction():
        print("\n✅ Migration forcée réussie")
    else:
        print("\n❌ Échec de la migration forcée")
        return False
    
    # Tester les endpoints
    print("\n🧪 Test des endpoints...")
    if test_endpoints():
        print("\n🎉 Migration terminée avec succès!")
        print("✅ La page Transactions devrait maintenant fonctionner")
        return True
    else:
        print("\n❌ Problème persistant après migration")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
