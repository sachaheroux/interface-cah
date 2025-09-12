#!/usr/bin/env python3
"""
Script pour corriger la structure de la table assignments
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_service import db_service
from sqlalchemy import text

def fix_assignments_table():
    """Corriger la structure de la table assignments"""
    print("🔧 CORRECTION DE LA TABLE ASSIGNMENTS")
    print("=" * 50)
    
    session = db_service.get_session()
    try:
        # 1. Vérifier la structure actuelle
        print("1️⃣ Vérification de la structure actuelle...")
        columns = session.execute(text("PRAGMA table_info(assignments)")).fetchall()
        column_names = [col[1] for col in columns]
        print(f"   📊 Colonnes actuelles: {column_names}")
        
        # 2. Créer une nouvelle table assignments avec la bonne structure
        print("2️⃣ Création de la nouvelle table assignments...")
        
        # Supprimer l'ancienne table
        session.execute(text("DROP TABLE IF EXISTS old_assignments"))
        session.execute(text("ALTER TABLE assignments RENAME TO old_assignments"))
        
        # Créer la nouvelle table
        session.execute(text("""
            CREATE TABLE assignments (
                id INTEGER PRIMARY KEY,
                tenant_id INTEGER NOT NULL,
                unit_id INTEGER NOT NULL,
                move_in_date DATE NOT NULL,
                move_out_date DATE,
                rent_amount DECIMAL(10, 2),
                deposit_amount DECIMAL(10, 2),
                lease_start_date DATE,
                lease_end_date DATE,
                rent_due_day INTEGER DEFAULT 1,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
                FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
            )
        """))
        
        print("   ✅ Nouvelle table assignments créée")
        
        # 3. Migrer les données existantes
        print("3️⃣ Migration des données existantes...")
        
        # Récupérer les données de l'ancienne table
        old_assignments = session.execute(text("SELECT * FROM old_assignments")).fetchall()
        print(f"   📊 {len(old_assignments)} assignations à migrer")
        
        for assignment in old_assignments:
            # Trouver l'unité correspondante
            unit_result = session.execute(text("""
                SELECT id FROM units 
                WHERE building_id = :building_id AND unit_number = :unit_number
            """), {
                "building_id": assignment[2],  # building_id dans l'ancienne structure
                "unit_number": assignment[3]   # unit_number dans l'ancienne structure
            }).fetchone()
            
            if unit_result:
                unit_id = unit_result[0]
                
                # Insérer dans la nouvelle table
                session.execute(text("""
                    INSERT INTO assignments (id, tenant_id, unit_id, move_in_date, move_out_date, rent_amount, deposit_amount, lease_start_date, lease_end_date, rent_due_day, notes, created_at, updated_at)
                    VALUES (:id, :tenant_id, :unit_id, :move_in_date, :move_out_date, :rent_amount, :deposit_amount, :lease_start_date, :lease_end_date, :rent_due_day, :notes, :created_at, :updated_at)
                """), {
                    "id": assignment[0],  # id
                    "tenant_id": assignment[1],  # tenant_id
                    "unit_id": unit_id,  # nouveau unit_id
                    "move_in_date": assignment[4],  # move_in_date
                    "move_out_date": assignment[5],  # move_out_date
                    "rent_amount": assignment[6],  # rent_amount
                    "deposit_amount": assignment[7],  # deposit_amount
                    "lease_start_date": assignment[8],  # lease_start_date
                    "lease_end_date": assignment[9],  # lease_end_date
                    "rent_due_day": assignment[10],  # rent_due_day
                    "notes": assignment[11],  # notes
                    "created_at": assignment[12],  # created_at
                    "updated_at": assignment[13]  # updated_at
                })
        
        print("   ✅ Données migrées")
        
        # 4. Supprimer l'ancienne table
        print("4️⃣ Nettoyage...")
        session.execute(text("DROP TABLE old_assignments"))
        print("   ✅ Ancienne table supprimée")
        
        # 5. Vérifier la migration
        print("5️⃣ Vérification...")
        new_assignments = session.execute(text("SELECT COUNT(*) FROM assignments")).fetchone()[0]
        print(f"   📊 {new_assignments} assignations dans la nouvelle table")
        
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
    
    if fix_assignments_table():
        print("\n🎉 CORRECTION RÉUSSIE !")
        print("   La table assignments a été mise à jour avec la nouvelle structure.")
        return True
    else:
        print("\n💥 ÉCHEC DE LA CORRECTION !")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
