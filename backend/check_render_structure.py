#!/usr/bin/env python3
"""
Script pour vérifier la vraie structure des tables sur Render
"""

import requests
import json

# Configuration
RENDER_API_BASE = "https://interface-cah-backend.onrender.com"

def check_table_structure():
    """Vérifier la structure des tables sur Render"""
    print("🔍 Vérification de la structure des tables sur Render...")
    
    # Test 1: Récupérer un immeuble pour voir la vraie structure
    print("\n1. Structure de la table immeubles:")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/buildings")
        if response.status_code == 200:
            buildings = response.json()
            if buildings and len(buildings) > 0:
                building = buildings[0]
                print(f"   ✅ Premier immeuble récupéré:")
                print(f"   Colonnes disponibles: {list(building.keys())}")
                print(f"   Détail des valeurs:")
                for key, value in building.items():
                    print(f"     {key}: {value} (type: {type(value).__name__})")
            else:
                print("   ❌ Aucun immeuble trouvé")
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Récupérer une unité pour voir la vraie structure
    print("\n2. Structure de la table unites:")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/units")
        if response.status_code == 200:
            data = response.json()
            units = data.get('data', [])
            if units and len(units) > 0:
                unit = units[0]
                print(f"   ✅ Première unité récupérée:")
                print(f"   Colonnes disponibles: {list(unit.keys())}")
                print(f"   Détail des valeurs:")
                for key, value in unit.items():
                    print(f"     {key}: {value} (type: {type(value).__name__})")
            else:
                print("   ❌ Aucune unité trouvée")
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Récupérer un locataire pour voir la vraie structure
    print("\n3. Structure de la table locataires:")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/tenants")
        if response.status_code == 200:
            data = response.json()
            tenants = data.get('data', [])
            if tenants and len(tenants) > 0:
                tenant = tenants[0]
                print(f"   ✅ Premier locataire récupéré:")
                print(f"   Colonnes disponibles: {list(tenant.keys())}")
                print(f"   Détail des valeurs:")
                for key, value in tenant.items():
                    print(f"     {key}: {value} (type: {type(value).__name__})")
            else:
                print("   ❌ Aucun locataire trouvé")
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Récupérer un bail pour voir la vraie structure
    print("\n4. Structure de la table baux:")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/leases")
        if response.status_code == 200:
            data = response.json()
            leases = data.get('data', [])
            if leases and len(leases) > 0:
                lease = leases[0]
                print(f"   ✅ Premier bail récupéré:")
                print(f"   Colonnes disponibles: {list(lease.keys())}")
                print(f"   Détail des valeurs:")
                for key, value in lease.items():
                    print(f"     {key}: {value} (type: {type(value).__name__})")
            else:
                print("   ❌ Aucun bail trouvé")
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 5: Récupérer une transaction pour voir la vraie structure
    print("\n5. Structure de la table transactions:")
    try:
        response = requests.get(f"{RENDER_API_BASE}/api/transactions")
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', [])
            if transactions and len(transactions) > 0:
                transaction = transactions[0]
                print(f"   ✅ Première transaction récupérée:")
                print(f"   Colonnes disponibles: {list(transaction.keys())}")
                print(f"   Détail des valeurs:")
                for key, value in transaction.items():
                    print(f"     {key}: {value} (type: {type(value).__name__})")
            else:
                print("   ❌ Aucune transaction trouvée")
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    check_table_structure()
