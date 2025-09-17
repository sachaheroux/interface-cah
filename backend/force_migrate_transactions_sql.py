#!/usr/bin/env python3
"""
Script pour forcer la migration de la table transactions via SQL direct
"""

import requests
import json

# Configuration
RENDER_API_BASE = "https://interface-cah-backend.onrender.com"

def force_migrate_transactions():
    """Forcer la migration de la table transactions"""
    print("🔧 Migration forcée de la table transactions...")
    
    # Étape 1: Vérifier l'état actuel
    print("\n1. Vérification de l'état actuel...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/transactions")
        print(f"   Status: {response.status_code}")
        if response.status_code == 500:
            print("   ✅ Confirme que la table n'a pas les nouvelles colonnes")
        else:
            print("   ⚠️  Table déjà migrée ou autre problème")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Étape 2: Utiliser l'endpoint de migration
    print("\n2. Tentative de migration via endpoint...")
    try:
        # Essayer d'utiliser un endpoint de migration s'il existe
        migration_data = {
            "action": "migrate_transactions",
            "add_columns": [
                "type VARCHAR(50) DEFAULT 'depense'",
                "categorie VARCHAR(100) DEFAULT 'autre'"
            ]
        }
        
        response = requests.post(f"{RENDER_API_BASE}/api/migrate", json=migration_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Migration réussie via endpoint")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Étape 3: Essayer de créer une transaction pour forcer la migration
    print("\n3. Tentative de création pour forcer la migration...")
    try:
        # Récupérer un immeuble
        response = requests.get(f"{RENDER_API_BASE}/api/buildings")
        if response.status_code == 200:
            buildings = response.json()
            if buildings and len(buildings) > 0:
                building_id = buildings[0]['id_immeuble']
                print(f"   Utilisation de l'immeuble ID: {building_id}")
                
                # Essayer de créer une transaction avec l'ancien format d'abord
                print("\n   Test avec l'ancien format...")
                old_transaction = {
                    "id_immeuble": building_id,
                    "type_transaction": "depense",
                    "montant": -200.0,
                    "date_transaction": "2025-01-17",
                    "description": "Test migration",
                    "statut": "paye",
                    "methode_de_paiement": "virement",
                    "reference": "MIG-OLD-001",
                    "source": "Test Migration",
                    "pdf_document": "",
                    "notes": "Test avec ancien format"
                }
                
                response = requests.post(f"{RENDER_API_BASE}/api/transactions", json=old_transaction)
                print(f"   Status (ancien): {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Transaction créée avec l'ancien format")
                    print(f"   Réponse: {response.json()}")
                else:
                    print(f"   ❌ Erreur (ancien): {response.text}")
                
                # Maintenant essayer avec le nouveau format
                print("\n   Test avec le nouveau format...")
                new_transaction = {
                    "id_immeuble": building_id,
                    "type": "depense",
                    "categorie": "taxes_scolaires",
                    "montant": -200.0,
                    "date_de_transaction": "2025-01-17",
                    "methode_de_paiement": "virement",
                    "reference": "MIG-NEW-001",
                    "source": "Test Migration",
                    "pdf_transaction": "",
                    "notes": "Test avec nouveau format"
                }
                
                response = requests.post(f"{RENDER_API_BASE}/api/transactions", json=new_transaction)
                print(f"   Status (nouveau): {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Transaction créée avec le nouveau format")
                    print(f"   Réponse: {response.json()}")
                    return True
                else:
                    print(f"   ❌ Erreur (nouveau): {response.text}")
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
    """Tester l'état final"""
    print("\n4. Test de l'état final...")
    
    try:
        # Test de récupération des transactions
        response = requests.get(f"{RENDER_API_BASE}/api/transactions")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Transactions: {len(data.get('data', []))} trouvées")
            if data.get('data'):
                print(f"   Première transaction: {json.dumps(data['data'][0], indent=2)}")
        else:
            print(f"   ❌ Transactions: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    success = force_migrate_transactions()
    if success:
        test_final_state()
        print("\n🎉 Migration terminée avec succès!")
    else:
        print("\n💥 Migration échouée!")
        print("\n💡 Solution alternative: Le backend doit être redéployé avec la nouvelle structure")
