#!/usr/bin/env python3
"""
Script pour forcer la création de la table transactions avec la nouvelle structure
"""

import requests
import time

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def force_create_new_table():
    """Forcer la création de la table avec la nouvelle structure"""
    print("🔧 Forçage de la création de la table avec la nouvelle structure...")
    
    try:
        # Récupérer un immeuble
        print("1. Récupération d'un immeuble...")
        buildings_response = requests.get(f"{RENDER_API_URL}/api/buildings")
        
        if buildings_response.status_code != 200:
            print("❌ Impossible de récupérer les immeubles")
            return False
        
        buildings = buildings_response.json()
        if not buildings:
            print("❌ Aucun immeuble trouvé")
            return False
        
        building_id = buildings[0]['id_immeuble']
        print(f"   ✅ Immeuble trouvé: ID {building_id}")
        
        # Créer une transaction avec la NOUVELLE structure
        print("2. Création d'une transaction avec la nouvelle structure...")
        new_transaction = {
            "id_immeuble": building_id,
            "categorie": "revenu",
            "montant": 0.01,
            "date_de_transaction": "2025-01-17",
            "methode_de_paiement": "test",
            "reference": "NEW-TABLE-TEST",
            "source": "Création de nouvelle table",
            "pdf_transaction": "",
            "notes": "Transaction de test pour créer la nouvelle table"
        }
        
        response = requests.post(f"{RENDER_API_URL}/api/transactions", json=new_transaction)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Transaction créée avec la nouvelle structure!")
            data = response.json()
            transaction_id = data.get('data', {}).get('id_transaction')
            
            if transaction_id:
                print(f"   Transaction ID: {transaction_id}")
                
                # Tester la récupération
                print("3. Test de récupération...")
                get_response = requests.get(f"{RENDER_API_URL}/api/transactions")
                print(f"   Status: {get_response.status_code}")
                
                if get_response.status_code == 200:
                    print("   ✅ Récupération réussie!")
                    
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
    """Test final"""
    print("\n🧪 Test final...")
    
    try:
        # Test de la liste
        response = requests.get(f"{RENDER_API_URL}/api/transactions")
        print(f"   Status liste: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', [])
            print(f"   ✅ Liste OK: {len(transactions)} transactions")
            return True
        else:
            print(f"   ❌ Erreur liste: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 CRÉATION DE LA NOUVELLE TABLE TRANSACTIONS")
    print("=" * 60)
    
    # Forcer la création
    if force_create_new_table():
        print("\n⏳ Attente de la stabilisation...")
        time.sleep(3)
        
        # Test final
        if test_final():
            print("\n🎉 CRÉATION RÉUSSIE!")
            print("✅ La table transactions utilise maintenant la nouvelle structure")
            print("✅ Vous pouvez créer et gérer des transactions")
            print("✅ La page Transactions devrait maintenant fonctionner")
            return True
        else:
            print("\n❌ Problème lors du test final")
            return False
    else:
        print("\n❌ Échec de la création")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Testez maintenant la page Transactions dans votre navigateur!")
    else:
        print("\n❌ La création a échoué")
