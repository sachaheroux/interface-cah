#!/usr/bin/env python3
"""
Script de vérification au démarrage de l'application
"""

import os
import sqlite3
from datetime import datetime

def check_database_on_startup():
    """Vérifier la base de données au démarrage"""
    
    print(f"🔍 Vérification de la base de données - {datetime.now()}")
    
    # Chemins
    data_dir = os.getenv('DATA_DIR', '/opt/render/project/src/data')
    db_path = os.path.join(data_dir, 'construction_projects.db')
    
    try:
        # Vérifier si la base existe
        if not os.path.exists(db_path):
            print("⚠️ Base de données construction n'existe pas")
            return False
        
        # Vérifier la structure
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier la table employes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employes'")
        if not cursor.fetchone():
            print("⚠️ Table employes n'existe pas")
            conn.close()
            return False
        
        # Compter les employés
        cursor.execute("SELECT COUNT(*) FROM employes")
        count = cursor.fetchone()[0]
        print(f"✅ Table employes: {count} enregistrement(s)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
        return False

if __name__ == "__main__":
    check_database_on_startup()
