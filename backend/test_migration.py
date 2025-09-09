#!/usr/bin/env python3
"""
Script de test pour vérifier la migration vers SQLite
Usage: python test_migration.py
"""

import os
import json
from database import db_manager

def test_database_connection():
    """Tester la connexion à la base de données"""
    print("🔌 Test de connexion à la base de données...")
    
    if db_manager.connect():
        print("✅ Connexion réussie")
        db_manager.disconnect()
        return True
    else:
        print("❌ Échec de la connexion")
        return False

def test_tables_exist():
    """Vérifier que toutes les tables existent"""
    print("\n📋 Vérification des tables...")
    
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        # Liste des tables attendues
        expected_tables = [
            "buildings", "tenants", "assignments", 
            "building_reports", "unit_reports", "invoices"
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = []
        for table in expected_tables:
            if table in existing_tables:
                print(f"  ✅ Table '{table}' existe")
            else:
                print(f"  ❌ Table '{table}' manquante")
                missing_tables.append(table)
        
        db_manager.disconnect()
        
        if missing_tables:
            print(f"❌ {len(missing_tables)} tables manquantes")
            return False
        else:
            print("✅ Toutes les tables existent")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des tables : {e}")
        return False

def test_data_integrity():
    """Tester l'intégrité des données"""
    print("\n🔍 Test d'intégrité des données...")
    
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        # Test 1: Vérifier les contraintes de clés étrangères
        print("  Test des contraintes de clés étrangères...")
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        
        if fk_errors:
            print(f"  ❌ {len(fk_errors)} erreurs de clés étrangères trouvées")
            for error in fk_errors:
                print(f"    - {error}")
            return False
        else:
            print("  ✅ Aucune erreur de clés étrangères")
        
        # Test 2: Vérifier les données orphelines
        print("  Test des données orphelines...")
        
        # Assignations avec building_id inexistant
        cursor.execute("""
            SELECT COUNT(*) FROM assignments a 
            LEFT JOIN buildings b ON a.building_id = b.id 
            WHERE b.id IS NULL
        """)
        orphan_assignments = cursor.fetchone()[0]
        
        if orphan_assignments > 0:
            print(f"  ⚠️ {orphan_assignments} assignations avec building_id inexistant")
        else:
            print("  ✅ Aucune assignation orpheline")
        
        # Test 3: Vérifier les valeurs NULL dans les champs obligatoires
        print("  Test des champs obligatoires...")
        
        required_fields = [
            ("buildings", "name"),
            ("tenants", "name"),
            ("invoices", "invoice_number"),
            ("invoices", "category"),
            ("invoices", "amount")
        ]
        
        null_errors = []
        for table, field in required_fields:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {field} IS NULL OR {field} = ''")
            null_count = cursor.fetchone()[0]
            if null_count > 0:
                null_errors.append(f"{table}.{field}: {null_count} valeurs vides")
        
        if null_errors:
            print("  ⚠️ Champs obligatoires vides trouvés:")
            for error in null_errors:
                print(f"    - {error}")
        else:
            print("  ✅ Tous les champs obligatoires sont remplis")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'intégrité : {e}")
        return False

def test_performance():
    """Tester les performances de la base de données"""
    print("\n⚡ Test de performance...")
    
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        import time
        
        # Test 1: Temps de lecture des immeubles
        start_time = time.time()
        cursor.execute("SELECT * FROM buildings")
        buildings = cursor.fetchall()
        read_time = time.time() - start_time
        print(f"  Lecture de {len(buildings)} immeubles: {read_time:.3f}s")
        
        # Test 2: Temps de recherche par nom
        start_time = time.time()
        cursor.execute("SELECT * FROM buildings WHERE name LIKE ?", ("%test%",))
        search_results = cursor.fetchall()
        search_time = time.time() - start_time
        print(f"  Recherche par nom: {search_time:.3f}s ({len(search_results)} résultats)")
        
        # Test 3: Temps de jointure
        start_time = time.time()
        cursor.execute("""
            SELECT b.name, t.name, a.unit_id 
            FROM buildings b
            JOIN assignments a ON b.id = a.building_id
            JOIN tenants t ON a.tenant_id = t.id
            LIMIT 10
        """)
        join_results = cursor.fetchall()
        join_time = time.time() - start_time
        print(f"  Jointure complexe: {join_time:.3f}s ({len(join_results)} résultats)")
        
        db_manager.disconnect()
        
        # Évaluer les performances
        if read_time < 0.1 and search_time < 0.05 and join_time < 0.1:
            print("  ✅ Performances excellentes")
            return True
        elif read_time < 0.5 and search_time < 0.2 and join_time < 0.5:
            print("  ✅ Performances bonnes")
            return True
        else:
            print("  ⚠️ Performances à surveiller")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test de performance : {e}")
        return False

def test_backup_restore():
    """Tester la sauvegarde et restauration"""
    print("\n💾 Test de sauvegarde...")
    
    try:
        # Créer une sauvegarde
        backup_path = db_manager.backup_database()
        if backup_path and os.path.exists(backup_path):
            print(f"  ✅ Sauvegarde créée: {backup_path}")
            print(f"  📏 Taille: {os.path.getsize(backup_path)} bytes")
            return True
        else:
            print("  ❌ Échec de la sauvegarde")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de sauvegarde : {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST DE LA BASE DE DONNÉES SQLITE")
    print("=" * 50)
    
    tests = [
        ("Connexion", test_database_connection),
        ("Tables", test_tables_exist),
        ("Intégrité", test_data_integrity),
        ("Performance", test_performance),
        ("Sauvegarde", test_backup_restore)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Test: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: RÉUSSI")
        else:
            print(f"❌ {test_name}: ÉCHOUÉ")
    
    print(f"\n📊 RÉSULTATS: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ Votre base de données SQLite est prête à l'emploi")
        return True
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")
        return False

if __name__ == "__main__":
    main()
