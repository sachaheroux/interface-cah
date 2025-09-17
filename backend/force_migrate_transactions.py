#!/usr/bin/env python3
"""
Script pour forcer la migration de la table transactions sur Render
"""

import requests
import time

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def force_migration():
    """Forcer la migration en créant une transaction de test"""
    print("🔄 Forçage de la migration de la table transactions...")
    
    try:
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
        
        # Créer une transaction de test pour forcer la création de la table
        test_transaction = {
            "id_immeuble": building_id,
            "categorie": "revenu",
            "montant": 0.01,
            "date_de_transaction": "2025-01-17",
            "methode_de_paiement": "test",
            "reference": "MIGRATION-FORCE",
            "source": "Migration forcée",
            "pdf_transaction": "",
            "notes": "Transaction de test pour forcer la migration"
        }
        
        print("   Création d'une transaction de test...")
        response = requests.post(f"{RENDER_API_URL}/api/transactions", json=test_transaction)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Transaction créée avec succès - Migration forcée!")
            transaction_id = response.json().get('data', {}).get('id_transaction')
            
            # Supprimer la transaction de test
            if transaction_id:
                print("   Suppression de la transaction de test...")
                delete_response = requests.delete(f"{RENDER_API_URL}/api/transactions/{transaction_id}")
                if delete_response.status_code == 200:
                    print("✅ Transaction de test supprimée")
                else:
                    print("⚠️ Transaction créée mais non supprimée")
            
            return True
        else:
            print(f"❌ Erreur lors de la création: {response.status_code}")
            print(f"   Détail: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration forcée: {e}")
        return False

def test_after_migration():
    """Tester après la migration"""
    print("\n🧪 Test après migration...")
    
    try:
        # Test de la liste des transactions
        response = requests.get(f"{RENDER_API_URL}/api/transactions")
        print(f"   Status liste: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', [])
            print(f"✅ Liste des transactions: {len(transactions)} transactions")
            return True
        else:
            print(f"❌ Erreur liste: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Migration forcée de la table transactions sur Render")
    print("=" * 60)
    
    # Forcer la migration
    if force_migration():
        print("\n⏳ Attente de la stabilisation...")
        time.sleep(5)
        
        # Tester après migration
        if test_after_migration():
            print("\n🎉 Migration terminée avec succès!")
            print("✅ La page Transactions devrait maintenant fonctionner")
            return True
        else:
            print("\n❌ Problème persistant après migration")
            return False
    else:
        print("\n❌ Échec de la migration forcée")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Vous pouvez maintenant tester la page Transactions!")
    else:
        print("\n❌ La migration a échoué")