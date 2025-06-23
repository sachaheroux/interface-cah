import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL sur Render
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)
else:
    # SQLite en local/fallback
    DATABASE_URL = "sqlite:///./buildings.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle de base de données pour les immeubles
class BuildingDB(Base):
    __tablename__ = "buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # Adresse (stockée en JSON pour PostgreSQL, TEXT pour SQLite)
    address = Column(JSON if "postgresql" in str(engine.url) else Text, nullable=False)
    
    # Informations de base
    type = Column(String, nullable=False)
    units = Column(Integer, nullable=False)
    floors = Column(Integer, nullable=False)
    year_built = Column(Integer, nullable=False)
    total_area = Column(Integer, nullable=True)
    
    # Caractéristiques (stockées en JSON pour PostgreSQL, TEXT pour SQLite)
    characteristics = Column(JSON if "postgresql" in str(engine.url) else Text, nullable=True)
    
    # Finances (stockées en JSON pour PostgreSQL, TEXT pour SQLite)
    financials = Column(JSON if "postgresql" in str(engine.url) else Text, nullable=True)
    
    # Contacts (stockés en JSON pour PostgreSQL, TEXT pour SQLite)
    contacts = Column(JSON if "postgresql" in str(engine.url) else Text, nullable=True)
    
    # Notes
    notes = Column(Text, default="")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Créer les tables
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Erreur création tables: {e}")
        return False

# Obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialiser avec des données de base
def init_default_buildings():
    """Ne pas créer d'immeubles de base - base de données vide"""
    # Base de données vide - les utilisateurs créent leurs propres immeubles
    pass

# Utilitaires pour gérer JSON/TEXT selon la base
def serialize_json_field(data):
    """Sérialiser les données JSON pour SQLite"""
    if data is None:
        return None
    if isinstance(data, str):
        return data
    return json.dumps(data)

def deserialize_json_field(data):
    """Désérialiser les données JSON depuis SQLite"""
    if data is None:
        return None
    if isinstance(data, dict):
        return data
    try:
        return json.loads(data)
    except:
        return data 