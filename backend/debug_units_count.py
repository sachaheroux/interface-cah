#!/usr/bin/env python3
"""
Script pour déboguer le nombre d'unités
"""

import requests
import sqlite3
from pathlib import Path

API_BASE_URL = "https://interface-cah-backend.onrender.com"
LOCAL_DB_PATH = Path("data/cah_database_local.db")

def check_api_units():
    """Vérifier les unités via l'API"""
    print("🔍 Vérification des unités via l'API...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/units")
        if response.status_code == 200:
            data = response.json()
            units = data.get('data', [])
            print(f"✅ API: {len(units)} unités")
            for unit in units:
                print(f"  - ID {unit['id_unite']}: {unit['adresse_unite']}")
            return units
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def check_local_units():
    """Vérifier les unités dans la base locale"""
    print("\n🔍 Vérification des unités dans la base locale...")
    if not LOCAL_DB_PATH.exists():
        print("❌ Base de données locale n'existe pas")
        return []
    
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM unites")
        count = cursor.fetchone()[0]
        print(f"✅ Base locale: {count} unités")
        
        cursor.execute("SELECT id_unite, adresse_unite FROM unites ORDER BY id_unite")
        units = cursor.fetchall()
        for unit in units:
            print(f"  - ID {unit[0]}: {unit[1]}")
        
        conn.close()
        return count
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 0

def main():
    print("🐛 Debug du nombre d'unités")
    print("=" * 40)
    
    api_units = check_api_units()
    local_count = check_local_units()
    
    print(f"\n📊 Résumé:")
    print(f"  - API: {len(api_units)} unités")
    print(f"  - Base locale: {local_count} unités")
    
    if len(api_units) != local_count:
        print("⚠️  Incohérence détectée!")
    else:
        print("✅ Cohérence OK")

if __name__ == "__main__":
    main()
