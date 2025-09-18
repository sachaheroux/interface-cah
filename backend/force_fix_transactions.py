#!/usr/bin/env python3
"""
Script pour forcer la correction de la table transactions sur Render
"""

import requests
import json

# Configuration
RENDER_API_BASE = "https://interface-cah-backend.onrender.com"

def force_fix_transactions():
    """Forcer la correction de la table transactions"""
    print("🔧 Correction forcée de la table transactions sur Render...")
    
    # Étape 1: Vérifier l'état actuel
    print("\n1. Vérification de l'état actuel...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/transactions")
        print(f"   Status: {response.status_code}")
        if response.status_code == 500:
            error_detail = response.json().get('detail', '')
            if 'no such column: transactions.type' in error_detail:
                print("   ✅ Confirme que la table n'a pas les colonnes type et categorie")
            else:
                print(f"   ❌ Autre erreur: {error_detail}")
        else:
            print("   ⚠️  Table déjà corrigée ou autre problème")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Étape 2: Essayer de créer une transaction pour forcer la migration
    print("\n2. Tentative de création pour forcer la migration...")
    try:
        # Récupérer un immeuble
        response = requests.get(f"{RENDER_API_BASE}/api/buildings")
        if response.status_code == 200:
            buildings = response.json()
            if buildings and len(buildings) > 0:
                building_id = buildings[0]['id_immeuble']
                print(f"   Utilisation de l'immeuble ID: {building_id}")
                
                # Essayer de créer une transaction avec l'ancien format d'abord
                print("\n   Test avec l'ancien format (pour forcer la migration)...")
                old_transaction = {
                    "id_immeuble": building_id,
                    "type_transaction": "depense",
                    "montant": -200.0,
                    "date_transaction": "2025-01-17",
                    "description": "Test migration forcée",
                    "statut": "paye",
                    "methode_de_paiement": "virement",
                    "reference": "FORCE-MIG-001",
                    "source": "Test Migration Forcée",
                    "pdf_document": "",
                    "notes": "Test pour forcer la migration de la table"
                }
                
                response = requests.post(f"{RENDER_API_BASE}/api/transactions", json=old_transaction)
                print(f"   Status (ancien): {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Transaction créée avec l'ancien format")
                    print(f"   Réponse: {response.json()}")
                    
                    # Maintenant essayer de récupérer les transactions
                    print("\n   Test de récupération après création...")
                    response = requests.get(f"{RENDER_API_BASE}/api/transactions")
                    print(f"   Status (GET): {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"   ✅ Transactions récupérées: {len(data.get('data', []))}")
                        return True
                    else:
                        print(f"   ❌ Erreur GET: {response.text}")
                else:
                    print(f"   ❌ Erreur (ancien): {response.text}")
                    
                    # Si l'ancien format ne marche pas, essayer le nouveau
                    print("\n   Test avec le nouveau format...")
                    new_transaction = {
                        "id_immeuble": building_id,
                        "type": "depense",
                        "categorie": "taxes_scolaires",
                        "montant": -200.0,
                        "date_de_transaction": "2025-01-17",
                        "methode_de_paiement": "virement",
                        "reference": "FORCE-NEW-001",
                        "source": "Test Migration Forcée",
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
    print("\n3. Test de l'état final...")
    
    try:
        # Test de récupération des transactions
        response = requests.get(f"{RENDER_API_BASE}/api/transactions")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Transactions: {len(data.get('data', []))} trouvées")
            if data.get('data'):
                print(f"   Première transaction: {json.dumps(data['data'][0], indent=2)}")
            return True
        else:
            print(f"   ❌ Transactions: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = force_fix_transactions()
    if success:
        test_final_state()
        print("\n🎉 Correction terminée avec succès!")
    else:
        print("\n💥 Correction échouée!")
        print("\n💡 Le backend doit être redéployé avec la nouvelle structure")
