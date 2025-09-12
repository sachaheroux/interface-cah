#!/usr/bin/env python3
"""
Script pour explorer le contenu de la base de données SQLite
"""

import sqlite3
import json
from datetime import datetime

def explore_database():
    """Explorer le contenu de la base de données"""
    print("🔍 EXPLORATION DE LA BASE DE DONNÉES SQLite")
    print("=" * 60)
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect('data/cah_database.db')
        cursor = conn.cursor()
        
        # 1. Lister toutes les tables
        print("📋 TABLES DISPONIBLES:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n" + "=" * 60)
        
        # 2. Explorer chaque table
        for table in tables:
            table_name = table[0]
            print(f"\n📊 TABLE: {table_name.upper()}")
            print("-" * 40)
            
            # Compter les enregistrements
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   Nombre d'enregistrements: {count}")
            
            if count > 0:
                # Afficher la structure
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print("   Structure:")
                for col in columns:
                    print(f"     - {col[1]} ({col[2]})")
                
                # Afficher les premiers enregistrements
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                records = cursor.fetchall()
                print("   Premiers enregistrements:")
                for i, record in enumerate(records, 1):
                    print(f"     {i}. {record}")
                
                if count > 5:
                    print(f"     ... et {count - 5} autres")
            else:
                print("   (Table vide)")
        
        print("\n" + "=" * 60)
        
        # 3. Statistiques globales
        print("\n📈 STATISTIQUES GLOBALES:")
        total_records = 0
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"   {table_name}: {count} enregistrements")
        
        print(f"\n   TOTAL: {total_records} enregistrements")
        
        # 4. Taille de la base de données
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        size_bytes = cursor.fetchone()[0]
        size_mb = size_bytes / (1024 * 1024)
        print(f"   Taille: {size_mb:.2f} MB")
        
        conn.close()
        print("\n✅ Exploration terminée !")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exploration: {e}")

def show_specific_table(table_name):
    """Afficher le contenu d'une table spécifique"""
    print(f"\n🔍 CONTENU DE LA TABLE: {table_name.upper()}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('data/cah_database.db')
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f"❌ La table '{table_name}' n'existe pas")
            return
        
        # Compter les enregistrements
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Nombre d'enregistrements: {count}")
        
        if count > 0:
            # Afficher tous les enregistrements
            cursor.execute(f"SELECT * FROM {table_name}")
            records = cursor.fetchall()
            
            # Afficher les colonnes
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"Colonnes: {', '.join(column_names)}")
            print("-" * 60)
            
            # Afficher les données
            for i, record in enumerate(records, 1):
                print(f"{i}. {dict(zip(column_names, record))}")
        else:
            print("(Table vide)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Afficher une table spécifique
        table_name = sys.argv[1]
        show_specific_table(table_name)
    else:
        # Exploration complète
        explore_database()
        
        print("\n💡 UTILISATION:")
        print("   python explore_database.py                    # Exploration complète")
        print("   python explore_database.py buildings          # Voir la table buildings")
        print("   python explore_database.py tenants            # Voir la table tenants")
        print("   python explore_database.py assignments        # Voir la table assignments")
        print("   python explore_database.py employees          # Voir la table employees")
        print("   python explore_database.py projects           # Voir la table projects")
