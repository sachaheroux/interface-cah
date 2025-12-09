#!/usr/bin/env python3
"""
Service de base de données pour les projets de construction
Utilise EXACTEMENT le même fichier SQLite que la partie locative
"""

from database import db_manager, engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

# Utiliser EXACTEMENT le même moteur et fichier que database.py
construction_engine = engine  # Même moteur que la partie locative
CONSTRUCTION_DATABASE_PATH = db_manager.db_path  # Même fichier SQLite

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
    Utilise le même fichier SQLite que la partie locative
    """
    try:
        from sqlalchemy import text
        
        print("🏗️ Initialisation de la base de données construction...")
        print(f"📁 Utilise le même fichier que la partie locative: {CONSTRUCTION_DATABASE_PATH}")
        
        # Créer toutes les tables dans le même fichier SQLite
        ConstructionBase.metadata.create_all(bind=construction_engine)
        
        # Ajouter les colonnes manquantes aux tables si elles existent déjà
        with get_construction_db_context() as db:
            try:
                # Vérifier et ajouter colonnes pour projets
                result = db.execute(text("PRAGMA table_info(projets)"))
                existing_columns = [col[1] for col in result.fetchall()]
                
                columns_to_add_projets = [
                    ("adresse", "VARCHAR(255)"),
                    ("ville", "VARCHAR(100)"),
                    ("province", "VARCHAR(50)"),
                    ("code_postal", "VARCHAR(10)"),
                    ("budget_total", "FLOAT DEFAULT 0")
                ]
                
                for col_name, col_type in columns_to_add_projets:
                    if col_name not in existing_columns:
                        try:
                            db.execute(text(f"ALTER TABLE projets ADD COLUMN {col_name} {col_type}"))
                            print(f"✅ Colonne '{col_name}' ajoutée à la table projets")
                        except Exception as e:
                            print(f"⚠️ Erreur lors de l'ajout de '{col_name}': {e}")
                
                # Vérifier et ajouter colonnes pour factures_st
                result = db.execute(text("PRAGMA table_info(factures_st)"))
                existing_columns_factures = [col[1] for col in result.fetchall()]
                
                columns_to_add_factures = [
                    ("reference", "VARCHAR(100)"),
                    ("date_de_paiement", "DATETIME"),
                    ("pdf_facture", "VARCHAR(500)")
                ]
                
                for col_name, col_type in columns_to_add_factures:
                    if col_name not in existing_columns_factures:
                        try:
                            db.execute(text(f"ALTER TABLE factures_st ADD COLUMN {col_name} {col_type}"))
                            print(f"✅ Colonne '{col_name}' ajoutée à la table factures_st")
                        except Exception as e:
                            print(f"⚠️ Erreur lors de l'ajout de '{col_name}': {e}")
                
                db.commit()
            except Exception as e:
                print(f"⚠️ Erreur lors de la vérification/ajout des colonnes: {e}")
                db.rollback()
        
        print("✅ Base de données construction initialisée avec succès")
        print("📁 Tables construction ajoutées au fichier SQLite existant")
        
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
