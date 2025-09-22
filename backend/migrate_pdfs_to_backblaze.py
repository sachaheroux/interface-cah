#!/usr/bin/env python3
"""
Script de migration des PDFs de Render vers Backblaze B2
"""

import os
import sys
import shutil
from pathlib import Path
from storage_service import get_storage_service
import sqlite3
from datetime import datetime

# Configuration
RENDER_DATA_DIR = "/opt/render/project/src/data"
LOCAL_DATA_DIR = "./data"
BACKUP_DIR = "./backup_before_migration"

def backup_existing_data():
    """Créer une sauvegarde complète avant migration"""
    print("💾 Création de la sauvegarde...")
    
    # Créer le dossier de backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Backup de la base de données
    db_path = os.path.join(LOCAL_DATA_DIR, "cah_database.db")
    if os.path.exists(db_path):
        backup_db_path = os.path.join(BACKUP_DIR, f"cah_database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        shutil.copy2(db_path, backup_db_path)
        print(f"✅ Base de données sauvegardée: {backup_db_path}")
    
    # Backup des PDFs
    documents_dir = os.path.join(LOCAL_DATA_DIR, "documents")
    if os.path.exists(documents_dir):
        backup_docs_dir = os.path.join(BACKUP_DIR, f"documents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copytree(documents_dir, backup_docs_dir)
        print(f"✅ PDFs sauvegardés: {backup_docs_dir}")
    
    print("✅ Sauvegarde terminée")

def get_existing_pdfs():
    """Récupérer la liste des PDFs existants"""
    print("🔍 Recherche des PDFs existants...")
    
    documents_dir = os.path.join(LOCAL_DATA_DIR, "documents")
    pdfs = []
    
    if os.path.exists(documents_dir):
        for filename in os.listdir(documents_dir):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(documents_dir, filename)
                pdfs.append({
                    "filename": filename,
                    "file_path": file_path,
                    "size": os.path.getsize(file_path)
                })
    
    print(f"📁 {len(pdfs)} PDFs trouvés")
    return pdfs

def migrate_pdf_to_backblaze(pdf_info, storage_service):
    """Migrer un PDF vers Backblaze B2"""
    try:
        # Lire le fichier
        with open(pdf_info["file_path"], "rb") as f:
            file_content = f.read()
        
        # Upload vers Backblaze B2
        result = storage_service.upload_pdf(
            file_content=file_content,
            original_filename=pdf_info["filename"],
            folder="documents"
        )
        
        if result["success"]:
            print(f"✅ Migré: {pdf_info['filename']} → {result['s3_key']}")
            return result
        else:
            print(f"❌ Échec: {pdf_info['filename']} - {result['error']}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration de {pdf_info['filename']}: {e}")
        return None

def update_database_references(migration_results):
    """Mettre à jour les références dans la base de données"""
    print("🔄 Mise à jour de la base de données...")
    
    db_path = os.path.join(LOCAL_DATA_DIR, "cah_database.db")
    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Créer un mapping des anciens noms vers les nouveaux
        filename_mapping = {}
        for result in migration_results:
            if result:
                filename_mapping[result["original_filename"]] = result["s3_key"]
        
        # Mettre à jour la table bails
        cursor.execute("SELECT id_bail, pdf_bail FROM bails WHERE pdf_bail IS NOT NULL AND pdf_bail != ''")
        bails = cursor.fetchall()
        
        for bail_id, old_filename in bails:
            if old_filename in filename_mapping:
                new_s3_key = filename_mapping[old_filename]
                cursor.execute(
                    "UPDATE bails SET pdf_bail = ? WHERE id_bail = ?",
                    (new_s3_key, bail_id)
                )
                print(f"✅ Bail {bail_id}: {old_filename} → {new_s3_key}")
        
        # Mettre à jour la table transactions
        cursor.execute("SELECT id_transaction, pdf_transaction FROM transactions WHERE pdf_transaction IS NOT NULL AND pdf_transaction != ''")
        transactions = cursor.fetchall()
        
        for transaction_id, old_filename in transactions:
            if old_filename in filename_mapping:
                new_s3_key = filename_mapping[old_filename]
                cursor.execute(
                    "UPDATE transactions SET pdf_transaction = ? WHERE id_transaction = ?",
                    (new_s3_key, transaction_id)
                )
                print(f"✅ Transaction {transaction_id}: {old_filename} → {new_s3_key}")
        
        conn.commit()
        conn.close()
        
        print("✅ Base de données mise à jour")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour de la base de données: {e}")
        return False

def cleanup_old_files(pdf_infos):
    """Nettoyer les anciens fichiers (optionnel)"""
    print("🧹 Nettoyage des anciens fichiers...")
    
    response = input("Voulez-vous supprimer les anciens fichiers PDF ? (y/N): ")
    if response.lower() != 'y':
        print("⏭️ Nettoyage ignoré")
        return
    
    for pdf_info in pdf_infos:
        try:
            os.remove(pdf_info["file_path"])
            print(f"🗑️ Supprimé: {pdf_info['filename']}")
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de {pdf_info['filename']}: {e}")

def main():
    """Fonction principale de migration"""
    print("🚀 Migration des PDFs vers Backblaze B2")
    print("=" * 50)
    
    # Vérifier les variables d'environnement
    if not os.getenv('B2_APPLICATION_KEY_ID') or not os.getenv('B2_APPLICATION_KEY'):
        print("❌ Variables d'environnement Backblaze B2 manquantes")
        print("📝 Configurez d'abord Backblaze B2 avec setup_backblaze_b2.py")
        return False
    
    try:
        # 1. Sauvegarde
        backup_existing_data()
        
        # 2. Récupérer les PDFs existants
        pdfs = get_existing_pdfs()
        if not pdfs:
            print("ℹ️ Aucun PDF à migrer")
            return True
        
        # 3. Initialiser le service de stockage
        storage_service = get_storage_service()
        
        # 4. Migrer chaque PDF
        migration_results = []
        for i, pdf_info in enumerate(pdfs, 1):
            print(f"📤 Migration {i}/{len(pdfs)}: {pdf_info['filename']}")
            result = migrate_pdf_to_backblaze(pdf_info, storage_service)
            migration_results.append(result)
        
        # 5. Mettre à jour la base de données
        update_database_references(migration_results)
        
        # 6. Nettoyage (optionnel)
        cleanup_old_files(pdfs)
        
        print("🎉 Migration terminée avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
