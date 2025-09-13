#!/usr/bin/env python3
"""
Script de migration pour Render - Ajouter toutes les colonnes manquantes à la table buildings
"""

import sqlite3
import os
from datetime import datetime

def migrate_render_database():
    """Migrer la base de données Render pour ajouter toutes les colonnes nécessaires"""
    
    # Chemin de la base de données sur Render
    db_path = os.getenv('DATABASE_URL', 'data/cah_database.db')
    
    # Si c'est une URL, extraire le chemin du fichier
    if db_path.startswith('sqlite:///'):
        db_path = db_path.replace('sqlite:///', '')
    
    print(f"🗄️ Base de données: {db_path}")
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 MIGRATION RENDER - TABLE BUILDINGS")
        print("=" * 50)
        
        # Vérifier la structure actuelle
        cursor.execute("PRAGMA table_info(buildings)")
        current_columns = [row[1] for row in cursor.fetchall()]
        print(f"📊 Colonnes actuelles: {current_columns}")
        
        # Colonnes à ajouter
        columns_to_add = [
            ("address_street", "TEXT"),
            ("address_city", "TEXT"),
            ("address_province", "TEXT"),
            ("address_postal_code", "TEXT"),
            ("address_country", "TEXT DEFAULT 'Canada'"),
            ("type", "TEXT NOT NULL DEFAULT 'residential'"),
            ("units", "INTEGER NOT NULL DEFAULT 0"),
            ("floors", "INTEGER NOT NULL DEFAULT 1"),
            ("year_built", "INTEGER"),
            ("total_area", "INTEGER"),
            ("characteristics", "TEXT"),
            # Colonnes financières séparées
            ("purchase_price", "REAL DEFAULT 0.0"),
            ("down_payment", "REAL DEFAULT 0.0"),
            ("interest_rate", "REAL DEFAULT 0.0"),
            ("current_value", "REAL DEFAULT 0.0"),
            # Colonnes de contacts séparées
            ("owner_name", "TEXT"),
            ("bank_name", "TEXT"),
            ("contractor_name", "TEXT"),
            ("notes", "TEXT DEFAULT ''"),
            ("is_default", "BOOLEAN DEFAULT FALSE")
        ]
        
        # Ajouter les colonnes manquantes
        for column_name, column_type in columns_to_add:
            if column_name not in current_columns:
                try:
                    alter_sql = f"ALTER TABLE buildings ADD COLUMN {column_name} {column_type}"
                    cursor.execute(alter_sql)
                    print(f"✅ Colonne ajoutée: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"⚠️  Colonne déjà présente: {column_name}")
                    else:
                        print(f"❌ Erreur pour {column_name}: {e}")
            else:
                print(f"ℹ️  Colonne déjà présente: {column_name}")
        
        # Vérifier la nouvelle structure
        cursor.execute("PRAGMA table_info(buildings)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"\n📊 Nouvelles colonnes: {new_columns}")
        
        # Sauvegarder les changements
        conn.commit()
        print("\n✅ Migration Render terminée avec succès!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration Render: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 MIGRATION RENDER - TABLE BUILDINGS")
    print("=" * 50)
    
    # Effectuer la migration
    success = migrate_render_database()
    
    if success:
        print(f"\n🎉 Migration Render réussie!")
    else:
        print(f"\n❌ Migration Render échouée!")
