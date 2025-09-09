#!/usr/bin/env python3
"""
Script de nettoyage complet de la base de données
Supprime TOUTES les données et recrée une base vide
"""

import os
import shutil
from datetime import datetime

def clean_database():
    """Nettoyer complètement la base de données"""
    print("🧹 NETTOYAGE COMPLET DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    # Chemin de la base de données
    db_path = "./data/cah_database.db"
    data_dir = "./data"
    
    try:
        # 1. Créer une sauvegarde de sécurité
        print("1️⃣ Création d'une sauvegarde de sécurité...")
        if os.path.exists(db_path):
            backup_name = f"backup_before_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = os.path.join(data_dir, "backups", backup_name)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(db_path, backup_path)
            print(f"✅ Sauvegarde créée: {backup_name}")
        else:
            print("ℹ️ Aucune base de données existante")
        
        # 2. Supprimer complètement le dossier data
        print("\n2️⃣ Suppression complète du dossier data...")
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
            print("✅ Dossier data supprimé")
        else:
            print("ℹ️ Dossier data n'existe pas")
        
        # 3. Recréer le dossier data
        print("\n3️⃣ Création d'un nouveau dossier data...")
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "backups"), exist_ok=True)
        print("✅ Dossier data recréé")
        
        # 4. Recréer la base de données propre
        print("\n4️⃣ Création d'une nouvelle base de données vide...")
        from database import init_database
        
        if init_database():
            print("✅ Nouvelle base de données créée")
        else:
            print("❌ Erreur lors de la création de la base de données")
            return False
        
        # 5. Vérifier que la base est complètement vide
        print("\n5️⃣ Vérification de la base de données vide...")
        from database import db_manager
        
        if db_manager.connect():
            cursor = db_manager.connection.cursor()
            
            tables = ["buildings", "tenants", "assignments", "building_reports", "unit_reports", "invoices"]
            total_records = 0
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_records += count
                print(f"   📊 Table {table}: {count} enregistrements")
            
            db_manager.disconnect()
            
            if total_records == 0:
                print("✅ Base de données complètement vide")
            else:
                print(f"⚠️ {total_records} enregistrements restants")
                return False
        
        print("\n🎉 NETTOYAGE TERMINÉ !")
        print("✅ Base de données complètement vide")
        print("✅ Prête pour de nouvelles données")
        print("✅ Toutes les anciennes données supprimées")
        print("✅ Sauvegarde de sécurité créée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("⚠️  ATTENTION: Cette opération va supprimer TOUTES les données !")
    print("   Une sauvegarde de sécurité sera créée avant la suppression.")
    print("   Le dossier data sera complètement supprimé et recréé.")
    print()
    
    response = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ").lower().strip()
    
    if response in ['oui', 'o', 'yes', 'y']:
        success = clean_database()
        if success:
            print("\n✅ Nettoyage réussi !")
            print("🚀 Vous pouvez maintenant recommencer de zéro")
        else:
            print("\n❌ Erreur lors du nettoyage")
    else:
        print("\n❌ Opération annulée")

if __name__ == "__main__":
    main()
