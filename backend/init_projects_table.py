#!/usr/bin/env python3
"""
Script pour initialiser la table projets si elle n'existe pas
"""

import sys
import os
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_construction import init_construction_database, get_construction_db_context

def init_projects_table():
    """Initialiser la table projets"""
    print("=" * 60)
    print("INITIALISATION DE LA TABLE PROJETS")
    print("=" * 60)
    
    try:
        # Initialiser toutes les tables de construction
        print("\n1️⃣ Initialisation de toutes les tables de construction...")
        if init_construction_database():
            print("✅ Tables initialisées avec succès")
        else:
            print("❌ Erreur lors de l'initialisation")
            return False
        
        # Vérifier que la table projets existe maintenant
        print("\n2️⃣ Vérification de la table projets...")
        with get_construction_db_context() as db:
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='projets'"))
            table_exists = result.fetchone()
            
            if table_exists:
                print("✅ Table 'projets' existe")
                
                # Vérifier la structure
                result = db.execute(text("PRAGMA table_info(projets)"))
                columns = result.fetchall()
                print(f"📊 Colonnes trouvées: {len(columns)}")
                for col in columns:
                    print(f"   - {col[1]}: {col[2]}")
                
                # Compter les projets
                count_result = db.execute(text("SELECT COUNT(*) FROM projets"))
                count = count_result.fetchone()[0]
                print(f"\n📊 Nombre de projets: {count}")
                
                return True
            else:
                print("❌ Table 'projets' n'existe toujours pas")
                return False
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    init_projects_table()

