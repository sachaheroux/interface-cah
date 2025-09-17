#!/usr/bin/env python3
"""
Créer les tables françaises localement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
from models_francais import Base

def create_local_tables():
    """Créer toutes les tables françaises localement"""
    
    print("🏗️ Création des tables françaises localement")
    print("=" * 50)
    
    try:
        # Créer toutes les tables
        Base.metadata.create_all(bind=db_manager.engine)
        print("✅ Toutes les tables françaises ont été créées avec succès!")
        
        # Lister les tables créées
        from sqlalchemy import inspect
        inspector = inspect(db_manager.engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 Tables disponibles: {tables}")
        
        # Vérifier les colonnes de la table baux
        if 'baux' in tables:
            columns = inspector.get_columns('baux')
            print(f"\n🏠 Colonnes de la table 'baux':")
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_local_tables()
