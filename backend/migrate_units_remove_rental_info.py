#!/usr/bin/env python3
"""
Script de migration pour supprimer la colonne rental_info de la table units
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, init_database
from database_service import db_service
from sqlalchemy import text
import traceback

def migrate_units_remove_rental_info():
    """Supprimer la colonne rental_info de la table units"""
    print("🏗️ MIGRATION - SUPPRESSION COLONNE RENTAL_INFO")
    print("=" * 60)
    
    session = db_service.get_session()
    try:
        # 1. Vérifier si la colonne existe
        print("1️⃣ Vérification de l'existence de la colonne rental_info...")
        
        result = session.execute(text("PRAGMA table_info(units)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'rental_info' not in columns:
            print("   ✅ La colonne rental_info n'existe pas, migration non nécessaire")
            return True
        
        print(f"   📊 Colonnes actuelles: {columns}")
        print("   ✅ Colonne rental_info trouvée, migration nécessaire")
        
        # 2. Créer une nouvelle table sans rental_info
        print("2️⃣ Création de la nouvelle table units...")
        
        session.execute(text("""
            CREATE TABLE units_new (
                id INTEGER PRIMARY KEY,
                building_id INTEGER NOT NULL,
                unit_number TEXT NOT NULL,
                unit_address TEXT,
                type TEXT DEFAULT '4 1/2',
                area INTEGER DEFAULT 0,
                bedrooms INTEGER DEFAULT 1,
                bathrooms INTEGER DEFAULT 1,
                amenities TEXT,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE,
                UNIQUE(building_id, unit_number)
            )
        """))
        
        print("   ✅ Nouvelle table units créée")
        
        # 3. Copier les données (sans rental_info)
        print("3️⃣ Copie des données...")
        
        session.execute(text("""
            INSERT INTO units_new (
                id, building_id, unit_number, unit_address, type, area, 
                bedrooms, bathrooms, amenities, notes, created_at, updated_at
            )
            SELECT 
                id, building_id, unit_number, unit_address, type, area,
                bedrooms, bathrooms, amenities, notes, created_at, updated_at
            FROM units
        """))
        
        print("   ✅ Données copiées")
        
        # 4. Supprimer l'ancienne table et renommer
        print("4️⃣ Remplacement de l'ancienne table...")
        
        session.execute(text("DROP TABLE units"))
        session.execute(text("ALTER TABLE units_new RENAME TO units"))
        
        print("   ✅ Ancienne table supprimée et nouvelle table renommée")
        
        # 5. Vérifier le résultat
        print("5️⃣ Vérification du résultat...")
        
        result = session.execute(text("PRAGMA table_info(units)"))
        columns = [row[1] for row in result.fetchall()]
        
        print(f"   📊 Nouvelles colonnes: {columns}")
        
        if 'rental_info' in columns:
            print("   ❌ ERREUR: La colonne rental_info existe encore!")
            return False
        
        print("   ✅ Migration terminée avec succès!")
        
        session.commit()
        return True
        
    except Exception as e:
        print(f"❌ ERREUR lors de la migration: {e}")
        print(f"📊 Traceback: {traceback.format_exc()}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DE LA MIGRATION")
    print("=" * 60)
    
    if init_database():
        print("✅ Base de données initialisée")
        
        if migrate_units_remove_rental_info():
            print("🎉 MIGRATION TERMINÉE AVEC SUCCÈS!")
        else:
            print("💥 MIGRATION ÉCHOUÉE!")
    else:
        print("❌ Impossible d'initialiser la base de données")
