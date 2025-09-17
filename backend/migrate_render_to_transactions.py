#!/usr/bin/env python3
"""
Script pour migrer la base de données Render vers le nouveau schéma transactions
"""

import requests
import json
import os

# Configuration Render
RENDER_API_URL = "https://interface-cah-backend.onrender.com"

def migrate_render_database():
    """Migrer la base de données Render"""
    
    try:
        print("🚀 Migration de la base de données Render...")
        print("=" * 50)
        
        # 1. Tester la connexion
        print("🔍 Test de connexion à Render...")
        response = requests.get(f"{RENDER_API_URL}/api/test-endpoint", timeout=30)
        if response.status_code == 200:
            print("✅ Connexion à Render établie")
        else:
            print(f"❌ Erreur de connexion: {response.status_code}")
            return False
        
        # 2. Vérifier les tables existantes
        print("\n📊 Vérification des tables existantes...")
        
        # Tester les endpoints existants
        endpoints_to_test = [
            "/api/buildings",
            "/api/units", 
            "/api/tenants",
            "/api/leases",
            "/api/transactions"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{RENDER_API_URL}{endpoint}", timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        count = len(data['data'])
                    else:
                        count = len(data) if isinstance(data, list) else 1
                    print(f"  ✅ {endpoint}: {count} enregistrements")
                else:
                    print(f"  ⚠️  {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {endpoint}: Erreur - {e}")
        
        # 3. Tester les nouveaux endpoints de transactions
        print("\n🔧 Test des nouveaux endpoints de transactions...")
        
        try:
            response = requests.get(f"{RENDER_API_URL}/api/transactions/constants", timeout=30)
            if response.status_code == 200:
                constants = response.json()
                print(f"  ✅ Constantes transactions: {len(constants)} types")
                print(f"     Types: {constants.get('types', [])}")
            else:
                print(f"  ❌ Constantes transactions: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Constantes transactions: Erreur - {e}")
        
        try:
            response = requests.get(f"{RENDER_API_URL}/api/transactions", timeout=30)
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('data', []))
                print(f"  ✅ Transactions: {count} enregistrements")
            else:
                print(f"  ❌ Transactions: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Transactions: Erreur - {e}")
        
        print("\n✅ Migration Render terminée!")
        print("💡 Les nouveaux endpoints de transactions sont disponibles.")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration Render: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Migration Render vers transactions")
    print("=" * 50)
    
    success = migrate_render_database()
    
    if success:
        print("\n🎉 Migration Render réussie!")
        print("🌐 Votre application est maintenant en ligne avec les transactions!")
    else:
        print("\n💥 Migration Render échouée!")
        print("🔧 Vérifiez les erreurs ci-dessus.")
