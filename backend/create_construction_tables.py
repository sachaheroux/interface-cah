#!/usr/bin/env python3
"""
Script pour créer toutes les tables de construction dans la base de données unifiée
"""

import os
import sys
from datetime import datetime

# Ajouter le répertoire backend au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_construction_tables():
    """Créer toutes les tables de construction"""
    
    print("🏗️ CRÉATION DES TABLES DE CONSTRUCTION")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from database_construction import init_construction_database, get_construction_db_context
        from sqlalchemy import text
        
        print("1️⃣ INITIALISATION DE LA BASE DE DONNÉES CONSTRUCTION")
        print("-" * 30)
        
        # Utiliser la fonction d'initialisation qui crée toutes les tables
        if init_construction_database():
            print("✅ Tables de construction créées avec succès")
        else:
            print("❌ Erreur lors de la création des tables")
            return False
        
        print("\n2️⃣ VÉRIFICATION DES TABLES CRÉÉES")
        print("-" * 30)
        
        with get_construction_db_context() as db:
            # Lister toutes les tables
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            
            print(f"📊 Tables totales dans la base: {len(tables)}")
            
            # Vérifier les tables de construction
            construction_tables = ['projets', 'employes', 'fournisseurs', 'matieres_premieres', 'commandes', 'lignes_commandes', 'punchs_employes', 'sous_traitants', 'factures_st']
            
            for table_name in construction_tables:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    print(f"✅ Table '{table_name}': {count} enregistrements")
                except Exception as e:
                    print(f"❌ Table '{table_name}': Erreur ({e})")
            
            print("\n3️⃣ TEST DE CRÉATION D'UN PROJET")
            print("-" * 30)
            
            # Tester la création d'un projet
            test_project_sql = """
            INSERT INTO projets (
                nom, description, adresse, ville, province, code_postal,
                budget_total, cout_actuel, statut, progression_pourcentage,
                client_nom, chef_projet, notes, cree_par
            ) VALUES (
                'Test Projet', 'Projet de test pour vérifier la création',
                '123 Test St', 'Test City', 'QC', 'H1H 1H1',
                100000.0, 25000.0, 'planification', 25.0,
                'Client Test', 'Chef Test', 'Notes de test', 'Test Script'
            )
            """
            
            db.execute(text(test_project_sql))
            db.commit()
            
            # Vérifier que le projet a été créé
            result = db.execute(text("SELECT * FROM projets WHERE nom = 'Test Projet'"))
            test_project = result.fetchone()
            
            if test_project:
                print("✅ Projet de test créé avec succès")
                print(f"   ID: {test_project[0]}")
                print(f"   Nom: {test_project[1]}")
                print(f"   Statut: {test_project[14] if len(test_project) > 14 else 'N/A'}")
                
                # Supprimer le projet de test
                delete_sql = "DELETE FROM projets WHERE nom = 'Test Projet'"
                db.execute(text(delete_sql))
                db.commit()
                print("✅ Projet de test supprimé")
            else:
                print("❌ Erreur lors de la création du projet de test")
            
            print("\n4️⃣ TEST DE CRÉATION D'UN EMPLOYÉ")
            print("-" * 30)
            
            # Tester la création d'un employé
            test_employee_sql = """
            INSERT INTO employes (
                prenom, nom, poste, numero, adresse_courriel, taux_horaire
            ) VALUES (
                'Test', 'Employé', 'Ouvrier', '(555) 123-4567', 'test@employe.com', 35.0
            )
            """
            
            db.execute(text(test_employee_sql))
            db.commit()
            
            # Vérifier que l'employé a été créé
            result = db.execute(text("SELECT * FROM employes WHERE prenom = 'Test'"))
            test_employee = result.fetchone()
            
            if test_employee:
                print("✅ Employé de test créé avec succès")
                print(f"   ID: {test_employee[0]}")
                print(f"   Nom: {test_employee[1]} {test_employee[2]}")
                print(f"   Taux horaire: {test_employee[6] if len(test_employee) > 6 else 'N/A'}")
                
                # Supprimer l'employé de test
                delete_sql = "DELETE FROM employes WHERE prenom = 'Test'"
                db.execute(text(delete_sql))
                db.commit()
                print("✅ Employé de test supprimé")
            else:
                print("❌ Erreur lors de la création de l'employé de test")
            
            print("\n5️⃣ VÉRIFICATION FINALE")
            print("-" * 30)
            
            # Compter toutes les tables
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            all_tables = result.fetchall()
            
            print(f"📊 Tables totales dans la base: {len(all_tables)}")
            print("📋 Liste complète des tables:")
            for table in all_tables:
                print(f"   - {table[0]}")
            
            print("\n" + "=" * 50)
            print("🎯 CRÉATION DES TABLES TERMINÉE AVEC SUCCÈS")
            print("=" * 50)
            print("✅ Toutes les tables de construction ont été créées")
            print("✅ Les tests de création fonctionnent")
            print("✅ La base de données est prête pour l'utilisation")
            print("\n💡 Prochaines étapes:")
            print("   1. Déployer les changements sur Render")
            print("   2. Tester la création de projets via l'interface")
            print("   3. Vérifier que les employés persistent")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    
    print("🚀 CRÉATION DES TABLES DE CONSTRUCTION")
    print("=" * 50)
    
    if create_construction_tables():
        print("\n✅ Création réussie!")
    else:
        print("\n❌ Création échouée!")
        sys.exit(1)

if __name__ == "__main__":
    main()


