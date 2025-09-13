#!/usr/bin/env python3
"""
Script de migration Render pour supprimer la colonne rental_info de la table units
"""

import os
import sys
import requests
import json
from datetime import datetime

# Configuration Render
RENDER_API_URL = "https://interface-cah-backend.onrender.com"
RENDER_API_KEY = os.getenv("RENDER_API_KEY")

def migrate_render_units_remove_rental_info():
    """Supprimer la colonne rental_info de la table units sur Render"""
    print("🌐 MIGRATION RENDER - SUPPRESSION COLONNE RENTAL_INFO")
    print("=" * 60)
    
    if not RENDER_API_KEY:
        print("❌ RENDER_API_KEY non définie")
        return False
    
    try:
        # 1. Vérifier la connexion à l'API
        print("1️⃣ Vérification de la connexion à l'API Render...")
        
        response = requests.get(f"{RENDER_API_URL}/api/buildings", timeout=30)
        if response.status_code != 200:
            print(f"   ❌ Erreur API: {response.status_code}")
            return False
        
        print("   ✅ Connexion API établie")
        
        # 2. Exécuter la migration via l'API
        print("2️⃣ Exécution de la migration...")
        
        migration_data = {
            "action": "remove_rental_info_column",
            "table": "units"
        }
        
        response = requests.post(
            f"{RENDER_API_URL}/api/migrate",
            json=migration_data,
            headers={
                "Authorization": f"Bearer {RENDER_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            print("   ✅ Migration exécutée avec succès")
            return True
        else:
            print(f"   ❌ Erreur migration: {response.status_code}")
            print(f"   📊 Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR lors de la migration Render: {e}")
        return False

def create_migration_sql():
    """Créer le SQL de migration pour Render"""
    print("📝 CRÉATION DU SQL DE MIGRATION")
    print("=" * 60)
    
    sql_commands = [
        "-- Migration: Supprimer la colonne rental_info de la table units",
        "-- Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "-- 1. Créer une nouvelle table sans rental_info",
        "CREATE TABLE units_new (",
        "    id INTEGER PRIMARY KEY,",
        "    building_id INTEGER NOT NULL,",
        "    unit_number TEXT NOT NULL,",
        "    unit_address TEXT,",
        "    type TEXT DEFAULT '4 1/2',",
        "    area INTEGER DEFAULT 0,",
        "    bedrooms INTEGER DEFAULT 1,",
        "    bathrooms INTEGER DEFAULT 1,",
        "    amenities TEXT,",
        "    notes TEXT DEFAULT '',",
        "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,",
        "    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,",
        "    FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE,",
        "    UNIQUE(building_id, unit_number)",
        ");",
        "",
        "-- 2. Copier les données (sans rental_info)",
        "INSERT INTO units_new (",
        "    id, building_id, unit_number, unit_address, type, area,",
        "    bedrooms, bathrooms, amenities, notes, created_at, updated_at",
        ")",
        "SELECT",
        "    id, building_id, unit_number, unit_address, type, area,",
        "    bedrooms, bathrooms, amenities, notes, created_at, updated_at",
        "FROM units;",
        "",
        "-- 3. Supprimer l'ancienne table et renommer",
        "DROP TABLE units;",
        "ALTER TABLE units_new RENAME TO units;",
        "",
        "-- 4. Vérifier le résultat",
        "PRAGMA table_info(units);"
    ]
    
    sql_content = "\n".join(sql_commands)
    
    # Sauvegarder dans un fichier
    with open("migrate_units_remove_rental_info.sql", "w", encoding="utf-8") as f:
        f.write(sql_content)
    
    print("✅ SQL de migration créé: migrate_units_remove_rental_info.sql")
    print("\n📋 COMMANDES SQL À EXÉCUTER:")
    print("=" * 60)
    print(sql_content)
    
    return True

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DE LA MIGRATION RENDER")
    print("=" * 60)
    
    # Créer le SQL de migration
    if create_migration_sql():
        print("\n✅ SQL de migration créé")
    
    # Essayer la migration via API (si disponible)
    if migrate_render_units_remove_rental_info():
        print("🎉 MIGRATION RENDER TERMINÉE AVEC SUCCÈS!")
    else:
        print("⚠️  Migration via API échouée, utilisez le SQL manuellement")
        print("📋 Exécutez le fichier migrate_units_remove_rental_info.sql sur Render")
