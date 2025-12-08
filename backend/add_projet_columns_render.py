#!/usr/bin/env python3
"""
Script pour ajouter les colonnes manquantes à la table projets sur Render
"""

import requests
import json

# Configuration
RENDER_URL = "https://interface-cah-backend.onrender.com"

def add_columns_to_render():
    """Ajouter les colonnes manquantes via l'API"""
    print("=" * 60)
    print("AJOUT DES COLONNES À LA TABLE PROJETS SUR RENDER")
    print("=" * 60)
    print(f"🌐 URL Render: {RENDER_URL}")
    print()
    
    # Colonnes à ajouter (celles qui n'existent pas encore)
    columns_to_add = [
        ("adresse", "VARCHAR(255)"),
        ("ville", "VARCHAR(100)"),
        ("province", "VARCHAR(50)"),
        ("code_postal", "VARCHAR(10)"),
        ("budget_total", "FLOAT DEFAULT 0")
    ]
    
    print("📋 Colonnes à ajouter:")
    for col_name, col_type in columns_to_add:
        print(f"   - {col_name}: {col_type}")
    print()
    
    try:
        # Appeler l'endpoint de migration
        print("1️⃣ Appel de l'endpoint de migration...")
        response = requests.post(
            f"{RENDER_URL}/api/construction/migrate/add-projet-columns",
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Migration réussie!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_columns_to_render()

