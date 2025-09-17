#!/usr/bin/env python3
"""
Script pour créer une transaction avec l'ancien format pour forcer la création de la table
"""

import requests
import time

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def create_old_format_transaction():
    """Créer une transaction avec l'ancien format"""
    print("🔧 Création d'une transaction avec l'ancien format...")
    
    try:
        # Récupérer un immeuble
        print("1. Récupération d'un immeuble...")
        buildings_response = requests.get(f"{RENDER_API_URL}/api/buildings")
        
        if buildings_response.status_code != 200:
            print(f"❌ Erreur buildings: {buildings_response.status_code}")
            return False
        
        buildings = buildings_response.json()
        if not buildings:
            print("❌ Aucun immeuble trouvé")
            return False
        
        building_id = buildings[0]['id_immeuble']
        print(f"   ✅ Immeuble trouvé: ID {building_id}")
        
        # Créer une transaction avec l'ANCIEN format
        print("2. Création d'une transaction avec l'ancien format...")
        old_transaction = {
            "id_immeuble": building_id,
            "type_transaction": "revenus",  # Ancien format
            "montant": 0.01,
            "description": "Test de création de table",
            "date_transaction": "2025-01-17",  # Ancien format
            "methode_paiement": "test",
            "statut": "en_attente",
            "reference": "OLD-FORMAT-TEST",
            "pdf_document": "",
            "notes": "Transaction avec ancien format pour créer la table"
        }
        
        response = requests.post(f"{RENDER_API_URL}/api/transactions", json=old_transaction)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Transaction créée avec l'ancien format!")
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

def test_after_creation():
    """Tester après création"""
    print("\n🧪 Test après création...")
    
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
    print("🚀 CRÉATION DE TABLE AVEC ANCIEN FORMAT")
    print("=" * 50)
    
    # Créer avec l'ancien format
    if create_old_format_transaction():
        print("\n⏳ Attente de la stabilisation...")
        time.sleep(3)
        
        # Tester après création
        if test_after_creation():
            print("\n🎉 TABLE CRÉÉE AVEC SUCCÈS!")
            print("✅ La table transactions existe maintenant")
            print("⚠️  Mais elle utilise encore l'ancien format")
            print("💡 Il faut maintenant déployer les nouvelles modifications")
            return True
        else:
            print("\n❌ Problème persistant après création")
            return False
    else:
        print("\n❌ Échec de la création")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Maintenant, déployez les nouvelles modifications!")
    else:
        print("\n❌ La création a échoué")
