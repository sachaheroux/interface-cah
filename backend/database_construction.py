#!/usr/bin/env python3
"""
Service de base de données pour les projets de construction
Base de données séparée : construction_projects.db
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

# Configuration de la base de données construction
CONSTRUCTION_DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'construction_projects.db')
CONSTRUCTION_DATABASE_URL = f"sqlite:///{CONSTRUCTION_DB_PATH}"

# Créer le répertoire data s'il n'existe pas
os.makedirs(os.path.dirname(CONSTRUCTION_DB_PATH), exist_ok=True)

# Moteur de base de données
construction_engine = create_engine(
    CONSTRUCTION_DATABASE_URL,
    echo=False,  # Mettre à True pour voir les requêtes SQL
    pool_pre_ping=True
)

# Session factory
ConstructionSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=construction_engine)

# Base pour les modèles
ConstructionBase = declarative_base()

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
        print(f"📁 Fichier : {CONSTRUCTION_DB_PATH}")
        
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
