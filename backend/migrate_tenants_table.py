#!/usr/bin/env python3
"""
Script de migration pour ajouter les colonnes manquantes à la table tenants
"""

import requests
import json

def migrate_tenants_table():
    """Ajouter les colonnes manquantes à la table tenants via l'API"""
    print("🔧 Migration de la table tenants - Ajout des colonnes manquantes")
    
    API_URL = "https://interface-cah-backend.onrender.com"
    
    # Colonnes à ajouter
    columns_to_add = [
        "address_street TEXT",
        "address_city TEXT", 
        "address_province TEXT",
        "address_postal_code TEXT",
        "address_country TEXT DEFAULT 'Canada'"
    ]
    
    try:
        # Créer un endpoint de migration temporaire
        migration_data = {
            "action": "add_columns",
            "table": "tenants",
            "columns": columns_to_add
        }
        
        print("📋 Colonnes à ajouter:")
        for col in columns_to_add:
            print(f"  - {col}")
        
        # Note: Il faudrait créer un endpoint de migration sur le backend
        # Pour l'instant, on va utiliser une approche différente
        print("\n⚠️  Migration manuelle nécessaire")
        print("Il faut exécuter ces commandes SQL sur la base de données Render:")
        print()
        
        for col in columns_to_add:
            print(f"ALTER TABLE tenants ADD COLUMN {col};")
        
        print("\nOu utiliser DB Browser pour SQLite pour ajouter ces colonnes.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    migrate_tenants_table()
