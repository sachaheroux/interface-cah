#!/usr/bin/env python3
"""
Analyse complète de l'erreur 500 dans l'API d'analyse de rentabilité
"""

import requests
import json
from datetime import datetime

def debug_analysis_complete():
    """Diagnostic complet de l'API d'analyse"""
    
    print("🔍 ANALYSE COMPLÈTE DE L'ERREUR 500")
    print("=" * 60)
    
    base_url = "https://interface-cah-backend.onrender.com/api"
    
    try:
        # 1. Tester chaque endpoint individuellement
        print("\n1. TEST DES ENDPOINTS INDIVIDUELS:")
        
        # Test immeubles
        print("\n   📍 Test /buildings:")
        response = requests.get(f"{base_url}/buildings")
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            buildings = response.json()
            print(f"      Nombre d'immeubles: {len(buildings)}")
        else:
            print(f"      Erreur: {response.text}")
        
        # Test transactions
        print("\n   📍 Test /transactions:")
        response = requests.get(f"{base_url}/transactions")
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            transactions_data = response.json()
            transactions = transactions_data.get('data', transactions_data)
            print(f"      Nombre de transactions: {len(transactions)}")
        else:
            print(f"      Erreur: {response.text}")
        
        # Test baux
        print("\n   📍 Test /leases:")
        response = requests.get(f"{base_url}/leases")
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            leases_data = response.json()
            leases = leases_data.get('data', leases_data)
            print(f"      Nombre de baux: {len(leases)}")
        else:
            print(f"      Erreur: {response.text}")
        
        # 2. Tester l'API d'analyse avec différents paramètres
        print("\n2. TEST DE L'API D'ANALYSE AVEC DIFFÉRENTS PARAMÈTRES:")
        
        # Test 1: Paramètres minimaux
        print("\n   📍 Test avec paramètres minimaux:")
        response = requests.get(f"{base_url}/analysis/profitability?building_ids=1&start_year=2025&start_month=7&end_year=2025&end_month=7")
        print(f"      Status: {response.status_code}")
        if response.status_code != 200:
            print(f"      Erreur: {response.text}")
        
        # Test 2: Paramètres avec plusieurs immeubles
        print("\n   📍 Test avec plusieurs immeubles:")
        response = requests.get(f"{base_url}/analysis/profitability?building_ids=1,2&start_year=2025&start_month=7&end_year=2025&end_month=7")
        print(f"      Status: {response.status_code}")
        if response.status_code != 200:
            print(f"      Erreur: {response.text}")
        
        # Test 3: Paramètres avec période plus longue
        print("\n   📍 Test avec période plus longue:")
        response = requests.get(f"{base_url}/analysis/profitability?building_ids=1&start_year=2025&start_month=7&end_year=2025&end_month=12")
        print(f"      Status: {response.status_code}")
        if response.status_code != 200:
            print(f"      Erreur: {response.text}")
        
        # 3. Analyser les paramètres de l'URL
        print("\n3. ANALYSE DES PARAMÈTRES:")
        test_url = f"{base_url}/analysis/profitability?building_ids=1&start_year=2025&start_month=7&end_year=2026&end_month=6"
        print(f"   URL complète: {test_url}")
        
        # Décoder les paramètres
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(test_url)
        params = parse_qs(parsed.query)
        print(f"   Paramètres décodés: {params}")
        
        # 4. Tester avec curl pour voir les détails de l'erreur
        print("\n4. TEST AVEC REQUÊTE DÉTAILLÉE:")
        response = requests.get(test_url, timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"   Response Length: {len(response.text)}")
        
        if response.status_code != 200:
            print(f"   Erreur complète:")
            print(f"   {response.text}")
            
            # Essayer de parser le JSON d'erreur
            try:
                error_data = response.json()
                print(f"   Erreur JSON: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Erreur non-JSON: {response.text[:500]}...")
        
        # 5. Vérifier la santé du serveur
        print("\n5. VÉRIFICATION DE LA SANTÉ DU SERVEUR:")
        try:
            response = requests.get(f"{base_url.replace('/api', '')}/health", timeout=10)
            print(f"   Health check: {response.status_code}")
        except:
            print("   Health check: Non disponible")
        
        # 6. Tester d'autres endpoints pour voir si le problème est général
        print("\n6. TEST D'AUTRES ENDPOINTS:")
        endpoints_to_test = [
            "/buildings/1",
            "/transactions/1", 
            "/leases/1"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                print(f"   {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"   {endpoint}: Erreur - {e}")
                
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_analysis_complete()
