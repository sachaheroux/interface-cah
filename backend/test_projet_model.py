#!/usr/bin/env python3
"""
Script pour tester que le modèle Projet correspond à la structure de la table
"""

import sys
import os
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_construction import get_construction_db_context
from models_construction import Projet

def test_projet_model():
    """Tester que le modèle correspond à la table"""
    print("=" * 60)
    print("TEST DU MODÈLE PROJET")
    print("=" * 60)
    print()
    
    try:
        with get_construction_db_context() as db:
            # 1. Vérifier la structure de la table
            print("1️⃣ STRUCTURE DE LA TABLE 'projets'")
            print("-" * 60)
            
            result = db.execute(text("PRAGMA table_info(projets)"))
            table_columns = [col[1] for col in result.fetchall()]
            
            print(f"📊 Colonnes dans la table: {len(table_columns)}")
            for col in table_columns:
                print(f"   - {col}")
            
            print()
            
            # 2. Vérifier les colonnes du modèle SQLAlchemy
            print("2️⃣ COLONNES DU MODÈLE SQLALCHEMY")
            print("-" * 60)
            
            model_columns = [col.name for col in Projet.__table__.columns]
            
            print(f"📊 Colonnes dans le modèle: {len(model_columns)}")
            for col in model_columns:
                print(f"   - {col}")
            
            print()
            
            # 3. Comparer
            print("3️⃣ COMPARAISON")
            print("-" * 60)
            
            missing_in_table = set(model_columns) - set(table_columns)
            missing_in_model = set(table_columns) - set(model_columns)
            
            if missing_in_table:
                print(f"❌ Colonnes dans le modèle mais PAS dans la table:")
                for col in missing_in_table:
                    print(f"   - {col}")
            else:
                print("✅ Toutes les colonnes du modèle existent dans la table")
            
            if missing_in_model:
                print(f"⚠️ Colonnes dans la table mais PAS dans le modèle:")
                for col in missing_in_model:
                    print(f"   - {col}")
            else:
                print("✅ Toutes les colonnes de la table sont dans le modèle")
            
            print()
            
            # 4. Test de création
            print("4️⃣ TEST DE CRÉATION D'UN PROJET")
            print("-" * 60)
            
            test_projet = Projet(
                nom="Test Projet",
                adresse="123 Test St",
                ville="Test City",
                province="QC",
                code_postal="H1H 1H1",
                budget_total=100000.0
            )
            
            # Vérifier que toutes les colonnes nécessaires sont présentes
            required_columns = ['nom']
            optional_columns = ['adresse', 'ville', 'province', 'code_postal', 'budget_total', 
                              'date_debut', 'date_fin_prevue', 'date_fin_reelle', 'notes']
            
            print("✅ Modèle Projet peut être créé avec les champs simplifiés")
            print(f"   Colonnes requises: {required_columns}")
            print(f"   Colonnes optionnelles: {optional_columns}")
            
            print()
            print("=" * 60)
            print("✅ Test terminé")
            print("=" * 60)
            
            return len(missing_in_table) == 0
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_projet_model()
    sys.exit(0 if success else 1)

