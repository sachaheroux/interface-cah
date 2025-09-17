#!/usr/bin/env python3
"""
Script pour créer une transaction avec l'ancien format sur Render
"""

import requests

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def create_old_format_transaction():
    """Créer une transaction avec l'ancien format"""
    print("🔧 Création d'une transaction avec l'ancien format...")
    
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
        
        # Créer une transaction avec l'ANCIEN format
        transaction = {
            "id_immeuble": building_id,
            "type_transaction": "revenus",  # Ancien format
            "montant": 100.50,
            "description": "Test avec ancien format",
            "date_transaction": "2025-01-17",  # Ancien format
            "methode_paiement": "virement",
            "statut": "en_attente",
            "reference": "OLD-FORMAT-001",
            "pdf_document": "",
            "notes": "Transaction avec ancien format"
        }
        
        print("🔄 Création de la transaction avec l'ancien format...")
        response = requests.post(f"{RENDER_API_URL}/api/transactions", json=transaction)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Transaction créée avec l'ancien format!")
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
    print("🚀 CRÉATION AVEC ANCIEN FORMAT")
    print("=" * 40)
    
    if create_old_format_transaction():
        print("\n🎉 SUCCÈS!")
        print("✅ La table transactions fonctionne avec l'ancien format")
        print("⚠️  Mais il faut maintenant déployer les nouvelles modifications")
        print("💡 Une fois déployé, la page Transactions fonctionnera")
    else:
        print("\n❌ ÉCHEC")
        print("❌ Il y a encore un problème avec la table transactions")

if __name__ == "__main__":
    main()
