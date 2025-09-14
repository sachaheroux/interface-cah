#!/usr/bin/env python3
"""
Script pour vérifier la structure de la table assignments
"""

import os
import sqlite3
from database import DATABASE_PATH

def check_assignments_table():
    """Vérifier la structure de la table assignments"""
    
    print(f"🔍 Vérification de la table assignments dans: {DATABASE_PATH}")
    
    if not os.path.exists(DATABASE_PATH):
        print("❌ Base de données n'existe pas")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Vérifier la structure de la table
        cursor.execute("PRAGMA table_info(assignments)")
        columns = cursor.fetchall()
        
        print("\n📋 Structure de la table assignments:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - NOT NULL: {col[3]} - Default: {col[4]}")
        
        # Vérifier les contraintes
        cursor.execute("PRAGMA foreign_key_list(assignments)")
        fks = cursor.fetchall()
        
        print("\n🔗 Clés étrangères:")
        for fk in fks:
            print(f"   - {fk[3]} -> {fk[2]}.{fk[4]}")
        
        # Vérifier les index
        cursor.execute("PRAGMA index_list(assignments)")
        indexes = cursor.fetchall()
        
        print("\n📊 Index:")
        for idx in indexes:
            print(f"   - {idx[1]} (unique: {idx[2]})")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_assignments_table()
