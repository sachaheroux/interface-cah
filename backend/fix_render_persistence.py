#!/usr/bin/env python3
"""
Script pour corriger la persistance des données sur Render
"""

import os

def fix_render_configuration():
    """Corriger la configuration Render pour la persistance"""
    
    print("🔧 CORRECTION DE LA CONFIGURATION RENDER")
    print("=" * 60)
    
    # Nouveau render.yaml avec disque persistant
    render_config = """services:
  - type: web
    name: interface-cah-backend
    env: python
    plan: starter  # Changé de 'free' à 'starter' pour le disque persistant
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.10
      - key: DATA_DIR
        value: /opt/render/project/src/data
      - key: ENVIRONMENT
        value: production
    # Configuration du disque persistant
    disk:
      name: cah-persistent-disk
      mountPath: /opt/render/project/src/data
      sizeGB: 1  # 1GB devrait être suffisant pour les bases de données
"""
    
    # Écrire le nouveau fichier
    with open('render.yaml', 'w', encoding='utf-8') as f:
        f.write(render_config)
    
    print("✅ render.yaml mis à jour avec:")
    print("   - Plan: starter (au lieu de free)")
    print("   - Disque persistant: cah-persistent-disk")
    print("   - Montage: /opt/render/project/src/data")
    print("   - Taille: 1GB")

def create_backup_script():
    """Créer un script de sauvegarde automatique"""
    
    print("\n💾 CRÉATION DU SCRIPT DE SAUVEGARDE")
    print("-" * 40)
    
    backup_script = '''#!/usr/bin/env python3
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
'''
    
    with open('backup_construction.py', 'w', encoding='utf-8') as f:
        f.write(backup_script)
    
    print("✅ Script de sauvegarde créé: backup_construction.py")

def create_restore_script():
    """Créer un script de restauration"""
    
    print("\n🔄 CRÉATION DU SCRIPT DE RESTAURATION")
    print("-" * 40)
    
    restore_script = '''#!/usr/bin/env python3
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
'''
    
    with open('restore_construction.py', 'w', encoding='utf-8') as f:
        f.write(restore_script)
    
    print("✅ Script de restauration créé: restore_construction.py")

def create_startup_check():
    """Créer un script de vérification au démarrage"""
    
    print("\n🚀 CRÉATION DU SCRIPT DE VÉRIFICATION AU DÉMARRAGE")
    print("-" * 40)
    
    startup_script = '''#!/usr/bin/env python3
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
'''
    
    with open('startup_check.py', 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    print("✅ Script de vérification créé: startup_check.py")

def main():
    """Fonction principale"""
    
    fix_render_configuration()
    create_backup_script()
    create_restore_script()
    create_startup_check()
    
    print("\n" + "=" * 60)
    print("🎯 CORRECTION TERMINÉE")
    print("=" * 60)
    print("📋 Actions à effectuer:")
    print("1. Commiter et déployer le nouveau render.yaml")
    print("2. Vérifier que le disque persistant est créé sur Render")
    print("3. Tester la persistance après redéploiement")
    print("4. Configurer des sauvegardes automatiques si nécessaire")

if __name__ == "__main__":
    main()
