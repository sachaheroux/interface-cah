#!/usr/bin/env python3
"""
Service de base de données pour les projets de construction
Base de données séparée : construction_projects.db
Utilise la même logique de persistance que la base locative
"""

import os
import sqlite3
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

# Configuration du chemin de la base de données construction
# Suivre la même logique que database.py
RENDER_DATABASE_URL = os.environ.get("DATABASE_URL")

# Initialiser CONSTRUCTION_DATABASE_PATH par défaut
CONSTRUCTION_DATABASE_PATH = None

if RENDER_DATABASE_URL:
    # Sur Render avec base de données PostgreSQL
    print(f"🗄️ Base de données Render PostgreSQL détectée pour construction")
    # Pour l'instant, on garde SQLite même sur Render pour la construction
    # TODO: Migrer vers PostgreSQL si nécessaire
    DATA_DIR = os.environ.get("DATA_DIR", "/opt/render/project/src/data")
else:
    # Configuration SQLite locale
    if os.environ.get("ENVIRONMENT") == "development" or os.name == 'nt':
        # En local (Windows) ou développement
        DATA_DIR = os.environ.get("DATA_DIR", "./data")
    else:
        # Sur Render ou production Linux
        DATA_DIR = os.environ.get("DATA_DIR", "/opt/render/project/src/data")

# Créer le répertoire s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# Chemin de la base de données construction SQLite
CONSTRUCTION_DATABASE_PATH = os.path.join(DATA_DIR, "construction_projects.db")
print(f"🗄️ Base de données construction SQLite : {CONSTRUCTION_DATABASE_PATH}")

# Créer le moteur SQLAlchemy
CONSTRUCTION_DATABASE_URL = f"sqlite:///{CONSTRUCTION_DATABASE_PATH}"

construction_engine = create_engine(
    CONSTRUCTION_DATABASE_URL,
    echo=False,  # Mettre à True pour voir les requêtes SQL
    pool_pre_ping=True,
    connect_args={
        "check_same_thread": False,
        "timeout": 30.0
    }
)

# Session factory
ConstructionSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=construction_engine)

# Base pour les modèles
ConstructionBase = declarative_base()

class ConstructionDatabaseManager:
    """Gestionnaire de base de données construction SQLite"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or CONSTRUCTION_DATABASE_PATH
        self.connection = None
        self.engine = construction_engine
        self.SessionLocal = ConstructionSessionLocal
    
    def connect(self):
        """Établir une connexion à la base de données construction"""
        if not self.db_path:
            print("⚠️ Aucun chemin de base de données construction défini")
            return False
            
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
            
            print(f"✅ Connexion à la base de données construction établie : {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion à la base de données construction : {e}")
            return False
    
    def disconnect(self):
        """Fermer la connexion à la base de données construction"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("🔌 Connexion à la base de données construction fermée")
    
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
            print(f"❌ Erreur lors de l'exécution de la requête construction : {e}")
            self.connection.rollback()
            return None
    
    def backup_database(self, backup_path: Optional[str] = None):
        """Créer une sauvegarde de la base de données construction"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(DATA_DIR, "backups", f"construction_backup_{timestamp}.db")
        
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
            
            print(f"✅ Sauvegarde construction créée : {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde construction : {e}")
            return None

# Instance globale du gestionnaire de base de données construction
construction_db_manager = ConstructionDatabaseManager()

def get_construction_db() -> Session:
    """
    Dependency pour obtenir une session de base de données construction
    """
    db = ConstructionSessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_construction_db_context():
    """
    Context manager pour les opérations de base de données construction
    """
    db = ConstructionSessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def init_construction_database():
    """
    Initialiser la base de données construction avec toutes les tables
    """
    try:
        print("🏗️ Initialisation de la base de données construction...")
        
        # Créer toutes les tables
        ConstructionBase.metadata.create_all(bind=construction_engine)
        
        print("✅ Base de données construction initialisée avec succès")
        print(f"📁 Fichier : {CONSTRUCTION_DATABASE_PATH}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base construction : {e}")
        return False

def check_construction_database():
    """
    Vérifier l'état de la base de données construction
    """
    try:
        with get_construction_db_context() as db:
            # Vérifier que la base existe et est accessible
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"📊 Tables dans la base construction : {len(tables)}")
            for table in tables:
                print(f"  - {table}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la base construction : {e}")
        return False

if __name__ == "__main__":
    # Test de la base de données
    print("🧪 Test de la base de données construction...")
    
    if init_construction_database():
        check_construction_database()
    else:
        print("❌ Échec de l'initialisation")
