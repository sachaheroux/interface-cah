#!/usr/bin/env python3
"""
Vérifier le contenu des fichiers .db
"""

import sqlite3
import os

def check_db_content():
    # Lister les fichiers .db
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    print('📁 Fichiers .db trouvés:')
    for f in db_files:
        print(f'  - {f}')

    # Vérifier le contenu du fichier le plus récent
    if db_files:
        latest_db = max(db_files, key=os.path.getctime)
        print(f'\n🔍 Contenu de {latest_db}:')
        
        conn = sqlite3.connect(latest_db)
        cursor = conn.cursor()
        
        # Lister les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f'📊 Tables: {[t[0] for t in tables]}')
        
        # Compter les enregistrements
        for table in tables:
            table_name = table[0]
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            print(f'  - {table_name}: {count} enregistrements')
        
        # Afficher quelques unités
        if 'units' in [t[0] for t in tables]:
            print('\n🏠 Unités:')
            cursor.execute('SELECT id, unit_number, unit_address FROM units LIMIT 5')
            units = cursor.fetchall()
            for unit in units:
                print(f'  - ID: {unit[0]}, Numéro: {unit[1]}, Adresse: {unit[2]}')
        
        conn.close()
    else:
        print('❌ Aucun fichier .db trouvé')

if __name__ == "__main__":
    check_db_content()

