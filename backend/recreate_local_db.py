#!/usr/bin/env python3
"""
Script pour forcer la recréation de la base locale avec la nouvelle structure
"""

import os
import sqlite3
from datetime import datetime

# Configuration
LOCAL_DB_PATH = "data/construction_projects_local.db"

def backup_old_database():
    """Sauvegarder l'ancienne base de données"""
    if os.path.exists(LOCAL_DB_PATH):
        backup_path = f"{LOCAL_DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"📁 Sauvegarde de l'ancienne base: {backup_path}")
        
        import shutil
        shutil.copy2(LOCAL_DB_PATH, backup_path)
        print(f"✅ Sauvegarde créée: {backup_path}")
        return backup_path
    return None

def delete_old_database():
    """Supprimer l'ancienne base de données"""
    if os.path.exists(LOCAL_DB_PATH):
        print(f"🗑️ Suppression de l'ancienne base: {LOCAL_DB_PATH}")
        os.remove(LOCAL_DB_PATH)
        print("✅ Ancienne base supprimée")
        return True
    else:
        print("⚠️ Aucune ancienne base trouvée")
        return False

def recreate_database():
    """Recréer la base de données avec la nouvelle structure"""
    print("🗄️ Recréation de la base de données...")
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    # Créer la table employes avec la nouvelle structure
    create_employes_sql = '''
        CREATE TABLE employes (
            id_employe INTEGER PRIMARY KEY,
            prenom TEXT NOT NULL,
            nom TEXT NOT NULL,
            poste TEXT,
            numero TEXT,
            adresse_courriel TEXT,
            taux_horaire REAL,
            date_creation TEXT,
            date_modification TEXT
        )
    '''
    
    cursor.execute(create_employes_sql)
    print("✅ Table 'employes' créée avec la colonne taux_horaire")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Base de données recréée: {LOCAL_DB_PATH}")

def verify_structure():
    """Vérifier la structure de la nouvelle base"""
    print("\n🔍 Vérification de la structure...")
    
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    # Vérifier la structure de la table employes
    cursor.execute("PRAGMA table_info(employes)")
    columns = cursor.fetchall()
    
    print("📋 Structure de la table employes:")
    for col in columns:
        print(f"  - {col[1]}: {col[2]} (not_null: {col[3]})")
    
    # Vérifier si taux_horaire existe
    column_names = [col[1] for col in columns]
    if 'taux_horaire' in column_names:
        print("✅ Colonne 'taux_horaire' présente")
    else:
        print("❌ Colonne 'taux_horaire' manquante")
    
    conn.close()

if __name__ == "__main__":
    print("🚀 Recréation de la base locale - Interface CAH")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Sauvegarder l'ancienne base
    backup_path = backup_old_database()
    
    # Supprimer l'ancienne base
    delete_old_database()
    
    # Recréer la base
    recreate_database()
    
    # Vérifier la structure
    verify_structure()
    
    print("\n" + "=" * 50)
    print("🏁 Recréation terminée")
    print()
    print("💡 Prochaines étapes:")
    print("   1. Exécuter le script de téléchargement")
    print("   2. Vérifier que la colonne taux_horaire apparaît")
    print("   3. Créer les nouveaux employés sur le site")

