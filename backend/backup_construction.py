#!/usr/bin/env python3
"""
Script de sauvegarde automatique des données construction
"""

import os
import shutil
import sqlite3
from datetime import datetime

def backup_construction_database():
    """Sauvegarder la base de données construction"""
    
    # Chemins
    data_dir = os.getenv('DATA_DIR', '/opt/render/project/src/data')
    db_path = os.path.join(data_dir, 'construction_projects.db')
    backup_dir = os.path.join(data_dir, 'backups')
    
    # Créer le dossier de sauvegarde
    os.makedirs(backup_dir, exist_ok=True)
    
    # Nom du fichier de sauvegarde
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'construction_backup_{timestamp}.db')
    
    try:
        # Copier la base de données
        shutil.copy2(db_path, backup_path)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Garder seulement les 5 dernières sauvegardes
        backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('construction_backup_')])
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(os.path.join(backup_dir, old_backup))
                print(f"🗑️ Ancienne sauvegarde supprimée: {old_backup}")
                
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")

if __name__ == "__main__":
    backup_construction_database()
