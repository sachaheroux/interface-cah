#!/usr/bin/env python3
"""
Script de réinitialisation complète de la base de données
"""

import os
import shutil
from datetime import datetime

def reset_database():
    """Réinitialiser complètement la base de données"""
    print("🧹 RÉINITIALISATION COMPLÈTE DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    # Chemin de la base de données
    db_path = "./data/cah_database.db"
    data_dir = "./data"
    
    try:
        # 1. Créer une sauvegarde de sécurité
        print("1️⃣ Création d'une sauvegarde de sécurité...")
        if os.path.exists(db_path):
            backup_name = f"backup_before_reset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = os.path.join(data_dir, "backups", backup_name)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(db_path, backup_path)
            print(f"✅ Sauvegarde créée: {backup_name}")
        else:
            print("ℹ️ Aucune base de données existante")
        
        # 2. Supprimer la base de données actuelle
        print("\n2️⃣ Suppression de la base de données actuelle...")
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Base de données supprimée")
        else:
            print("ℹ️ Aucune base de données à supprimer")
        
        # 3. Supprimer les fichiers WAL et SHM
        wal_file = db_path + "-wal"
        shm_file = db_path + "-shm"
        
        for file_path in [wal_file, shm_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ Fichier supprimé: {os.path.basename(file_path)}")
        
        # 4. Supprimer tous les fichiers JSON de données
        print("\n3️⃣ Suppression des fichiers JSON de données...")
        json_files = [
            "buildings_data.json",
            "tenants_data.json", 
            "assignments_data.json",
            "building_reports_data.json",
            "unit_reports_data.json",
            "invoices_data.json"
        ]
        
        for json_file in json_files:
            file_path = os.path.join(data_dir, json_file)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ Supprimé: {json_file}")
            else:
                print(f"ℹ️ N'existe pas: {json_file}")
        
        # 5. Recréer la base de données propre
        print("\n4️⃣ Création d'une nouvelle base de données propre...")
        from database import init_database
        
        if init_database():
            print("✅ Nouvelle base de données créée")
        else:
            print("❌ Erreur lors de la création de la base de données")
            return False
        
        # 6. Vérifier que la base est vide
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
        
        # 7. Nettoyer les sauvegardes anciennes (garder seulement les 5 plus récentes)
        print("\n6️⃣ Nettoyage des anciennes sauvegardes...")
        backups_dir = os.path.join(data_dir, "backups")
        if os.path.exists(backups_dir):
            backup_files = []
            for file in os.listdir(backups_dir):
                if file.endswith('.db'):
                    file_path = os.path.join(backups_dir, file)
                    backup_files.append((os.path.getmtime(file_path), file_path))
            
            # Trier par date de modification (plus récent en premier)
            backup_files.sort(key=lambda x: x[0], reverse=True)
            
            # Supprimer les anciennes sauvegardes (garder les 5 plus récentes)
            for _, file_path in backup_files[5:]:
                os.remove(file_path)
                print(f"🗑️ Ancienne sauvegarde supprimée: {os.path.basename(file_path)}")
            
            print(f"✅ {min(5, len(backup_files))} sauvegardes conservées")
        
        print("\n🎉 RÉINITIALISATION TERMINÉE !")
        print("✅ Base de données complètement vide")
        print("✅ Prête pour de nouvelles données")
        print("✅ Anciennes données supprimées")
        print("✅ Sauvegarde de sécurité créée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("⚠️  ATTENTION: Cette opération va supprimer TOUTES les données !")
    print("   Une sauvegarde de sécurité sera créée avant la suppression.")
    print()
    
    response = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ").lower().strip()
    
    if response in ['oui', 'o', 'yes', 'y']:
        success = reset_database()
        if success:
            print("\n✅ Réinitialisation réussie !")
            print("🚀 Vous pouvez maintenant recommencer de zéro")
        else:
            print("\n❌ Erreur lors de la réinitialisation")
    else:
        print("\n❌ Opération annulée")

if __name__ == "__main__":
    main()
