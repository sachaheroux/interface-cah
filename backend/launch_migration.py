#!/usr/bin/env python3
"""
Script pour lancer la migration de la table transactions sur Render
"""

import requests
import time

# Configuration
RENDER_API_BASE = "https://interface-cah-backend.onrender.com"

def launch_migration():
    """Lancer la migration de la table transactions"""
    print("🔄 Lancement de la migration de la table transactions...")
    
    try:
        # Lancer la migration
        response = requests.post(f"{RENDER_API_BASE}/api/migrate/transactions")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Migration réussie: {data.get('message', '')}")
            return True
        else:
            print(f"❌ Erreur de migration: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_endpoints():
    """Tester les endpoints après migration"""
    print("\n🧪 Test des endpoints après migration...")
    
    # Test 1: Constantes
    print("\n1. Test des constantes...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/transactions-constants")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Types: {data.get('types', [])}")
            print(f"   ✅ Catégories: {data.get('categories', [])}")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Récupération des transactions
    print("\n2. Test de récupération des transactions...")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/transactions")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Transactions: {len(data.get('data', []))} trouvées")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Création d'une transaction de test
    print("\n3. Test de création d'une transaction...")
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
                    "reference": "TEST-MIGRATION-001",
                    "source": "Test Migration",
                    "pdf_transaction": "",
                    "notes": "Test après migration"
                }
                
                response = requests.post(f"{RENDER_API_BASE}/api/transactions", json=test_transaction)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Transaction créée avec succès!")
                    print(f"   Réponse: {response.json()}")
                else:
                    print(f"   ❌ Erreur: {response.text}")
            else:
                print("   ❌ Aucun immeuble trouvé")
        else:
            print(f"   ❌ Erreur lors de la récupération des immeubles: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    print("⏳ Attente de 10 secondes pour le déploiement...")
    time.sleep(10)
    
    success = launch_migration()
    if success:
        print("\n⏳ Attente de 5 secondes...")
        time.sleep(5)
        test_endpoints()
        print("\n🎉 Migration et tests terminés!")
    else:
        print("\n💥 Migration échouée!")
