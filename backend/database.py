import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./buildings.db")

# Pour PostgreSQL sur Render, l'URL est fournie automatiquement
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle de base de données pour les immeubles
class BuildingDB(Base):
    __tablename__ = "buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # Adresse (stockée en JSON)
    address = Column(JSON, nullable=False)
    
    # Informations de base
    type = Column(String, nullable=False)
    units = Column(Integer, nullable=False)
    floors = Column(Integer, nullable=False)
    year_built = Column(Integer, nullable=False)
    total_area = Column(Integer, nullable=True)
    
    # Caractéristiques (stockées en JSON)
    characteristics = Column(JSON, nullable=True)
    
    # Finances (stockées en JSON)
    financials = Column(JSON, nullable=True)
    
    # Contacts (stockés en JSON)
    contacts = Column(JSON, nullable=True)
    
    # Notes
    notes = Column(Text, default="")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Créer les tables
def create_tables():
    Base.metadata.create_all(bind=engine)

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