#!/usr/bin/env python3
"""
Vérifier le contenu de la base de données téléchargée de Render
"""

import sqlite3
import os

def check_downloaded_database():
    """Vérifier le contenu de la base de données téléchargée"""
    
    print("🔍 VÉRIFICATION DE LA BASE DE DONNÉES TÉLÉCHARGÉE")
    print("=" * 60)
    
    # Trouver le fichier de base le plus récent
    files = [f for f in os.listdir('.') if f.startswith('cah_database_cloud_') and f.endswith('.db')]
    
    if not files:
        print("❌ Aucun fichier de base de données cloud trouvé")
        return
    
    latest_file = max(files, key=os.path.getctime)
    print(f"📁 Fichier le plus récent: {latest_file}")
    
    try:
        conn = sqlite3.connect(latest_file)
        cursor = conn.cursor()
        
        # Vérifier les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Tables trouvées: {[t[0] for t in tables]}")
        
        # Vérifier le contenu de chaque table
        print("\n📋 CONTENU DES TABLES:")
        print("-" * 40)
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count} enregistrements")
            
            # Si la table n'est pas vide, afficher quelques exemples
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print(f"    Exemples:")
                for i, row in enumerate(rows):
                    print(f"      [{i+1}] {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

if __name__ == "__main__":
    check_downloaded_database()
