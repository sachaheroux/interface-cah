#!/usr/bin/env python3
"""
Script de restauration des données construction
"""

import os
import shutil
import glob
from datetime import datetime

def restore_construction_database():
    """Restaurer la base de données construction"""
    
    # Chemins
    data_dir = os.getenv('DATA_DIR', '/opt/render/project/src/data')
    db_path = os.path.join(data_dir, 'construction_projects.db')
    backup_dir = os.path.join(data_dir, 'backups')
    
    # Trouver la sauvegarde la plus récente
    backup_pattern = os.path.join(backup_dir, 'construction_backup_*.db')
    backups = glob.glob(backup_pattern)
    
    if not backups:
        print("❌ Aucune sauvegarde trouvée")
        return False
    
    latest_backup = max(backups, key=os.path.getctime)
    
    try:
        # Restaurer la base de données
        shutil.copy2(latest_backup, db_path)
        print(f"✅ Base restaurée depuis: {latest_backup}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur restauration: {e}")
        return False

if __name__ == "__main__":
    restore_construction_database()
