#!/usr/bin/env python3
"""
Script pour corriger la structure de la table unit_reports
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_service import db_service
from sqlalchemy import text

def fix_unit_reports_table():
    """Corriger la structure de la table unit_reports"""
    print("🔧 CORRECTION DE LA TABLE UNIT_REPORTS")
    print("=" * 50)
    
    session = db_service.get_session()
    try:
        # 1. Vérifier la structure actuelle
        print("1️⃣ Vérification de la structure actuelle...")
        columns = session.execute(text("PRAGMA table_info(unit_reports)")).fetchall()
        column_names = [col[1] for col in columns]
        print(f"   📊 Colonnes actuelles: {column_names}")
        
        # 2. Créer une nouvelle table unit_reports avec la bonne structure
        print("2️⃣ Création de la nouvelle table unit_reports...")
        
        # Supprimer l'ancienne table
        session.execute(text("DROP TABLE IF EXISTS old_unit_reports"))
        session.execute(text("ALTER TABLE unit_reports RENAME TO old_unit_reports"))
        
        # Créer la nouvelle table
        session.execute(text("""
            CREATE TABLE unit_reports (
                id INTEGER PRIMARY KEY,
                unit_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                tenant_name VARCHAR(255),
                payment_method VARCHAR(100),
                is_heated_lit BOOLEAN DEFAULT FALSE,
                is_furnished BOOLEAN DEFAULT FALSE,
                wifi_included BOOLEAN DEFAULT FALSE,
                rent_amount DECIMAL(10, 2) DEFAULT 0.0,
                start_date DATE,
                end_date DATE,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE,
                UNIQUE (unit_id, year, month)
            )
        """))
        
        print("   ✅ Nouvelle table unit_reports créée")
        
        # 3. Migrer les données existantes
        print("3️⃣ Migration des données existantes...")
        
        # Récupérer les données de l'ancienne table
        old_reports = session.execute(text("SELECT * FROM old_unit_reports")).fetchall()
        print(f"   📊 {len(old_reports)} rapports à migrer")
        
        for report in old_reports:
            # Trouver l'unité correspondante
            unit_result = session.execute(text("""
                SELECT id FROM units 
                WHERE building_id = :building_id AND unit_number = :unit_number
            """), {
                "building_id": report[1],  # building_id dans l'ancienne structure
                "unit_number": report[2]   # unit_id était un string dans l'ancienne structure
            }).fetchone()
            
            if unit_result:
                unit_id = unit_result[0]
                
                # Insérer dans la nouvelle table
                session.execute(text("""
                    INSERT INTO unit_reports (id, unit_id, year, month, tenant_name, payment_method, is_heated_lit, is_furnished, wifi_included, rent_amount, start_date, end_date, notes, created_at, updated_at)
                    VALUES (:id, :unit_id, :year, :month, :tenant_name, :payment_method, :is_heated_lit, :is_furnished, :wifi_included, :rent_amount, :start_date, :end_date, :notes, :created_at, :updated_at)
                """), {
                    "id": report[0],  # id
                    "unit_id": unit_id,  # nouveau unit_id
                    "year": report[3],  # year
                    "month": report[4],  # month
                    "tenant_name": report[5],  # tenant_name
                    "payment_method": report[6],  # payment_method
                    "is_heated_lit": report[7],  # is_heated_lit
                    "is_furnished": report[8],  # is_furnished
                    "wifi_included": report[9],  # wifi_included
                    "rent_amount": report[10],  # rent_amount
                    "start_date": report[11],  # start_date
                    "end_date": report[12],  # end_date
                    "notes": report[13],  # notes
                    "created_at": report[14],  # created_at
                    "updated_at": report[15]  # updated_at
                })
        
        print("   ✅ Données migrées")
        
        # 4. Supprimer l'ancienne table
        print("4️⃣ Nettoyage...")
        session.execute(text("DROP TABLE old_unit_reports"))
        print("   ✅ Ancienne table supprimée")
        
        # 5. Vérifier la migration
        print("5️⃣ Vérification...")
        new_reports = session.execute(text("SELECT COUNT(*) FROM unit_reports")).fetchone()[0]
        print(f"   📊 {new_reports} rapports dans la nouvelle table")
        
        # 6. Commit
        session.commit()
        print("6️⃣ Changements sauvegardés...")
        print("   ✅ Migration terminée avec succès")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return False
    finally:
        session.close()

def main():
    """Fonction principale"""
    print("🚀 DÉMARRAGE DE LA CORRECTION")
    print("=" * 50)
    
    if fix_unit_reports_table():
        print("\n🎉 CORRECTION RÉUSSIE !")
        print("   La table unit_reports a été mise à jour avec la nouvelle structure.")
        return True
    else:
        print("\n💥 ÉCHEC DE LA CORRECTION !")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
