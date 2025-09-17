#!/usr/bin/env python3
"""
Script pour migrer la table transactions sur Render avec les nouvelles colonnes
"""

import requests
import json

# Configuration
RENDER_API_BASE = "https://interface-cah-backend.onrender.com"

def migrate_transactions_table():
    """Migrer la table transactions sur Render"""
    print("🔄 Migration de la table transactions sur Render...")
    
    # Étape 1: Récupérer les données existantes
    print("\n1. Récupération des données existantes...")
    try:
        # Utiliser l'ancien endpoint qui fonctionne
        response = requests.get(f"{RENDER_API_BASE}/api/transactions")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', [])
            print(f"   Nombre de transactions trouvées: {len(transactions)}")
            
            if transactions:
                print("   Première transaction (ancien format):")
                print(f"   {json.dumps(transactions[0], indent=2)}")
        else:
            print(f"   Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False
    
    # Étape 2: Créer une transaction de test avec le nouveau format
    print("\n2. Test de création avec le nouveau format...")
    try:
        # Récupérer un immeuble
        response = requests.get(f"{RENDER_API_BASE}/api/buildings")
        if response.status_code == 200:
            buildings = response.json()
            if buildings and len(buildings) > 0:
                building_id = buildings[0]['id_immeuble']
                print(f"   Utilisation de l'immeuble ID: {building_id}")
                
                # Créer une transaction de test
                test_transaction = {
                    "id_immeuble": building_id,
                    "type": "depense",
                    "categorie": "taxes_scolaires",
                    "montant": -200.0,
                    "date_de_transaction": "2025-01-17",
                    "methode_de_paiement": "virement",
                    "reference": "MIGRATION-TEST-001",
                    "source": "Test Migration",
                    "pdf_transaction": "",
                    "notes": "Test de migration de la table"
                }
                
                response = requests.post(f"{RENDER_API_BASE}/api/transactions", json=test_transaction)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Migration réussie! La table a été mise à jour.")
                    print(f"   Transaction créée: {response.json()}")
                    return True
                else:
                    print(f"   ❌ Erreur lors de la création: {response.text}")
                    return False
            else:
                print("   ❌ Aucun immeuble trouvé")
                return False
        else:
            print(f"   ❌ Erreur lors de la récupération des immeubles: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_final_state():
    """Tester l'état final après migration"""
    print("\n3. Test de l'état final...")
    
    try:
        # Test des constantes
        response = requests.get(f"{RENDER_API_BASE}/api/transactions-constants")
        if response.status_code == 200:
            print("   ✅ Constantes: OK")
        else:
            print(f"   ❌ Constantes: {response.status_code}")
        
        # Test de récupération des transactions
        response = requests.get(f"{RENDER_API_BASE}/api/transactions")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Transactions: {len(data.get('data', []))} trouvées")
        else:
            print(f"   ❌ Transactions: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    success = migrate_transactions_table()
    if success:
        test_final_state()
        print("\n🎉 Migration terminée avec succès!")
    else:
        print("\n💥 Migration échouée!")
