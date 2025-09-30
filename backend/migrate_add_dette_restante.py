#!/usr/bin/env python3
"""
Migration pour ajouter la colonne dette_restante à la table immeubles
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données
RENDER_DATABASE_URL = os.environ.get("DATABASE_URL")

if RENDER_DATABASE_URL:
    # Utiliser PostgreSQL sur Render
    engine = create_engine(RENDER_DATABASE_URL)
    print("🔗 Connexion à la base de données Render (PostgreSQL)")
else:
    # Utiliser SQLite local
    engine = create_engine("sqlite:///data/cah_database.db")
    print("🔗 Connexion à la base de données locale (SQLite)")

def migrate_add_dette_restante():
    """Ajouter la colonne dette_restante à la table immeubles"""
    try:
        with engine.connect() as conn:
            # Vérifier si la colonne existe déjà
            if RENDER_DATABASE_URL:
                # PostgreSQL
                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'immeubles' 
                    AND column_name = 'dette_restante'
                """)
            else:
                # SQLite
                check_query = text("""
                    PRAGMA table_info(immeubles)
                """)
            
            result = conn.execute(check_query)
            
            if RENDER_DATABASE_URL:
                # PostgreSQL
                column_exists = result.fetchone() is not None
            else:
                # SQLite
                columns = [row[1] for row in result.fetchall()]
                column_exists = 'dette_restante' in columns
            
            if column_exists:
                print("✅ La colonne 'dette_restante' existe déjà")
                return True
            
            # Ajouter la colonne
            if RENDER_DATABASE_URL:
                # PostgreSQL
                alter_query = text("""
                    ALTER TABLE immeubles 
                    ADD COLUMN dette_restante DECIMAL(12, 2) DEFAULT 0
                """)
            else:
                # SQLite
                alter_query = text("""
                    ALTER TABLE immeubles 
                    ADD COLUMN dette_restante DECIMAL(12, 2) DEFAULT 0
                """)
            
            conn.execute(alter_query)
            conn.commit()
            
            print("✅ Colonne 'dette_restante' ajoutée avec succès")
            
            # Vérifier que la colonne a été ajoutée
            if RENDER_DATABASE_URL:
                verify_query = text("""
                    SELECT column_name, data_type, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'immeubles' 
                    AND column_name = 'dette_restante'
                """)
            else:
                verify_query = text("""
                    PRAGMA table_info(immeubles)
                """)
            
            result = conn.execute(verify_query)
            if RENDER_DATABASE_URL:
                column_info = result.fetchone()
                if column_info:
                    print(f"✅ Vérification: {column_info[0]} ({column_info[1]}) - Default: {column_info[2]}")
            else:
                columns = result.fetchall()
                dette_column = next((col for col in columns if col[1] == 'dette_restante'), None)
                if dette_column:
                    print(f"✅ Vérification: {dette_column[1]} ({dette_column[2]}) - Default: {dette_column[4]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Début de la migration: Ajout de la colonne dette_restante")
    success = migrate_add_dette_restante()
    
    if success:
        print("🎉 Migration terminée avec succès!")
    else:
        print("💥 Migration échouée!")
        sys.exit(1)
