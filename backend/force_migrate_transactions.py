#!/usr/bin/env python3
"""
Script pour forcer la migration de la table transactions sur Render
"""

import os
import sys
import requests
from datetime import datetime

# Configuration Render
RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def force_recreate_transactions():
    """Forcer la recréation de la table transactions via l'API"""
    try:
        print("🔄 Forçage de la recréation de la table transactions...")
        
        # 1. Créer une transaction de test pour déclencher la création de la table
        print("📝 Création d'une transaction de test...")
        
        test_transaction = {
            "id_immeuble": 1,  # Supposons qu'il y ait au moins un immeuble
            "categorie": "revenu",
            "montant": 0.01,
            "date_de_transaction": "2025-01-01",
            "methode_de_paiement": "test",
            "reference": "test_migration",
            "source": "Migration automatique",
            "pdf_transaction": "",
            "notes": "Transaction de test pour migration"
        }
        
        try:
            response = requests.post(f"{RENDER_API_URL}/api/transactions", json=test_transaction)
            if response.status_code == 201:
                print("✅ Transaction de test créée avec succès")
                transaction_id = response.json().get('data', {}).get('id_transaction')
                
                # Supprimer la transaction de test
                if transaction_id:
                    delete_response = requests.delete(f"{RENDER_API_URL}/api/transactions/{transaction_id}")
                    if delete_response.status_code == 200:
                        print("✅ Transaction de test supprimée")
                    else:
                        print("⚠️ Transaction de test créée mais non supprimée")
                
                return True
            else:
                print(f"❌ Erreur création transaction: {response.status_code}")
                print(f"   Détail: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la création de test: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

def test_transactions_endpoint():
    """Tester l'endpoint des transactions"""
    try:
        print("🧪 Test de l'endpoint des transactions...")
        
        response = requests.get(f"{RENDER_API_URL}/api/transactions")
        if response.status_code == 200:
            transactions = response.json().get('data', [])
            print(f"✅ Endpoint des transactions fonctionne ({len(transactions)} transactions)")
            return True
        else:
            print(f"❌ Erreur transactions: {response.status_code}")
            print(f"   Détail: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_constants_endpoint():
    """Tester l'endpoint des constantes"""
    try:
        print("🧪 Test de l'endpoint des constantes...")
        
        response = requests.get(f"{RENDER_API_URL}/api/transactions/constants")
        if response.status_code == 200:
            constants = response.json()
            print("✅ Endpoint des constantes fonctionne")
            print(f"   Catégories: {constants.get('categories', [])}")
            print(f"   Méthodes de paiement: {constants.get('payment_methods', [])}")
            return True
        else:
            print(f"❌ Erreur constantes: {response.status_code}")
            print(f"   Détail: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Migration forcée de la table transactions sur Render")
    print("=" * 60)
    
    # Test initial
    print("🔍 Test initial...")
    if test_transactions_endpoint():
        print("✅ La table transactions fonctionne déjà!")
        return True
    
    # Migration forcée
    print("\n🔄 Début de la migration forcée...")
    if not force_recreate_transactions():
        print("❌ Échec de la migration forcée")
        return False
    
    # Test final
    print("\n🧪 Test final...")
    if test_transactions_endpoint() and test_constants_endpoint():
        print("\n🎉 Migration terminée avec succès!")
        print("✅ La page Transactions devrait maintenant fonctionner")
        return True
    else:
        print("\n❌ Problème persistant après migration")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
