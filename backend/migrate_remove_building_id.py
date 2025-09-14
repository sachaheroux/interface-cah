#!/usr/bin/env python3
"""
Script pour supprimer la colonne building_id de la table assignments sur Render
"""

import os
import sqlite3
from database import DATABASE_PATH

def migrate_remove_building_id():
    """Supprimer la colonne building_id de la table assignments"""
    
    print(f"🔄 Migration: Suppression de building_id de la table assignments")
    print(f"📁 Base de données: {DATABASE_PATH}")
    
    if not os.path.exists(DATABASE_PATH):
        print("❌ Base de données n'existe pas")
        return False
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Vérifier si la colonne building_id existe
        cursor.execute("PRAGMA table_info(assignments)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'building_id' not in column_names:
            print("✅ La colonne building_id n'existe pas, migration non nécessaire")
            return True
        
        print("🔍 Colonne building_id trouvée, suppression en cours...")
        
        # 2. Créer une nouvelle table sans building_id
        cursor.execute("""
            CREATE TABLE assignments_new (
                id INTEGER PRIMARY KEY,
                tenant_id INTEGER NOT NULL,
                unit_id INTEGER NOT NULL,
                move_in_date DATE NOT NULL,
                move_out_date DATE,
                rent_amount DECIMAL(10,2),
                deposit_amount DECIMAL(10,2),
                lease_start_date DATE,
                lease_end_date DATE,
                rent_due_day INTEGER DEFAULT 1,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
                FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
            )
        """)
        
        # 3. Copier les données (sans building_id)
        cursor.execute("""
            INSERT INTO assignments_new (
                id, tenant_id, unit_id, move_in_date, move_out_date,
                rent_amount, deposit_amount, lease_start_date, lease_end_date,
                rent_due_day, notes, created_at, updated_at
            )
            SELECT 
                id, tenant_id, unit_id, move_in_date, move_out_date,
                rent_amount, deposit_amount, lease_start_date, lease_end_date,
                rent_due_day, notes, created_at, updated_at
            FROM assignments
        """)
        
        # 4. Supprimer l'ancienne table
        cursor.execute("DROP TABLE assignments")
        
        # 5. Renommer la nouvelle table
        cursor.execute("ALTER TABLE assignments_new RENAME TO assignments")
        
        # 6. Recréer les index
        cursor.execute("CREATE INDEX idx_assignments_tenant ON assignments(tenant_id)")
        cursor.execute("CREATE INDEX idx_assignments_unit ON assignments(unit_id)")
        
        # 7. Valider les changements
        conn.commit()
        
        print("✅ Migration terminée avec succès")
        print("✅ Colonne building_id supprimée de la table assignments")
        
        # Vérifier la nouvelle structure
        cursor.execute("PRAGMA table_info(assignments)")
        columns = cursor.fetchall()
        print("\n📋 Nouvelle structure de la table assignments:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - NOT NULL: {col[3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_remove_building_id()
    if success:
        print("\n🎉 Migration réussie !")
    else:
        print("\n💥 Migration échouée !")
