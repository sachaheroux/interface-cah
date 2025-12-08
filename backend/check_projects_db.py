#!/usr/bin/env python3
"""
Script pour vérifier les projets dans la base de données
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_construction import get_construction_db_context, CONSTRUCTION_DATABASE_PATH

def check_projects():
    """Vérifier tous les projets dans la base de données"""
    print("=" * 60)
    print("VÉRIFICATION DES PROJETS DANS LA BASE DE DONNÉES")
    print("=" * 60)
    print(f"📁 Base de données: {CONSTRUCTION_DATABASE_PATH}")
    print()
    
    try:
        with get_construction_db_context() as db:
            # Vérifier la structure de la table
            print("1️⃣ STRUCTURE DE LA TABLE 'projets'")
            print("-" * 60)
            
            result = db.execute(text("PRAGMA table_info(projets)"))
            columns = result.fetchall()
            
            print(f"📊 Colonnes trouvées: {len(columns)}")
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                not_null = "NOT NULL" if col[3] else "NULL"
                default = f"DEFAULT {col[4]}" if col[4] else ""
                print(f"   - {col_name}: {col_type} {not_null} {default}")
            
            print()
            
            # Compter les projets
            print("2️⃣ NOMBRE DE PROJETS")
            print("-" * 60)
            
            count_result = db.execute(text("SELECT COUNT(*) FROM projets"))
            count = count_result.fetchone()[0]
            print(f"📊 Total de projets: {count}")
            print()
            
            # Récupérer tous les projets
            if count > 0:
                print("3️⃣ DONNÉES DES PROJETS")
                print("-" * 60)
                
                result = db.execute(text("SELECT * FROM projets ORDER BY date_creation DESC"))
                projects = result.fetchall()
                
                # Obtenir les noms de colonnes
                column_names = [col[1] for col in columns]
                
                for idx, project in enumerate(projects, 1):
                    print(f"\n📋 PROJET #{idx}")
                    print("-" * 40)
                    
                    # Créer un dictionnaire avec les données
                    project_dict = dict(zip(column_names, project))
                    
                    # Afficher toutes les colonnes, organisées par catégorie
                    base_fields = ['id_projet', 'nom', 'date_debut', 'date_fin_prevue', 'date_fin_reelle', 'notes', 'date_creation', 'date_modification']
                    new_fields = ['adresse', 'ville', 'province', 'code_postal', 'budget_total']
                    
                    # Informations de base
                    print("   📋 Informations de base:")
                    for col_name in base_fields:
                        if col_name in project_dict:
                            value = project_dict[col_name]
                            if value is not None:
                                if 'date' in col_name.lower():
                                    print(f"      • {col_name}: {value}")
                                else:
                                    print(f"      • {col_name}: {value}")
                            else:
                                print(f"      • {col_name}: (vide)")
                    
                    # Nouveaux champs (adresse et budget)
                    print("   📍 Adresse:")
                    for col_name in ['adresse', 'ville', 'province', 'code_postal']:
                        if col_name in project_dict:
                            value = project_dict[col_name]
                            if value is not None:
                                print(f"      • {col_name}: {value}")
                            else:
                                print(f"      • {col_name}: (vide)")
                    
                    # Budget
                    if 'budget_total' in project_dict:
                        budget = project_dict['budget_total']
                        if budget is not None:
                            print(f"   💰 Budget total: ${budget:,.2f}")
                        else:
                            print(f"   💰 Budget total: (vide)")
                    
                    # Autres champs (si présents)
                    other_fields = [col for col in project_dict.keys() if col not in base_fields + new_fields]
                    if other_fields:
                        print("   📝 Autres champs:")
                        for col_name in other_fields:
                            value = project_dict[col_name]
                            if value is not None:
                                if isinstance(value, float):
                                    if 'budget' in col_name.lower() or 'cout' in col_name.lower() or 'marge' in col_name.lower():
                                        print(f"      • {col_name}: ${value:,.2f}")
                                    else:
                                        print(f"      • {col_name}: {value}")
                                else:
                                    print(f"      • {col_name}: {value}")
                            else:
                                print(f"      • {col_name}: (vide)")
            else:
                print("⚠️ Aucun projet trouvé dans la base de données")
            
            print()
            print("=" * 60)
            print("✅ Vérification terminée")
            print("=" * 60)
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    check_projects()

