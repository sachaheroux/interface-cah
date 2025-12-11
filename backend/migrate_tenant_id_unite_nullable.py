#!/usr/bin/env python3
"""
Script pour modifier la colonne id_unite dans la table locataires
pour permettre les valeurs NULL (désélectionner une unité)
"""

import sqlite3
import os
from database import db_manager

def migrate_tenant_id_unite_nullable():
    """Modifier la colonne id_unite pour permettre NULL"""
    print("🔄 Migration: Permettre id_unite NULL dans la table locataires")
    print("=" * 60)
    
    db_path = db_manager.db_path
    print(f"📁 Base de données: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier la structure actuelle
        cursor.execute("PRAGMA table_info(locataires)")
        columns = cursor.fetchall()
        print("\n📋 Structure actuelle de la table locataires:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - nullable: {not col[3]}")
        
        # Vérifier si id_unite est déjà nullable
        id_unite_col = next((col for col in columns if col[1] == 'id_unite'), None)
        if id_unite_col and not id_unite_col[3]:  # Si NOT NULL
            print("\n🔧 Modification de la colonne id_unite pour permettre NULL...")
            
            # SQLite ne supporte pas directement ALTER COLUMN pour modifier nullable
            # Il faut recréer la table
            print("   ⚠️ SQLite nécessite de recréer la table...")
            
            # 1. Créer une table temporaire avec la nouvelle structure
            cursor.execute("""
                CREATE TABLE locataires_new (
                    id_locataire INTEGER PRIMARY KEY,
                    id_unite INTEGER REFERENCES unites(id_unite) ON DELETE CASCADE,
                    nom VARCHAR(255) NOT NULL,
                    prenom VARCHAR(255),
                    email VARCHAR(255),
                    telephone VARCHAR(50),
                    statut VARCHAR(50) DEFAULT 'actif',
                    notes TEXT DEFAULT '',
                    date_creation DATETIME,
                    date_modification DATETIME
                )
            """)
            
            # 2. Copier les données
            cursor.execute("""
                INSERT INTO locataires_new 
                SELECT * FROM locataires
            """)
            
            # 3. Supprimer l'ancienne table
            cursor.execute("DROP TABLE locataires")
            
            # 4. Renommer la nouvelle table
            cursor.execute("ALTER TABLE locataires_new RENAME TO locataires")
            
            # 5. Recréer les index
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_locataires_id_unite ON locataires(id_unite)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_locataires_nom ON locataires(nom)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_locataires_email ON locataires(email)")
            
            conn.commit()
            print("   ✅ Table recréée avec id_unite nullable")
        else:
            print("\n✅ La colonne id_unite est déjà nullable")
        
        # Vérifier la nouvelle structure
        cursor.execute("PRAGMA table_info(locataires)")
        columns = cursor.fetchall()
        print("\n📋 Nouvelle structure de la table locataires:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - nullable: {not col[3]}")
        
        conn.close()
        print("\n✅ Migration terminée avec succès!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    migrate_tenant_id_unite_nullable()


