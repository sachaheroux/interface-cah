#!/usr/bin/env python3
"""
Service de sauvegarde automatique pour Interface CAH
"""

import os
import shutil
import gzip
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import schedule
import time
import threading
from pathlib import Path

from database import db_manager, DATABASE_PATH

class BackupService:
    """Service de sauvegarde automatique de la base de données"""
    
    def __init__(self, backup_dir: str = "./backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.max_backups = 30  # Garder 30 sauvegardes maximum
        self.compression_enabled = True
        self.running = False
        self.backup_thread = None
        
    def create_backup(self, backup_type: str = "manual") -> Optional[str]:
        """
        Créer une sauvegarde de la base de données
        
        Args:
            backup_type: Type de sauvegarde ('manual', 'scheduled', 'before_migration')
        
        Returns:
            Chemin vers le fichier de sauvegarde créé, ou None en cas d'erreur
        """
        try:
            # Vérifier que la base de données existe
            if not os.path.exists(DATABASE_PATH):
                print(f"❌ Base de données non trouvée : {DATABASE_PATH}")
                return None
            
            # Créer le nom du fichier de sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"cah_backup_{backup_type}_{timestamp}.db"
            
            if self.compression_enabled:
                backup_filename += ".gz"
            
            backup_path = self.backup_dir / backup_filename
            
            # Créer la sauvegarde
            if self.compression_enabled:
                # Sauvegarde compressée
                with open(DATABASE_PATH, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Sauvegarde simple
                shutil.copy2(DATABASE_PATH, backup_path)
            
            # Vérifier la sauvegarde
            if self._verify_backup(backup_path):
                print(f"✅ Sauvegarde créée : {backup_path}")
                
                # Nettoyer les anciennes sauvegardes
                self._cleanup_old_backups()
                
                # Créer un fichier de métadonnées
                self._create_backup_metadata(backup_path, backup_type)
                
                return str(backup_path)
            else:
                print(f"❌ Échec de la vérification de la sauvegarde : {backup_path}")
                if backup_path.exists():
                    backup_path.unlink()
                return None
                
        except Exception as e:
            print(f"❌ Erreur lors de la création de la sauvegarde : {e}")
            return None
    
    def _verify_backup(self, backup_path: Path) -> bool:
        """Vérifier l'intégrité d'une sauvegarde"""
        try:
            if not backup_path.exists():
                return False
            
            # Vérifier la taille du fichier
            if backup_path.stat().st_size == 0:
                return False
            
            # Si c'est compressé, essayer de le décompresser
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rb') as f:
                    # Lire quelques octets pour vérifier que c'est valide
                    f.read(1024)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la vérification : {e}")
            return False
    
    def _create_backup_metadata(self, backup_path: Path, backup_type: str):
        """Créer un fichier de métadonnées pour la sauvegarde"""
        try:
            metadata = {
                "backup_type": backup_type,
                "created_at": datetime.now().isoformat(),
                "database_path": str(DATABASE_PATH),
                "backup_size": backup_path.stat().st_size,
                "compressed": self.compression_enabled,
                "version": "1.0.0"
            }
            
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la création des métadonnées : {e}")
    
    def _cleanup_old_backups(self):
        """Nettoyer les anciennes sauvegardes pour ne garder que les plus récentes"""
        try:
            # Lister tous les fichiers de sauvegarde
            backup_files = []
            for file_path in self.backup_dir.glob("cah_backup_*.db*"):
                if file_path.is_file():
                    backup_files.append((file_path.stat().st_mtime, file_path))
            
            # Trier par date de modification (plus récent en premier)
            backup_files.sort(key=lambda x: x[0], reverse=True)
            
            # Supprimer les anciennes sauvegardes
            if len(backup_files) > self.max_backups:
                for _, file_path in backup_files[self.max_backups:]:
                    try:
                        file_path.unlink()
                        # Supprimer aussi le fichier de métadonnées
                        metadata_path = file_path.with_suffix('.json')
                        if metadata_path.exists():
                            metadata_path.unlink()
                        print(f"🗑️ Ancienne sauvegarde supprimée : {file_path.name}")
                    except Exception as e:
                        print(f"⚠️ Erreur lors de la suppression de {file_path.name} : {e}")
                        
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage des sauvegardes : {e}")
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restaurer une sauvegarde
        
        Args:
            backup_path: Chemin vers le fichier de sauvegarde
        
        Returns:
            True si la restauration a réussi, False sinon
        """
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                print(f"❌ Fichier de sauvegarde non trouvé : {backup_path}")
                return False
            
            # Créer une sauvegarde de sécurité avant la restauration
            safety_backup = self.create_backup("before_restore")
            if not safety_backup:
                print("❌ Impossible de créer une sauvegarde de sécurité")
                return False
            
            print(f"🛡️ Sauvegarde de sécurité créée : {safety_backup}")
            
            # Fermer la connexion à la base de données
            if db_manager.connection:
                db_manager.disconnect()
            
            # Restaurer la sauvegarde
            if backup_path.suffix == '.gz':
                # Décompresser et restaurer
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(DATABASE_PATH, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Restaurer directement
                shutil.copy2(backup_path, DATABASE_PATH)
            
            # Vérifier la restauration
            if self._verify_restoration():
                print(f"✅ Sauvegarde restaurée avec succès : {backup_path}")
                return True
            else:
                print(f"❌ Échec de la vérification de la restauration")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la restauration : {e}")
            return False
    
    def _verify_restoration(self) -> bool:
        """Vérifier que la restauration a réussi"""
        try:
            # Tenter de se connecter à la base de données restaurée
            if db_manager.connect():
                cursor = db_manager.connection.cursor()
                
                # Vérifier que les tables existent
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = ['buildings', 'tenants', 'assignments', 'building_reports', 'unit_reports', 'invoices']
                
                if all(table in tables for table in expected_tables):
                    print("✅ Tables de base de données vérifiées")
                    db_manager.disconnect()
                    return True
                else:
                    print(f"❌ Tables manquantes. Trouvées : {tables}")
                    db_manager.disconnect()
                    return False
            else:
                print("❌ Impossible de se connecter à la base de données restaurée")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la vérification de la restauration : {e}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """Lister toutes les sauvegardes disponibles"""
        backups = []
        
        try:
            for file_path in self.backup_dir.glob("cah_backup_*.db*"):
                if file_path.is_file() and not file_path.name.endswith('.json'):
                    # Charger les métadonnées si disponibles
                    metadata_path = file_path.with_suffix('.json')
                    metadata = {}
                    
                    if metadata_path.exists():
                        try:
                            with open(metadata_path, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                        except:
                            pass
                    
                    backup_info = {
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "created_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "backup_type": metadata.get("backup_type", "unknown"),
                        "compressed": file_path.suffix == '.gz'
                    }
                    
                    backups.append(backup_info)
            
            # Trier par date de création (plus récent en premier)
            backups.sort(key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            print(f"❌ Erreur lors du listing des sauvegardes : {e}")
        
        return backups
    
    def start_automatic_backups(self):
        """Démarrer les sauvegardes automatiques"""
        if self.running:
            print("⚠️ Les sauvegardes automatiques sont déjà en cours")
            return
        
        print("🔄 Démarrage des sauvegardes automatiques...")
        
        # Programmer les sauvegardes
        schedule.every().day.at("02:00").do(self._scheduled_backup, "daily")
        schedule.every().sunday.at("03:00").do(self._scheduled_backup, "weekly")
        schedule.every().monday.at("04:00").do(self._scheduled_backup, "monthly")
        
        # Démarrer le thread de sauvegarde
        self.running = True
        self.backup_thread = threading.Thread(target=self._backup_worker, daemon=True)
        self.backup_thread.start()
        
        print("✅ Sauvegardes automatiques démarrées")
        print("   - Quotidienne : 02:00")
        print("   - Hebdomadaire : Dimanche 03:00")
        print("   - Mensuelle : Lundi 04:00")
    
    def stop_automatic_backups(self):
        """Arrêter les sauvegardes automatiques"""
        if not self.running:
            print("⚠️ Les sauvegardes automatiques ne sont pas en cours")
            return
        
        self.running = False
        schedule.clear()
        
        if self.backup_thread and self.backup_thread.is_alive():
            self.backup_thread.join(timeout=5)
        
        print("🛑 Sauvegardes automatiques arrêtées")
    
    def _scheduled_backup(self, backup_type: str):
        """Effectuer une sauvegarde programmée"""
        print(f"🔄 Sauvegarde {backup_type} programmée...")
        backup_path = self.create_backup(backup_type)
        if backup_path:
            print(f"✅ Sauvegarde {backup_type} terminée : {backup_path}")
        else:
            print(f"❌ Échec de la sauvegarde {backup_type}")
    
    def _backup_worker(self):
        """Worker thread pour les sauvegardes automatiques"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Vérifier toutes les minutes
            except Exception as e:
                print(f"❌ Erreur dans le worker de sauvegarde : {e}")
                time.sleep(60)

# Instance globale du service de sauvegarde
backup_service = BackupService()

def get_backup_service():
    """Obtenir l'instance du service de sauvegarde"""
    return backup_service
