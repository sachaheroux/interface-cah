#!/usr/bin/env python3
"""
Service de base de données d'authentification (SQLite)
Base de données séparée pour l'authentification multi-tenant
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models_auth import Base, Compagnie, Utilisateur, DemandeAcces

# Chemin de la base de données d'authentification
DATA_DIR = os.environ.get("DATA_DIR", "./data")
os.makedirs(DATA_DIR, exist_ok=True)
AUTH_DB_PATH = os.path.join(DATA_DIR, "auth.db")

print(f"📁 Base de données d'authentification : {AUTH_DB_PATH}")

# Créer le moteur SQLAlchemy pour SQLite
engine = create_engine(
    f"sqlite:///{AUTH_DB_PATH}",
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "check_same_thread": False,
        "timeout": 30.0
    }
)

# Créer la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_auth_database():
    """Initialiser la base de données d'authentification"""
    try:
        # Créer toutes les tables si elles n'existent pas
        Base.metadata.create_all(bind=engine)
        print("✅ Tables d'authentification créées/vérifiées")
        
        # Créer la compagnie par défaut si elle n'existe pas
        create_default_company()
        
        return True
    except Exception as e:
        print(f"❌ Erreur initialisation DB auth: {e}")
        return False

def create_default_company():
    """Créer la compagnie CAH Immobilier par défaut si elle n'existe pas"""
    db = SessionLocal()
    try:
        # Vérifier si la compagnie existe déjà
        existing = db.query(Compagnie).filter_by(nom_compagnie="CAH Immobilier").first()
        
        company_id = None
        if not existing:
            # Générer un code d'accès unique
            import auth_service
            code_acces = auth_service.generate_company_access_code()
            
            # Créer la compagnie par défaut
            default_company = Compagnie(
                nom_compagnie="CAH Immobilier",
                email_compagnie="sacha.heroux87@gmail.com",
                schema_name="cah_database",  # Pointe vers cah_database.db
                code_acces=code_acces,
                date_creation=datetime.utcnow()
            )
            db.add(default_company)
            db.commit()
            db.refresh(default_company)
            company_id = default_company.id_compagnie
            print(f"✅ Compagnie 'CAH Immobilier' créée (ID: {company_id}, Code: {code_acces})")
        else:
            company_id = existing.id_compagnie
            print(f"ℹ️ Compagnie 'CAH Immobilier' existe déjà (ID: {company_id})")
        
        # Créer l'utilisateur admin Sacha si il n'existe pas
        if company_id:
            create_default_admin_user(db, company_id)
            
    except Exception as e:
        print(f"❌ Erreur création compagnie par défaut: {e}")
        db.rollback()
    finally:
        db.close()

def create_default_admin_user(db: SessionLocal, company_id: int):
    """Créer l'utilisateur admin Sacha si il n'existe pas"""
    try:
        # Vérifier si Sacha existe déjà
        existing_user = db.query(Utilisateur).filter_by(email="sacha.heroux87@gmail.com").first()
        
        if not existing_user:
            # Importer auth_service pour hasher le mot de passe
            import auth_service
            
            # Créer l'utilisateur admin
            admin_user = Utilisateur(
                id_compagnie=company_id,
                email="sacha.heroux87@gmail.com",
                mot_de_passe_hash=auth_service.hash_password("Champion2024!"),
                nom="Heroux",
                prenom="Sacha",
                role="admin",
                est_admin_principal=True,
                statut="actif",
                email_verifie=True,
                date_creation=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
            print(f"✅ Utilisateur admin 'Sacha Heroux' créé pour CAH Immobilier")
        else:
            print(f"ℹ️ Utilisateur 'sacha.heroux87@gmail.com' existe déjà")
            
    except Exception as e:
        print(f"❌ Erreur création utilisateur admin: {e}")
        db.rollback()

def get_auth_db():
    """Obtenir une session de base de données d'authentification"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_company_database_path(company_id: int) -> str:
    """
    Retourner le chemin de la base de données d'une compagnie
    
    Pour l'instant : toutes les compagnies pointent vers cah_database.db
    Plus tard : chaque compagnie aura sa propre DB
    """
    db = SessionLocal()
    try:
        company = db.query(Compagnie).filter_by(id_compagnie=company_id).first()
        if company:
            # Pour l'instant, utiliser le schema_name comme nom de fichier DB
            db_name = f"{company.schema_name}.db"
            db_path = os.path.join(DATA_DIR, db_name)
            return db_path
        return os.path.join(DATA_DIR, "cah_database.db")  # Fallback
    finally:
        db.close()

# Importer datetime
from datetime import datetime

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔧 INITIALISATION BASE DE DONNÉES D'AUTHENTIFICATION")
    print("="*60)
    init_auth_database()
    print("="*60 + "\n")

