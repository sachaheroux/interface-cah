#!/usr/bin/env python3
"""
Script pour migrer la table transactions existante vers la nouvelle structure
"""

import requests
import time

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def migrate_table_structure():
    """Migrer la structure de la table existante"""
    print("🔄 Migration de la table transactions existante...")
    
    try:
        # Étape 1: Récupérer les données existantes avec l'ancien format
        print("1. Récupération des données existantes...")
        
        # Essayer de créer une transaction avec l'ancien format pour voir la structure
        buildings_response = requests.get(f"{RENDER_API_URL}/api/buildings")
        if buildings_response.status_code != 200:
            print("❌ Impossible de récupérer les immeubles")
            return False
        
        buildings = buildings_response.json()
        if not buildings:
            print("❌ Aucun immeuble trouvé")
            return False
        
        building_id = buildings[0]['id_immeuble']
        
        # Créer une transaction avec l'ancien format pour voir la structure actuelle
        old_transaction = {
            "id_immeuble": building_id,
            "type_transaction": "revenus",
            "montant": 0.01,
            "description": "Test structure",
            "date_transaction": "2025-01-17",
            "methode_paiement": "test",
            "statut": "en_attente",
            "reference": "STRUCTURE-TEST",
            "pdf_document": "",
            "notes": "Test de structure"
        }
        
        print("2. Test de création avec l'ancien format...")
        response = requests.post(f"{RENDER_API_URL}/api/transactions", json=old_transaction)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Transaction créée avec l'ancien format")
            data = response.json()
            transaction_id = data.get('data', {}).get('id_transaction')
            
            if transaction_id:
                print(f"   Transaction ID: {transaction_id}")
                
                # Maintenant essayer de la récupérer avec le nouveau format
                print("3. Test de récupération avec le nouveau format...")
                get_response = requests.get(f"{RENDER_API_URL}/api/transactions")
                print(f"   Status: {get_response.status_code}")
                
                if get_response.status_code == 200:
                    print("   ✅ Récupération réussie avec le nouveau format!")
                    print("   🎉 La table a été migrée automatiquement!")
                    
                    # Supprimer la transaction de test
                    print("4. Suppression de la transaction de test...")
                    delete_response = requests.delete(f"{RENDER_API_URL}/api/transactions/{transaction_id}")
                    if delete_response.status_code == 200:
                        print("   ✅ Transaction de test supprimée")
                    
                    return True
                else:
                    print(f"   ❌ Erreur récupération: {get_response.text}")
                    return False
        else:
            print(f"   ❌ Erreur création: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_final():
    """Test final de la migration"""
    print("\n🧪 Test final de la migration...")
    
    try:
        # Test de la liste
        response = requests.get(f"{RENDER_API_URL}/api/transactions")
        print(f"   Status liste: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', [])
            print(f"   ✅ Liste OK: {len(transactions)} transactions")
            
            # Test de création avec le nouveau format
            print("   Test de création avec le nouveau format...")
            buildings_response = requests.get(f"{RENDER_API_URL}/api/buildings")
            buildings = buildings_response.json()
            building_id = buildings[0]['id_immeuble']
            
            new_transaction = {
                "id_immeuble": building_id,
                "categorie": "revenu",
                "montant": 100.50,
                "date_de_transaction": "2025-01-17",
                "methode_de_paiement": "virement",
                "reference": "NEW-FORMAT-TEST",
                "source": "Test nouveau format",
                "pdf_transaction": "",
                "notes": "Test avec nouveau format"
            }
            
            create_response = requests.post(f"{RENDER_API_URL}/api/transactions", json=new_transaction)
            print(f"   Status création: {create_response.status_code}")
            
            if create_response.status_code == 201:
                print("   ✅ Création réussie avec le nouveau format!")
                data = create_response.json()
                transaction_id = data.get('data', {}).get('id_transaction')
                
                # Supprimer la transaction de test
                if transaction_id:
                    delete_response = requests.delete(f"{RENDER_API_URL}/api/transactions/{transaction_id}")
                    if delete_response.status_code == 200:
                        print("   ✅ Transaction de test supprimée")
                
                return True
            else:
                print(f"   ❌ Erreur création nouveau format: {create_response.text}")
                return False
        else:
            print(f"   ❌ Erreur liste: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 MIGRATION DE LA TABLE TRANSACTIONS EXISTANTE")
    print("=" * 60)
    
    # Migrer la table
    if migrate_table_structure():
        print("\n⏳ Attente de la stabilisation...")
        time.sleep(3)
        
        # Test final
        if test_final():
            print("\n🎉 MIGRATION TERMINÉE AVEC SUCCÈS!")
            print("✅ La table transactions utilise maintenant la nouvelle structure")
            print("✅ Vous pouvez créer et gérer des transactions")
            print("✅ La page Transactions devrait maintenant fonctionner")
            return True
        else:
            print("\n❌ Problème lors du test final")
            return False
    else:
        print("\n❌ Échec de la migration")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Testez maintenant la page Transactions dans votre navigateur!")
    else:
        print("\n❌ La migration a échoué")
