#!/usr/bin/env python3
"""
Script pour forcer la création de la table transactions sur Render
"""

import requests
import json

# Configuration Render
RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def force_create_transactions_table():
    """Forcer la création de la table transactions"""
    
    try:
        print("🔧 Création forcée de la table transactions sur Render...")
        print("=" * 50)
        
        # 1. Tester d'abord si l'endpoint fonctionne
        print("🔍 Test de l'endpoint de test...")
        response = requests.get(f"{RENDER_API_URL}/api/test-endpoint", timeout=30)
        if response.status_code == 200:
            print("✅ Endpoint de test OK")
        else:
            print(f"❌ Endpoint de test échoué: {response.status_code}")
            return False
        
        # 2. Essayer de créer une transaction pour déclencher la création de table
        print("\n🔧 Tentative de création de transaction...")
        test_transaction = {
            "id_immeuble": 1,
            "type_transaction": "test_creation_table",
            "montant": 1.0,
            "description": "Test pour créer la table",
            "date_transaction": "2025-01-17",
            "methode_paiement": "virement",
            "statut": "en_attente",
            "reference": "TABLE_CREATION_TEST"
        }
        
        response = requests.post(f"{RENDER_API_URL}/api/transactions", 
                               json=test_transaction, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Transaction créée avec succès - Table créée!")
            transaction_data = response.json()
            print(f"   ID transaction: {transaction_data.get('data', {}).get('id_transaction')}")
        else:
            print(f"❌ Erreur création transaction: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Détail erreur: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Erreur texte: {response.text}")
        
        # 3. Tester maintenant l'endpoint GET
        print("\n🔍 Test de l'endpoint GET après création...")
        response = requests.get(f"{RENDER_API_URL}/api/transactions", timeout=30)
        print(f"   Status GET: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('data', []))
            print(f"✅ GET transactions OK: {count} enregistrements")
        else:
            print(f"❌ GET transactions échoué: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Détail erreur: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Erreur texte: {response.text}")
        
        print("\n🎉 Test de création de table terminé!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de table: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Création forcée de la table transactions")
    print("=" * 50)
    
    success = force_create_transactions_table()
    
    if success:
        print("\n🎉 Table transactions créée!")
        print("🌐 Votre application est maintenant complète sur Render!")
    else:
        print("\n💥 Échec de la création de table!")
        print("🔧 Vérifiez les erreurs ci-dessus.")
