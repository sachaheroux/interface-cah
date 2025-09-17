#!/usr/bin/env python3
"""
Script pour analyser en détail les réponses de l'API Render
"""

import requests
import json

RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def debug_api_response(url, name):
    """Analyser en détail une réponse API"""
    print(f"\n🔍 DEBUG: {name}")
    print(f"URL: {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.content:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Content: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if isinstance(data, list):
                    print(f"List Length: {len(data)}")
                    if data:
                        print(f"First Item Type: {type(data[0])}")
                        print(f"First Item: {data[0]}")
                elif isinstance(data, dict):
                    print(f"Dict Keys: {list(data.keys())}")
                    for key, value in data.items():
                        print(f"  {key}: {type(value)} = {value}")
                
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print(f"Raw Content: {response.text}")
        else:
            print("Empty Response")
            
    except Exception as e:
        print(f"Exception: {e}")

def main():
    """Fonction principale"""
    print("🚀 DEBUG COMPLET DES RÉPONSES API RENDER")
    print("=" * 60)
    
    # Tester tous les endpoints
    endpoints = [
        (f"{RENDER_API_URL}/api/buildings", "Buildings"),
        (f"{RENDER_API_URL}/api/tenants", "Tenants"),
        (f"{RENDER_API_URL}/api/units", "Units"),
        (f"{RENDER_API_URL}/api/leases", "Leases"),
        (f"{RENDER_API_URL}/api/transactions-constants", "Transaction Constants"),
        (f"{RENDER_API_URL}/api/transactions", "Transactions"),
    ]
    
    for url, name in endpoints:
        debug_api_response(url, name)
    
    print("\n" + "=" * 60)
    print("📊 ANALYSE TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main()
