#!/usr/bin/env python3
"""
Script pour forcer la création de la table transactions avec la nouvelle structure
"""

import requests
import time

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def fix_transactions_table():
    """Forcer la création de la table transactions"""
    print("🔧 Correction de la table transactions...")
    
    try:
        # Récupérer un immeuble (on sait que buildings retourne une liste directe)
        print("1. Récupération d'un immeuble...")
        buildings_response = requests.get(f"{RENDER_API_URL}/api/buildings")
        
        if buildings_response.status_code != 200:
            print(f"❌ Erreur buildings: {buildings_response.status_code}")
            return False
        
        buildings = buildings_response.json()  # Liste directe, pas d'objet data
        if not buildings:
            print("❌ Aucun immeuble trouvé")
            return False
        
        building_id = buildings[0]['id_immeuble']
        print(f"   ✅ Immeuble trouvé: ID {building_id}")
        
        # Créer une transaction de test pour forcer la création de la table
        print("2. Création d'une transaction de test...")
        test_transaction = {
            "id_immeuble": building_id,
            "categorie": "revenu",
            "montant": 0.01,
            "date_de_transaction": "2025-01-17",
            "methode_de_paiement": "test",
            "reference": "FIX-TABLE-TEST",
            "source": "Correction de table",
            "pdf_transaction": "",
            "notes": "Transaction de test pour créer la table"
        }
        
        response = requests.post(f"{RENDER_API_URL}/api/transactions", json=test_transaction)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Transaction créée - Table migrée!")
            data = response.json()
            transaction_id = data.get('data', {}).get('id_transaction')
            
            if transaction_id:
                print(f"   Transaction ID: {transaction_id}")
                
                # Supprimer la transaction de test
                print("3. Suppression de la transaction de test...")
                delete_response = requests.delete(f"{RENDER_API_URL}/api/transactions/{transaction_id}")
                if delete_response.status_code == 200:
                    print("   ✅ Transaction de test supprimée")
                else:
                    print(f"   ⚠️ Erreur suppression: {delete_response.status_code}")
            
            return True
        else:
            print(f"   ❌ Erreur création: {response.status_code}")
            print(f"   Détail: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_transactions_after_fix():
    """Tester les transactions après correction"""
    print("\n🧪 Test des transactions après correction...")
    
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
    print("🚀 CORRECTION DE LA TABLE TRANSACTIONS")
    print("=" * 50)
    
    # Corriger la table
    if fix_transactions_table():
        print("\n⏳ Attente de la stabilisation...")
        time.sleep(3)
        
        # Tester après correction
        if test_transactions_after_fix():
            print("\n🎉 CORRECTION RÉUSSIE!")
            print("✅ La page Transactions devrait maintenant fonctionner")
            print("✅ Vous pouvez créer et gérer des transactions")
            return True
        else:
            print("\n❌ Problème persistant après correction")
            return False
    else:
        print("\n❌ Échec de la correction")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Testez maintenant la page Transactions dans votre navigateur!")
    else:
        print("\n❌ La correction a échoué")
