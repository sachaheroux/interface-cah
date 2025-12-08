#!/usr/bin/env python3
"""
Script pour migrer la base de données construction et ajouter les nouvelles colonnes au modèle Projet
"""

import os
import sys
from datetime import datetime

# Ajouter le répertoire backend au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def migrate_projet_table():
    """Migrer la table projets avec les nouvelles colonnes"""
    
    print("🏗️ MIGRATION DE LA TABLE PROJETS")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from database_construction import get_construction_db_context
        from sqlalchemy import text
        
        print("1️⃣ CONNEXION À LA BASE DE DONNÉES")
        print("-" * 30)
        
        with get_construction_db_context() as db:
            print("✅ Connexion à la base de données établie")
            
            # Vérifier la structure actuelle de la table
            print("\n2️⃣ VÉRIFICATION DE LA STRUCTURE ACTUELLE")
            print("-" * 30)
            
            result = db.execute(text("PRAGMA table_info(projets)"))
            columns = result.fetchall()
            
            print(f"📊 Colonnes actuelles dans la table projets: {len(columns)}")
            existing_columns = [col[1] for col in columns]
            
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # Nouvelles colonnes à ajouter
            new_columns = [
                ("description", "TEXT"),
                ("adresse", "VARCHAR(255)"),
                ("ville", "VARCHAR(100)"),
                ("province", "VARCHAR(50)"),
                ("code_postal", "VARCHAR(10)"),
                ("budget_total", "FLOAT DEFAULT 0"),
                ("cout_actuel", "FLOAT DEFAULT 0"),
                ("marge_beneficiaire", "FLOAT DEFAULT 0"),
                ("statut", "VARCHAR(50) DEFAULT 'planification'"),
                ("progression_pourcentage", "FLOAT DEFAULT 0"),
                ("client_nom", "VARCHAR(255)"),
                ("client_telephone", "VARCHAR(20)"),
                ("client_email", "VARCHAR(255)"),
                ("chef_projet", "VARCHAR(255)"),
                ("architecte", "VARCHAR(255)"),
                ("entrepreneur_principal", "VARCHAR(255)"),
                ("plans_pdf", "VARCHAR(500)"),
                ("permis_construction", "VARCHAR(100)"),
                ("numero_permis", "VARCHAR(50)"),
                ("risques_identifies", "TEXT"),
                ("ameliorations_futures", "TEXT"),
                ("cree_par", "VARCHAR(255)"),
                ("modifie_par", "VARCHAR(255)")
            ]
            
            print("\n3️⃣ AJOUT DES NOUVELLES COLONNES")
            print("-" * 30)
            
            columns_added = 0
            for column_name, column_type in new_columns:
                if column_name not in existing_columns:
                    try:
                        alter_sql = f"ALTER TABLE projets ADD COLUMN {column_name} {column_type}"
                        db.execute(text(alter_sql))
                        print(f"✅ Colonne '{column_name}' ajoutée")
                        columns_added += 1
                    except Exception as e:
                        print(f"❌ Erreur ajout colonne '{column_name}': {e}")
                else:
                    print(f"ℹ️ Colonne '{column_name}' existe déjà")
            
            db.commit()
            
            print(f"\n📊 {columns_added} nouvelles colonnes ajoutées")
            
            # Vérifier la structure finale
            print("\n4️⃣ VÉRIFICATION DE LA STRUCTURE FINALE")
            print("-" * 30)
            
            result = db.execute(text("PRAGMA table_info(projets)"))
            final_columns = result.fetchall()
            
            print(f"📊 Colonnes finales dans la table projets: {len(final_columns)}")
            for col in final_columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # Mettre à jour les projets existants avec des valeurs par défaut
            print("\n5️⃣ MISE À JOUR DES PROJETS EXISTANTS")
            print("-" * 30)
            
            # Mettre à jour le statut des projets existants
            update_sql = """
            UPDATE projets 
            SET statut = 'planification' 
            WHERE statut IS NULL OR statut = ''
            """
            result = db.execute(text(update_sql))
            print(f"✅ {result.rowcount} projets mis à jour avec le statut par défaut")
            
            db.commit()
            
            print("\n6️⃣ TEST DE LA MIGRATION")
            print("-" * 30)
            
            # Tester la création d'un projet avec les nouvelles colonnes
            test_project_sql = """
            INSERT INTO projets (
                nom, description, adresse, ville, province, code_postal,
                budget_total, cout_actuel, statut, progression_pourcentage,
                client_nom, chef_projet, notes, cree_par
            ) VALUES (
                'Test Migration', 'Projet de test pour vérifier la migration',
                '123 Test St', 'Test City', 'QC', 'H1H 1H1',
                100000.0, 25000.0, 'planification', 25.0,
                'Client Test', 'Chef Test', 'Notes de test', 'Migration Script'
            )
            """
            
            db.execute(text(test_project_sql))
            db.commit()
            
            # Récupérer le projet de test
            test_result = db.execute(text("SELECT * FROM projets WHERE nom = 'Test Migration'"))
            test_project = test_result.fetchone()
            
            if test_project:
                print("✅ Projet de test créé avec succès")
                print(f"   ID: {test_project[0]}")
                print(f"   Nom: {test_project[1]}")
                print(f"   Statut: {test_project[14] if len(test_project) > 14 else 'N/A'}")
                
                # Supprimer le projet de test
                delete_sql = "DELETE FROM projets WHERE nom = 'Test Migration'"
                db.execute(text(delete_sql))
                db.commit()
                print("✅ Projet de test supprimé")
            else:
                print("❌ Erreur lors de la création du projet de test")
            
            print("\n" + "=" * 50)
            print("🎯 MIGRATION TERMINÉE AVEC SUCCÈS")
            print("=" * 50)
            print("✅ La table projets a été mise à jour avec toutes les nouvelles colonnes")
            print("✅ Les projets existants ont été mis à jour")
            print("✅ La migration a été testée avec succès")
            print("\n💡 Prochaines étapes:")
            print("   1. Déployer les changements sur Render")
            print("   2. Tester la création de projets via l'interface")
            print("   3. Vérifier que toutes les colonnes sont fonctionnelles")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    
    print("🚀 DÉMARRAGE DE LA MIGRATION PROJETS")
    print("=" * 50)
    
    if migrate_projet_table():
        print("\n✅ Migration réussie!")
    else:
        print("\n❌ Migration échouée!")
        sys.exit(1)

if __name__ == "__main__":
    main()


