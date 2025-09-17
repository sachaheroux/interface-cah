#!/usr/bin/env python3
"""
Script simple pour tester la création d'une transaction sur Render
"""

import requests

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def test_transaction_creation():
    """Tester la création d'une transaction"""
    print("🧪 Test de création d'une transaction...")
    
    try:
        # Récupérer un immeuble
        buildings_response = requests.get(f"{RENDER_API_URL}/api/buildings")
        if buildings_response.status_code != 200:
            print("❌ Impossible de récupérer les immeubles")
            return False
        
        buildings = buildings_response.json()
        if not buildings:
            print("❌ Aucun immeuble trouvé")
            return False
        
        building_id = buildings[0]['id_immeuble']
        print(f"✅ Immeuble trouvé: ID {building_id}")
        
        # Créer une transaction de test
        transaction = {
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
        
        print("🔄 Création de la transaction...")
        response = requests.post(f"{RENDER_API_URL}/api/transactions", json=transaction)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Transaction créée avec succès!")
            data = response.json()
            transaction_id = data.get('data', {}).get('id_transaction')
            print(f"ID de la transaction: {transaction_id}")
            
            # Tester la récupération
            print("\n🧪 Test de récupération...")
            get_response = requests.get(f"{RENDER_API_URL}/api/transactions")
            print(f"Status récupération: {get_response.status_code}")
            
            if get_response.status_code == 200:
                print("✅ Récupération réussie!")
                transactions = get_response.json().get('data', [])
                print(f"Nombre de transactions: {len(transactions)}")
                
                # Supprimer la transaction de test
                if transaction_id:
                    print(f"\n🗑️ Suppression de la transaction de test...")
                    delete_response = requests.delete(f"{RENDER_API_URL}/api/transactions/{transaction_id}")
                    if delete_response.status_code == 200:
                        print("✅ Transaction de test supprimée")
                    else:
                        print(f"⚠️ Erreur suppression: {delete_response.status_code}")
                
                return True
            else:
                print(f"❌ Erreur récupération: {get_response.text}")
                return False
        else:
            print(f"❌ Erreur création: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 TEST DE CRÉATION DE TRANSACTION")
    print("=" * 40)
    
    if test_transaction_creation():
        print("\n🎉 SUCCÈS!")
        print("✅ La table transactions fonctionne maintenant")
        print("✅ Vous pouvez créer et gérer des transactions")
        print("✅ La page Transactions devrait maintenant fonctionner")
    else:
        print("\n❌ ÉCHEC")
        print("❌ Il y a encore un problème avec la table transactions")

if __name__ == "__main__":
    main()
