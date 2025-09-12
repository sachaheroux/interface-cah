#!/usr/bin/env python3
"""
Script simple pour créer la table units
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, init_database
from database_service import db_service
from sqlalchemy import text
import traceback

def create_units_table():
    """Créer la table units"""
    print("🏗️ CRÉATION DE LA TABLE UNITS")
    print("=" * 50)
    
    session = db_service.get_session()
    try:
        # 1. Vérifier si la table existe déjà
        print("1️⃣ Vérification de l'existence de la table...")
        
        result = session.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='units'
        """)).fetchone()
        
        if result:
            print("   ✅ Table units existe déjà")
            return True
        
        # 2. Créer la table units
        print("2️⃣ Création de la table units...")
        
        session.execute(text("""
            CREATE TABLE units (
                id INTEGER PRIMARY KEY,
                building_id INTEGER NOT NULL,
                unit_number VARCHAR(50) NOT NULL,
                unit_address VARCHAR(255),
                type VARCHAR(50) DEFAULT '1 1/2',
                area INTEGER DEFAULT 0,
                bedrooms INTEGER DEFAULT 1,
                bathrooms INTEGER DEFAULT 1,
                amenities TEXT,
                rental_info TEXT,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE,
                UNIQUE (building_id, unit_number)
            )
        """))
        
        print("   ✅ Table units créée")
        
        # 3. Créer les index
        print("3️⃣ Création des index...")
        
        session.execute(text("CREATE INDEX idx_units_building_id ON units(building_id)"))
        session.execute(text("CREATE INDEX idx_units_unit_number ON units(unit_number)"))
        
        print("   ✅ Index créés")
        
        # 4. Commit
        session.commit()
        print("4️⃣ Changements sauvegardés...")
        print("   ✅ Table units prête à être utilisée")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        traceback.print_exc()
        session.rollback()
        return False
    finally:
        session.close()

def main():
    """Fonction principale"""
    print("🚀 DÉMARRAGE DE LA CRÉATION")
    print("=" * 50)
    
    if create_units_table():
        print("\n🎉 CRÉATION RÉUSSIE !")
        print("   La table units est maintenant disponible.")
        return True
    else:
        print("\n💥 ÉCHEC DE LA CRÉATION !")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
