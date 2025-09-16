#!/usr/bin/env python3
"""
Configuration de la base de données SQLite pour Interface CAH
"""

import os
import sqlite3
from datetime import datetime
from typing import Optional
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuration du chemin de la base de données
if os.environ.get("ENVIRONMENT") == "development" or os.name == 'nt':
    # En local (Windows) ou développement
    DATA_DIR = os.environ.get("DATA_DIR", "./data")
else:
    # Sur Render ou production Linux
    DATA_DIR = os.environ.get("DATA_DIR", "/opt/render/project/src/data")

# Créer le répertoire s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# Chemin de la base de données SQLite
DATABASE_PATH = os.path.join(DATA_DIR, "cah_database.db")

print(f"🗄️ Base de données SQLite : {DATABASE_PATH}")

# Créer le moteur SQLAlchemy
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    echo=False,  # Mettre à True pour voir les requêtes SQL
    pool_pre_ping=True,
    connect_args={
        "check_same_thread": False,
        "timeout": 30.0
    }
)

# Créer la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseManager:
    """Gestionnaire de base de données SQLite"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.connection = None
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def connect(self):
        """Établir une connexion à la base de données"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,  # Permet l'utilisation multi-thread
                timeout=30.0  # Timeout de 30 secondes
            )
            # Activer les contraintes de clés étrangères
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Optimiser les performances
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.connection.execute("PRAGMA synchronous = NORMAL")
            self.connection.execute("PRAGMA cache_size = 1000")
            self.connection.execute("PRAGMA temp_store = MEMORY")
            
            print(f"✅ Connexion à la base de données établie : {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion à la base de données : {e}")
            return False
    
    def disconnect(self):
        """Fermer la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("🔌 Connexion à la base de données fermée")
    
    
    def get_connection(self):
        """Obtenir la connexion actuelle"""
        if not self.connection:
            self.connect()
        return self.connection
    
    def execute_query(self, query: str, params: tuple = ()):
        """Exécuter une requête SQL"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de la requête : {e}")
            self.connection.rollback()
            return None
    
    def backup_database(self, backup_path: Optional[str] = None):
        """Créer une sauvegarde de la base de données"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(DATA_DIR, "backups", f"cah_backup_{timestamp}.db")
        
        # Créer le répertoire de sauvegarde
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        try:
            # Fermer la connexion actuelle
            if self.connection:
                self.connection.close()
            
            # Copier le fichier de base de données
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            # Rétablir la connexion
            self.connect()
            
            print(f"✅ Sauvegarde créée : {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")
            return None

# Instance globale du gestionnaire de base de données
db_manager = DatabaseManager()

def get_database():
    """Obtenir l'instance de la base de données"""
    return db_manager

def init_database():
    """Initialiser la base de données (créer les tables)"""
    try:
        # Importer les modèles français
        from models_francais import Base
        
        # Créer toutes les tables avec SQLAlchemy
        Base.metadata.create_all(bind=engine)
        print("✅ Tables françaises créées avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables françaises: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Initialisation de la base de données SQLite...")
    if init_database():
        print("✅ Base de données initialisée avec succès !")
    else:
        print("❌ Erreur lors de l'initialisation de la base de données")
