#!/usr/bin/env python3
"""
Script de diagnostic complet pour identifier et corriger les problèmes sur Render
"""

import requests
import time
import sys

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def test_endpoint(url, method="GET", data=None, expected_status=200):
    """Tester un endpoint et retourner le résultat"""
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"  {method} {url}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"  ✅ OK")
            return True, response.json() if response.content else {}
        else:
            print(f"  ❌ ERREUR")
            print(f"  Response: {response.text[:200]}...")
            return False, {}
            
    except Exception as e:
        print(f"  ❌ EXCEPTION: {e}")
        return False, {}

def diagnose_assignments_issue():
    """Diagnostiquer le problème des assignments"""
    print("\n🔍 DIAGNOSTIC: Assignments")
    print("-" * 40)
    
    # Vérifier si l'endpoint assignments existe
    success, data = test_endpoint(f"{RENDER_API_URL}/api/assignments", expected_status=404)
    
    if not success:
        print("❌ L'endpoint /api/assignments n'existe plus (c'est normal)")
        print("💡 Solution: Le frontend doit utiliser /api/tenants au lieu de /api/assignments")
        return False
    
    return True

def diagnose_transactions_constants():
    """Diagnostiquer le problème des constantes de transactions"""
    print("\n🔍 DIAGNOSTIC: Constantes de transactions")
    print("-" * 40)
    
    success, data = test_endpoint(f"{RENDER_API_URL}/api/transactions/constants")
    
    if success:
        print("✅ Constantes récupérées avec succès")
        print(f"   Données: {data}")
        return True
    else:
        print("❌ Problème avec les constantes de transactions")
        return False

def diagnose_transactions_list():
    """Diagnostiquer le problème de la liste des transactions"""
    print("\n🔍 DIAGNOSTIC: Liste des transactions")
    print("-" * 40)
    
    success, data = test_endpoint(f"{RENDER_API_URL}/api/transactions")
    
    if success:
        transactions = data.get('data', [])
        print(f"✅ Liste des transactions récupérée ({len(transactions)} transactions)")
        return True
    else:
        print("❌ Problème avec la liste des transactions")
        return False

def diagnose_database_structure():
    """Diagnostiquer la structure de la base de données"""
    print("\n🔍 DIAGNOSTIC: Structure de la base de données")
    print("-" * 40)
    
    # Tester la création d'une transaction pour voir si la table existe
    print("  Test de création d'une transaction...")
    
    # D'abord, récupérer un immeuble
    buildings_success, buildings_data = test_endpoint(f"{RENDER_API_URL}/api/buildings")
    if not buildings_success:
        print("❌ Impossible de récupérer les immeubles")
        return False
    
    buildings = buildings_data.get('data', [])
    if not buildings:
        print("❌ Aucun immeuble trouvé")
        return False
    
    building_id = buildings[0]['id_immeuble']
    print(f"  Utilisation de l'immeuble ID: {building_id}")
    
    # Créer une transaction de test
    test_transaction = {
        "id_immeuble": building_id,
        "categorie": "revenu",
        "montant": 0.01,
        "date_de_transaction": "2025-01-17",
        "methode_de_paiement": "test",
        "reference": "TEST-DIAGNOSTIC",
        "source": "Diagnostic automatique",
        "pdf_transaction": "",
        "notes": "Transaction de test pour diagnostic"
    }
    
    success, data = test_endpoint(f"{RENDER_API_URL}/api/transactions", "POST", test_transaction, 201)
    
    if success:
        transaction_id = data.get('data', {}).get('id_transaction')
        print(f"✅ Transaction créée avec succès (ID: {transaction_id})")
        
        # Supprimer la transaction de test
        if transaction_id:
            delete_success, _ = test_endpoint(f"{RENDER_API_URL}/api/transactions/{transaction_id}", "DELETE", expected_status=200)
            if delete_success:
                print("✅ Transaction de test supprimée")
        
        return True
    else:
        print("❌ Impossible de créer une transaction")
        return False

def fix_frontend_assignments():
    """Proposer des corrections pour le frontend"""
    print("\n🔧 CORRECTIONS FRONTEND")
    print("-" * 40)
    
    print("❌ Problème identifié: Le frontend utilise encore /api/assignments")
    print("💡 Solutions nécessaires:")
    print("   1. Remplacer getAssignments() par getTenants() dans api.js")
    print("   2. Mettre à jour Buildings.jsx pour utiliser les locataires")
    print("   3. Supprimer les références aux assignments dans le frontend")
    
    return False

def main():
    """Fonction principale"""
    print("🚀 DIAGNOSTIC COMPLET DU BACKEND RENDER")
    print("=" * 50)
    
    # Attendre un peu pour que le déploiement se stabilise
    print("⏳ Attente de la stabilisation du déploiement...")
    time.sleep(10)
    
    # Tests de diagnostic
    results = []
    
    results.append(("Assignments", diagnose_assignments_issue()))
    results.append(("Constantes transactions", diagnose_transactions_constants()))
    results.append(("Liste transactions", diagnose_transactions_list()))
    results.append(("Structure base de données", diagnose_database_structure()))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ RÉSOLU" if success else "❌ PROBLÈME"
        print(f"{status} - {test_name}")
        if not success:
            all_passed = False
    
    # Corrections frontend
    print("\n🔧 CORRECTIONS NÉCESSAIRES")
    print("-" * 30)
    
    if not all_passed:
        print("❌ Des problèmes ont été identifiés")
        fix_frontend_assignments()
    else:
        print("✅ Tous les tests backend sont passés")
        print("💡 Le problème vient probablement du frontend")
        fix_frontend_assignments()
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
