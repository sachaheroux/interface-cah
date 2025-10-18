#!/usr/bin/env python3
"""
Service de base de données pour les projets de construction
Utilise EXACTEMENT la même configuration que database.py
"""

from database import db_manager
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

# Utiliser EXACTEMENT la même configuration que database.py
construction_engine = db_manager.engine
CONSTRUCTION_DATABASE_PATH = db_manager.db_path

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
        print(f"📁 Utilise la même base que la partie locative")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base construction : {e}")
        return False

if __name__ == "__main__":
    # Test de la base de données
    print("🧪 Test de la base de données construction...")
    
    if init_construction_database():
        print("✅ Base de données construction prête")
    else:
        print("❌ Échec de l'initialisation")
