#!/usr/bin/env python3
"""
Script simple pour télécharger la base de données Render via SSH
Utilise scp pour copier directement le fichier de base de données
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
RENDER_HOST = "interface-cah-backend.onrender.com"  # À ajuster selon votre configuration Render
RENDER_DB_PATH = "/opt/render/project/src/data/cah_database.db"  # Chemin sur Render
LOCAL_DATA_DIR = Path("data")
LOCAL_DB_PATH = LOCAL_DATA_DIR / f"cah_database_render_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def create_data_directory():
    """Créer le répertoire data s'il n'existe pas"""
    LOCAL_DATA_DIR.mkdir(exist_ok=True)
    print(f"📁 Répertoire de données: {LOCAL_DATA_DIR.absolute()}")

def download_via_scp():
    """Télécharger la base de données via SCP"""
    try:
        print("🔄 Téléchargement via SCP...")
        
        # Commande SCP pour télécharger le fichier
        cmd = [
            "scp",
            f"render@{RENDER_HOST}:{RENDER_DB_PATH}",
            str(LOCAL_DB_PATH)
        ]
        
        print(f"📤 Commande: {' '.join(cmd)}")
        
        # Exécuter la commande
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Base de données téléchargée: {LOCAL_DB_PATH}")
            return True
        else:
            print(f"❌ Erreur SCP: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ SCP non trouvé. Installez OpenSSH ou utilisez le script API")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        return False

def show_database_info():
    """Afficher des informations sur la base de données téléchargée"""
    try:
        import sqlite3
        
        if not LOCAL_DB_PATH.exists():
            print("❌ Fichier de base de données non trouvé")
            return
        
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        print("\n📊 Informations sur la base de données téléchargée:")
        print("=" * 60)
        
        # Lister les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📋 Tables trouvées ({len(tables)}):")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} enregistrements")
        
        # Afficher quelques exemples d'immeubles
        print("\n🏢 Exemples d'immeubles:")
        cursor.execute("SELECT id_immeuble, nom_immeuble, adresse, ville FROM immeubles LIMIT 5")
        buildings = cursor.fetchall()
        
        for building in buildings:
            print(f"  - ID {building[0]}: {building[1]} - {building[2]}, {building[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage des informations: {e}")

def main():
    """Fonction principale"""
    print("🚀 Téléchargement de la base de données Render (SCP)")
    print("=" * 60)
    
    # Créer le répertoire de données
    create_data_directory()
    
    # Télécharger via SCP
    if download_via_scp():
        print("\n✅ Téléchargement terminé avec succès!")
        show_database_info()
        
        print(f"\n📁 Base de données locale: {LOCAL_DB_PATH.absolute()}")
        print("💡 Vous pouvez maintenant ouvrir ce fichier avec DB Browser for SQLite")
    else:
        print("\n❌ Échec du téléchargement")
        print("💡 Essayez le script download_render_db.py qui utilise l'API")

if __name__ == "__main__":
    main()
