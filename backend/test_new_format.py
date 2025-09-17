#!/usr/bin/env python3
"""
Script pour tester le nouveau format français sur Render
"""

import requests
import time

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def test_new_format():
    """Tester le nouveau format français"""
    print("🧪 Test du nouveau format français...")
    
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
        
        # Créer une transaction avec le NOUVEAU format français
        transaction = {
            "id_immeuble": building_id,
            "categorie": "revenu",
            "montant": 100.50,
            "date_de_transaction": "2025-01-17",
            "methode_de_paiement": "virement",
            "reference": "NEW-FORMAT-001",
            "source": "Test nouveau format",
            "pdf_transaction": "",
            "notes": "Transaction avec nouveau format français"
        }
        
        print("🔄 Création de la transaction avec le nouveau format...")
        response = requests.post(f"{RENDER_API_URL}/api/transactions", json=transaction)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Transaction créée avec le nouveau format!")
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
    print("🚀 TEST DU NOUVEAU FORMAT FRANÇAIS")
    print("=" * 50)
    
    # Attendre un peu pour que le déploiement se termine
    print("⏳ Attente du déploiement...")
    time.sleep(30)
    
    if test_new_format():
        print("\n🎉 SUCCÈS!")
        print("✅ Le nouveau format français fonctionne")
        print("✅ Vous pouvez créer et gérer des transactions")
        print("✅ La page Transactions devrait maintenant fonctionner")
    else:
        print("\n❌ ÉCHEC")
        print("❌ Le nouveau format ne fonctionne pas encore")
        print("💡 Il faut attendre que le déploiement se termine")

if __name__ == "__main__":
    main()
