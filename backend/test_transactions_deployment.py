#!/usr/bin/env python3
"""
Script pour tester le déploiement des transactions sur Render
"""

import requests
import time
import sys

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def test_constants():
    """Tester l'endpoint des constantes"""
    try:
        print("🧪 Test des constantes...")
        response = requests.get(f"{RENDER_API_URL}/api/transactions/constants")
        
        if response.status_code == 200:
            constants = response.json()
            print("✅ Constantes récupérées avec succès")
            print(f"   Catégories: {constants.get('categories', [])}")
            print(f"   Méthodes de paiement: {constants.get('payment_methods', [])}")
            
            # Vérifier que les nouvelles catégories sont présentes
            if 'revenu' in constants.get('categories', []) and 'depense' in constants.get('categories', []):
                print("✅ Nouvelles catégories présentes")
                return True
            else:
                print("❌ Nouvelles catégories manquantes")
                return False
        else:
            print(f"❌ Erreur constantes: {response.status_code}")
            print(f"   Détail: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test des constantes: {e}")
        return False

def test_transactions_list():
    """Tester l'endpoint de liste des transactions"""
    try:
        print("🧪 Test de la liste des transactions...")
        response = requests.get(f"{RENDER_API_URL}/api/transactions")
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', [])
            print(f"✅ Liste des transactions récupérée ({len(transactions)} transactions)")
            return True
        else:
            print(f"❌ Erreur liste transactions: {response.status_code}")
            print(f"   Détail: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de la liste: {e}")
        return False

def test_create_transaction():
    """Tester la création d'une transaction"""
    try:
        print("🧪 Test de création d'une transaction...")
        
        # D'abord, récupérer un immeuble existant
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
            "montant": 100.50,
            "date_de_transaction": "2025-01-17",
            "methode_de_paiement": "virement",
            "reference": "TEST-001",
            "source": "Test automatique",
            "pdf_transaction": "",
            "notes": "Transaction de test"
        }
        
        response = requests.post(f"{RENDER_API_URL}/api/transactions", json=test_transaction)
        
        if response.status_code == 201:
            data = response.json()
            transaction = data.get('data', {})
            print("✅ Transaction créée avec succès")
            print(f"   ID: {transaction.get('id_transaction')}")
            print(f"   Catégorie: {transaction.get('categorie')}")
            print(f"   Montant: {transaction.get('montant')}")
            
            # Supprimer la transaction de test
            transaction_id = transaction.get('id_transaction')
            if transaction_id:
                delete_response = requests.delete(f"{RENDER_API_URL}/api/transactions/{transaction_id}")
                if delete_response.status_code == 200:
                    print("✅ Transaction de test supprimée")
                else:
                    print("⚠️ Transaction créée mais non supprimée")
            
            return True
        else:
            print(f"❌ Erreur création transaction: {response.status_code}")
            print(f"   Détail: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de création: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test du déploiement des transactions sur Render")
    print("=" * 55)
    
    # Attendre un peu pour que le déploiement se termine
    print("⏳ Attente du déploiement...")
    time.sleep(30)
    
    # Tests
    tests = [
        ("Constantes", test_constants),
        ("Liste des transactions", test_transactions_list),
        ("Création de transaction", test_create_transaction)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
        
        if not success:
            print(f"❌ Échec du test: {test_name}")
            break
    
    # Résumé
    print("\n" + "=" * 55)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 55)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASSÉ" if success else "❌ ÉCHEC"
        print(f"{status} - {test_name}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ La page Transactions devrait maintenant fonctionner parfaitement")
        print("✅ Vous pouvez maintenant créer et gérer des transactions")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("⚠️ Le déploiement n'est pas encore complet")
        print("   Veuillez attendre quelques minutes et relancer ce script")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
