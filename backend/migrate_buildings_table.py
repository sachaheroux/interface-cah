#!/usr/bin/env python3
"""
Script de migration pour ajouter toutes les colonnes manquantes à la table buildings
"""

import sqlite3
import os
from datetime import datetime

def migrate_buildings_table():
    """Migrer la table buildings pour ajouter toutes les colonnes nécessaires"""
    
    db_path = "data/cah_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 MIGRATION DE LA TABLE BUILDINGS")
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
            ("financials", "TEXT"),
            ("contacts", "TEXT"),
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
        print("\n✅ Migration terminée avec succès!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def backup_database():
    """Créer une sauvegarde de la base de données avant migration"""
    db_path = "data/cah_database.db"
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"data/cah_database_backup_{timestamp}.db"
        
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Sauvegarde créée: {backup_path}")
        return backup_path
    return None

if __name__ == "__main__":
    print("🚀 MIGRATION DE LA TABLE BUILDINGS")
    print("=" * 50)
    
    # Créer une sauvegarde
    backup_path = backup_database()
    
    # Effectuer la migration
    success = migrate_buildings_table()
    
    if success:
        print(f"\n🎉 Migration réussie!")
        if backup_path:
            print(f"💾 Sauvegarde disponible: {backup_path}")
    else:
        print(f"\n❌ Migration échouée!")
        if backup_path:
            print(f"💾 Vous pouvez restaurer depuis: {backup_path}")
